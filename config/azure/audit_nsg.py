#!/usr/bin/env python3
"""Ocena reguł grup zabezpieczeń sieci (NSG): czy ruch z Internetu i z innych podsieci jest zablokowany tak,
jak zakłada projekt. Reguły są oceniane według priorytetów, a nie tylko wyszukiwane po nazwie portu.

Użycie: audit_nsg.py --web-cidr 10.0.0.0/23 --app-cidr 10.0.2.0/23 --db-cidr 10.0.4.0/24 nsg-web.json nsg-app.json nsg-db.json
Kod wyjścia: liczba nieudanych sprawdzeń (0 = wszystko w porządku).
"""
import argparse
import ipaddress
import json
import sys

INTERNET = {"*", "internet", "any", "0.0.0.0/0"}  # takie źródła obejmują ruch z Internetu
VNET = {"*", "virtualnetwork", "any"}  # takie źródła obejmują ruch z sieci wirtualnej
MANAGEMENT_PORTS = (22, 3389)  # SSH i RDP
DB_PORTS = (3306, 5432)  # MySQL i PostgreSQL


def _as_list(*values):
    result = []
    for value in values:
        if isinstance(value, list):
            result += value
        elif value:
            result.append(value)
    return [str(v) for v in result]


def _port_matches(rule, port):
    for value in _as_list(rule.get("destinationPortRange"), rule.get("destinationPortRanges")):
        if value == "*":
            return True
        if "-" in value:
            low, high = value.split("-", 1)
            if int(low) <= port <= int(high):
                return True
        elif value.isdigit() and int(value) == port:
            return True
    return False


def _protocol_matches(rule):
    return str(rule.get("protocol", "*")).lower() in ("*", "tcp")


def _source_matches(rule, source):
    """source: 'internet' albo adres IP z sieci wirtualnej."""
    for prefix in _as_list(rule.get("sourceAddressPrefix"), rule.get("sourceAddressPrefixes")):
        prefix = prefix.lower()
        if source == "internet":
            if prefix in INTERNET:
                return True
        else:
            if prefix in VNET:
                return True
            try:
                if ipaddress.ip_address(source) in ipaddress.ip_network(prefix, strict=False):
                    return True
            except ValueError:
                pass  # np. nazwa tagu usługi, której tu nie rozpoznajemy
    return False


def verdict(rules, source, port):
    """Zwraca 'Allow' albo 'Deny' dla ruchu przychodzącego TCP: pierwsza pasująca reguła wg priorytetu,
    a gdy żadna nie pasuje, reguły domyślne NSG (z sieci wirtualnej dozwolone, z Internetu zablokowane)."""
    inbound = sorted((r for r in rules if r.get("direction") == "Inbound"), key=lambda r: r["priority"])
    for rule in inbound:
        if _protocol_matches(rule) and _source_matches(rule, source) and _port_matches(rule, port):
            return rule["access"]
    return "Deny" if source == "internet" else "Allow"


def host_in(cidr):
    network = ipaddress.ip_network(cidr)
    return str(network.network_address + 10)


class Audit:
    def __init__(self):
        self.failures = 0

    def check(self, description, ok):
        print(("PASS  " if ok else "FAIL  ") + description)
        if not ok:
            self.failures += 1

    def expect(self, rules, source_label, source, port, expected):
        actual = verdict(rules, source, port)
        self.check(f"{source_label} -> port {port}: {expected}", actual == expected)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--web-cidr", required=True)
    parser.add_argument("--app-cidr", required=True)
    parser.add_argument("--db-cidr", required=True)
    parser.add_argument("web_rules")
    parser.add_argument("app_rules")
    parser.add_argument("db_rules")
    args = parser.parse_args()
    web = json.load(open(args.web_rules, encoding="utf-8"))
    app = json.load(open(args.app_rules, encoding="utf-8"))
    db = json.load(open(args.db_rules, encoding="utf-8"))
    web_ip, app_ip = host_in(args.web_cidr), host_in(args.app_cidr)

    audit = Audit()

    print("-- Warstwa DB (nsg-db): zero dostępu z Internetu, dostęp tylko z podsieci z back-endem")
    for port in DB_PORTS + MANAGEMENT_PORTS:
        audit.expect(db, "Internet (0.0.0.0/0)", "internet", port, "Deny")
    audit.expect(db, f"podsieć z back-endem ({args.web_cidr})", web_ip, 5432, "Allow")
    audit.expect(db, f"inna podsieć ({args.app_cidr})", app_ip, 5432, "Deny")
    audit.expect(db, f"inna podsieć ({args.app_cidr})", app_ip, 22, "Deny")

    print("-- Warstwa Web (nsg-web): z Internetu tylko 80 i 443, porty zarządcze zablokowane")
    for port in (80, 443):
        audit.expect(web, "Internet", "internet", port, "Allow")
    for port in MANAGEMENT_PORTS + DB_PORTS:
        audit.expect(web, "Internet", "internet", port, "Deny")

    print("-- Warstwa App (nsg-app, podsieć zarezerwowana): brak ruchu z Internetu")
    for port in (80, 443, 8000) + MANAGEMENT_PORTS + DB_PORTS:
        audit.expect(app, "Internet", "internet", port, "Deny")

    print("-- Porty zarządcze (SSH 22, RDP 3389) z Internetu we wszystkich grupach NSG")
    for name, rules in (("nsg-web", web), ("nsg-app", app), ("nsg-db", db)):
        for port in MANAGEMENT_PORTS:
            audit.check(f"{name}: Internet -> {port} zablokowany", verdict(rules, "internet", port) == "Deny")

    print(f"Nieudane sprawdzenia reguł sieciowych: {audit.failures}")
    return min(audit.failures, 255)


if __name__ == "__main__":
    sys.exit(main())
