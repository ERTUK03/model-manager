from app.api.deps import get_model_service
from app.main import app

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


def create(client, **overrides):
    return client.post("/api/models", json={**VALID, **overrides})


def test_health_returns_200(client):
    assert client.get("/api/health").status_code == 200


def test_create_returns_201(client):
    response = create(client)
    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["name"] == "iris-classifier"


def test_list_returns_200(client):
    create(client)
    create(client, name="second-model")
    response = client.get("/api/models")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_existing_returns_200(client):
    model_id = create(client).json()["id"]
    response = client.get(f"/api/models/{model_id}")
    assert response.status_code == 200
    assert response.json()["id"] == model_id


def test_get_missing_returns_404(client):
    response = client.get("/api/models/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Model nie istnieje"}


def test_update_returns_200(client):
    model_id = create(client).json()["id"]
    response = client.put(f"/api/models/{model_id}", json={**VALID, "version": "1.1.0", "status": "published"})
    assert response.status_code == 200
    assert response.json()["version"] == "1.1.0"
    assert response.json()["status"] == "published"


def test_update_missing_returns_404(client):
    assert client.put("/api/models/999", json=VALID).status_code == 404


def test_delete_returns_204_then_404(client):
    model_id = create(client).json()["id"]
    assert client.delete(f"/api/models/{model_id}").status_code == 204
    assert client.get(f"/api/models/{model_id}").status_code == 404
    assert client.delete(f"/api/models/{model_id}").status_code == 404


def test_missing_required_field_returns_400(client):
    payload = {k: v for k, v in VALID.items() if k != "name"}
    response = client.post("/api/models", json=payload)
    assert response.status_code == 400
    assert response.json()["errors"][0]["field"] == "body.name"


def test_invalid_values_return_400(client):
    assert create(client, accuracy=1.5).status_code == 400
    assert create(client, version="abc").status_code == 400
    assert create(client, status="unknown").status_code == 400
    assert create(client, framework="Unknown").status_code == 400
    assert create(client, name="a").status_code == 400
    assert create(client, size_mb=-1).status_code == 400


def test_wrong_type_returns_400(client):
    assert create(client, accuracy="wysoka").status_code == 400


def test_unknown_field_returns_400(client):
    assert create(client, hack="x").status_code == 400


def test_invalid_id_returns_400(client):
    assert client.get("/api/models/abc").status_code == 400
    assert client.get("/api/models/0").status_code == 400


def test_unexpected_error_returns_500(client):
    class BrokenService:
        def list_models(self):
            raise RuntimeError("boom")

    app.dependency_overrides[get_model_service] = lambda: BrokenService()
    response = client.get("/api/models")
    assert response.status_code == 500
    assert response.json() == {"detail": "Wewnętrzny błąd serwera"}
