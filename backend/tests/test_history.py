VALID = {
    "name": "iris",
    "description": "Klasyfikacja irysów",
    "framework": "scikit-learn",
    "task": "Klasyfikacja",
    "version": "1.0.0",
    "accuracy": 0.9,
    "size_mb": 1.0,
    "status": "draft",
}


def create(client, **overrides):
    response = client.post("/api/models", json={**VALID, **overrides})
    assert response.status_code == 201, response.text
    return response.json()["id"]


def history(client, model_id):
    response = client.get(f"/api/models/{model_id}/history")
    assert response.status_code == 200, response.text
    return response.json()


def test_creation_is_recorded_with_author_and_values(client):
    model_id = create(client)
    (entry,) = history(client, model_id)
    assert entry["action"] == "created"
    assert entry["model_name"] == "iris"
    assert entry["user_email"] == "admin@example.com"
    assert entry["changes"]["name"] == {"from": None, "to": "iris"}
    assert entry["changes"]["status"] == {"from": None, "to": "draft"}


def test_update_records_only_changed_fields(client):
    model_id = create(client)
    client.put(f"/api/models/{model_id}", json={**VALID, "version": "1.1.0", "status": "published"})
    entries = history(client, model_id)
    assert [e["action"] for e in entries] == ["updated", "created"]  # najnowszy wpis pierwszy
    assert entries[0]["changes"] == {
        "version": {"from": "1.0.0", "to": "1.1.0"},
        "status": {"from": "draft", "to": "published"},
    }


def test_status_transitions_are_tracked(client):
    model_id = create(client)
    for status in ("published", "archived"):
        client.put(f"/api/models/{model_id}", json={**VALID, "status": status})
    transitions = [(e["changes"]["status"]["from"], e["changes"]["status"]["to"]) for e in history(client, model_id)[:2]]
    assert transitions == [("published", "archived"), ("draft", "published")]


def test_update_without_changes_creates_no_entry(client):
    model_id = create(client)
    assert client.put(f"/api/models/{model_id}", json=VALID).status_code == 200
    assert len(history(client, model_id)) == 1


def test_clearing_a_field_is_recorded(client):
    model_id = create(client)
    client.put(f"/api/models/{model_id}", json={**VALID, "accuracy": None})
    assert history(client, model_id)[0]["changes"] == {"accuracy": {"from": 0.9, "to": None}}


def test_history_survives_model_deletion(client):
    model_id = create(client)
    client.put(f"/api/models/{model_id}", json={**VALID, "name": "iris-v2"})
    assert client.delete(f"/api/models/{model_id}").status_code == 204
    assert client.get(f"/api/models/{model_id}").status_code == 404
    entries = history(client, model_id)
    assert [e["action"] for e in entries] == ["deleted", "updated", "created"]
    assert entries[0]["model_name"] == "iris-v2"
    assert entries[0]["changes"] is None


def test_history_of_unknown_model_returns_404(client):
    response = client.get("/api/models/9999/history")
    assert response.status_code == 404
    assert response.json() == {"detail": "Model nie istnieje"}


def test_failed_operations_leave_no_history(client):
    assert client.put("/api/models/9999", json=VALID).status_code == 404
    assert client.delete("/api/models/9999").status_code == 404
    assert client.post("/api/models", json={**VALID, "version": "zła"}).status_code == 400
    assert client.get("/api/history").json()["total"] == 0


def test_regular_user_can_read_model_history_but_not_global_log(client, user_client):
    model_id = create(client)
    assert user_client.get(f"/api/models/{model_id}/history").status_code == 200
    response = user_client.get("/api/history")
    assert response.status_code == 403


def test_anonymous_cannot_read_history(anon_client):
    assert anon_client.get("/api/models/1/history").status_code == 401
    assert anon_client.get("/api/history").status_code == 401


def test_global_log_lists_all_models_newest_first_with_filters(client):
    first = create(client, name="pierwszy")
    second = create(client, name="drugi")
    client.put(f"/api/models/{first}", json={**VALID, "name": "pierwszy", "status": "published"})
    client.delete(f"/api/models/{second}")

    body = client.get("/api/history").json()
    assert body["total"] == 4
    assert [e["action"] for e in body["items"]] == ["deleted", "updated", "created", "created"]

    deleted = client.get("/api/history?action=deleted").json()
    assert deleted["total"] == 1 and deleted["items"][0]["model_name"] == "drugi"

    only_first = client.get(f"/api/history?model_id={first}").json()
    assert only_first["total"] == 2


def test_global_log_is_paginated(client):
    model_id = create(client)
    for i in range(1, 6):
        client.put(f"/api/models/{model_id}", json={**VALID, "version": f"1.0.{i}"})
    page_1 = client.get("/api/history?page_size=4&page=1").json()
    page_2 = client.get("/api/history?page_size=4&page=2").json()
    assert page_1["total"] == 6 and page_1["pages"] == 2
    assert len(page_1["items"]) == 4 and len(page_2["items"]) == 2
    assert not {e["id"] for e in page_1["items"]} & {e["id"] for e in page_2["items"]}


def test_global_log_rejects_invalid_parameters(client):
    assert client.get("/api/history?action=inna").status_code == 400
    assert client.get("/api/history?page=0").status_code == 400
    assert client.get("/api/history?page_size=101").status_code == 400


def test_model_and_history_are_saved_atomically(client, monkeypatch):
    from app.repositories.history_repository import HistoryRepository

    def failing_add(self, *args, **kwargs):
        raise RuntimeError("awaria zapisu historii")

    monkeypatch.setattr(HistoryRepository, "add", failing_add)
    assert client.post("/api/models", json=VALID).status_code == 500
    monkeypatch.undo()
    # bez wpisu w historii nie ma też modelu
    assert client.get("/api/models").json()["total"] == 0
