"""Testy logiki oceny reguł NSG na sztucznych danych (nie wymagają dostępu do Azure).
Uruchomienie:  python3 -m unittest test_audit_nsg -v"""
import unittest

from audit_nsg import verdict


def rule(name, priority, access, source, ports, direction="Inbound", protocol="*"):
    sources = source if isinstance(source, list) else [source]
    port_list = ports if isinstance(ports, list) else [ports]
    return {
        "name": name,
        "priority": priority,
        "access": access,
        "direction": direction,
        "protocol": protocol,
        "sourceAddressPrefix": sources[0] if len(sources) == 1 else None,
        "sourceAddressPrefixes": sources if len(sources) > 1 else [],
        "destinationPortRange": port_list[0] if len(port_list) == 1 else None,
        "destinationPortRanges": port_list if len(port_list) > 1 else [],
    }


WEB = "10.0.0.10"  # adres w podsieci z back-endem
APP = "10.0.2.10"  # adres w innej podsieci

DB_OK = [
    rule("allow-postgres-from-web", 100, "Allow", "10.0.0.0/23", "5432", protocol="Tcp"),
    rule("deny-mgmt-ports-internet", 110, "Deny", "Internet", ["22", "3389"]),
    rule("deny-all-inbound", 4000, "Deny", ["VirtualNetwork", "Internet"], "*"),
]


class VerdictTests(unittest.TestCase):
    def test_correct_db_configuration(self):
        self.assertEqual(verdict(DB_OK, WEB, 5432), "Allow")
        self.assertEqual(verdict(DB_OK, "internet", 5432), "Deny")
        self.assertEqual(verdict(DB_OK, "internet", 3306), "Deny")
        self.assertEqual(verdict(DB_OK, APP, 5432), "Deny")  # inna podsieć nie dostaje dostępu

    def test_without_lockdown_other_subnets_reach_the_database(self):
        # przed uruchomieniem 03-lockdown.sh: brak reguły Deny, więc działa domyślna AllowVnetInBound
        before = [r for r in DB_OK if r["name"] != "deny-all-inbound"]
        self.assertEqual(verdict(before, APP, 5432), "Allow")
        self.assertEqual(verdict(before, "internet", 5432), "Deny")  # z Internetu i tak blokuje reguła domyślna

    def test_rule_open_to_the_world_is_detected(self):
        bad = DB_OK + [rule("tymczasowo", 90, "Allow", "*", "5432")]
        self.assertEqual(verdict(bad, "internet", 5432), "Allow")
        bad_cidr = [rule("otwarte", 90, "Allow", "0.0.0.0/0", "5432")]
        self.assertEqual(verdict(bad_cidr, "internet", 5432), "Allow")

    def test_priority_decides_not_order_in_list(self):
        rules = [rule("deny", 200, "Deny", "Internet", "443"), rule("allow", 100, "Allow", "Internet", "443")]
        self.assertEqual(verdict(rules, "internet", 443), "Allow")
        rules = [rule("deny", 50, "Deny", "Internet", "443"), rule("allow", 100, "Allow", "Internet", "443")]
        self.assertEqual(verdict(rules, "internet", 443), "Deny")

    def test_port_ranges_and_wildcards(self):
        self.assertEqual(verdict([rule("zakres", 100, "Allow", "Internet", "20-30")], "internet", 22), "Allow")
        self.assertEqual(verdict([rule("zakres", 100, "Allow", "Internet", "23-30")], "internet", 22), "Deny")
        self.assertEqual(verdict([rule("wszystkie", 100, "Allow", "Internet", "*")], "internet", 3389), "Allow")
        self.assertEqual(verdict([rule("lista", 100, "Allow", "Internet", ["80", "443"])], "internet", 443), "Allow")

    def test_management_ports_open_by_mistake(self):
        rules = [rule("ssh", 100, "Allow", "Internet", "22")]
        self.assertEqual(verdict(rules, "internet", 22), "Allow")
        self.assertEqual(verdict(rules + [rule("deny", 90, "Deny", "Internet", ["22", "3389"])], "internet", 22), "Deny")

    def test_other_directions_and_udp_only_rules_are_ignored(self):
        self.assertEqual(verdict([rule("out", 100, "Allow", "*", "*", direction="Outbound")], "internet", 80), "Deny")
        self.assertEqual(verdict([rule("udp", 100, "Allow", "Internet", "53", protocol="Udp")], "internet", 53), "Deny")


if __name__ == "__main__":
    unittest.main()
