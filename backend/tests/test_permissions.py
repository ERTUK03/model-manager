VALID = {
    "name": "iris-classifier",
    "description": "Klasyfikacja irysów",
    "framework": "scikit-learn",
    "task": "Klasyfikacja",
    "version": "1.0.0",
    "accuracy": 0.95,
    "size_mb": 1.2,
    "status": "draft",
}


def test_health_is_public(anon_client):
    assert anon_client.get("/api/health").status_code == 200


def test_anonymous_cannot_access_models(anon_client):
    for response in (
        anon_client.get("/api/models"),
        anon_client.get("/api/models/1"),
        anon_client.post("/api/models", json=VALID),
        anon_client.put("/api/models/1", json=VALID),
        anon_client.delete("/api/models/1"),
    ):
        assert response.status_code == 401
        assert response.headers["www-authenticate"] == "Bearer"


def test_invalid_token_is_rejected(anon_client):
    response = anon_client.get("/api/models", headers={"Authorization": "Bearer nieprawidlowy"})
    assert response.status_code == 401


def test_user_can_read_models(client, user_client):
    model_id = client.post("/api/models", json=VALID).json()["id"]
    assert user_client.get("/api/models").status_code == 200
    assert user_client.get(f"/api/models/{model_id}").status_code == 200


def test_user_cannot_modify_models(client, user_client):
    model_id = client.post("/api/models", json=VALID).json()["id"]

    created = user_client.post("/api/models", json=VALID)
    assert created.status_code == 403
    assert created.json() == {"detail": "Brak uprawnień do wykonania tej operacji"}
    assert user_client.put(f"/api/models/{model_id}", json=VALID).status_code == 403
    assert user_client.delete(f"/api/models/{model_id}").status_code == 403

    # model nie został zmieniony ani usunięty
    assert client.get(f"/api/models/{model_id}").status_code == 200
    assert client.get("/api/models").json()["total"] == 1


def test_permission_is_checked_before_validation(user_client):
    # Zwykły użytkownik dostaje 403 także dla niepoprawnych danych, bez ujawniania reguł walidacji
    assert user_client.post("/api/models", json={}).status_code == 403


def test_admin_can_modify_models(client):
    created = client.post("/api/models", json=VALID)
    assert created.status_code == 201
    model_id = created.json()["id"]
    assert client.put(f"/api/models/{model_id}", json={**VALID, "status": "published"}).status_code == 200
    assert client.delete(f"/api/models/{model_id}").status_code == 204
