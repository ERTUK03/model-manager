import pytest

MODEL = {"name": "iris", "framework": "scikit-learn", "task": "Klasyfikacja", "version": "1.0.0"}


@pytest.fixture
def model_id(client):
    return client.post("/api/models", json=MODEL).json()["id"]


def upload(client, model_id, name="iris.pkl", content=b"model-bytes"):
    assert client.post(f"/api/models/{model_id}/file", files={"file": (name, content)}).status_code == 200


def test_user_gets_download_url(client, user_client, model_id, storage):
    upload(client, model_id, content=b"x" * 1234)
    response = user_client.get(f"/api/models/{model_id}/download")
    assert response.status_code == 200
    body = response.json()
    (key,) = storage.files.keys()
    assert body["url"] == f"https://storage.test/{key}?sig=fake&ttl=300"
    assert body["file_name"] == "iris.pkl"
    assert body["file_size"] == 1234
    assert body["expires_in"] == 300


def test_admin_can_download_too(client, model_id):
    upload(client, model_id)
    assert client.get(f"/api/models/{model_id}/download").status_code == 200


def test_model_without_file_returns_404(client, model_id):
    response = client.get(f"/api/models/{model_id}/download")
    assert response.status_code == 404
    assert response.json() == {"detail": "Plik nie istnieje"}


def test_unknown_model_returns_404(client):
    assert client.get("/api/models/9999/download").status_code == 404


def test_download_after_file_removal_returns_404(client, model_id):
    upload(client, model_id)
    client.delete(f"/api/models/{model_id}/file")
    assert client.get(f"/api/models/{model_id}/download").status_code == 404


def test_anonymous_cannot_download(anon_client, client, model_id):
    upload(client, model_id)
    response = anon_client.get(f"/api/models/{model_id}/download")
    assert response.status_code == 401


def test_download_url_does_not_expose_internal_storage_path_in_model_details(client, model_id):
    upload(client, model_id)
    details = client.get(f"/api/models/{model_id}").json()
    assert "file_key" not in details and "url" not in details


def test_invalid_id_returns_400(client):
    assert client.get("/api/models/abc/download").status_code == 400
