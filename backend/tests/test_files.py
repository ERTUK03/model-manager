import hashlib

import pytest

from app.api.deps import get_file_storage
from app.main import app
from app.repositories.history_repository import HistoryRepository

MODEL = {"name": "iris", "framework": "scikit-learn", "task": "Klasyfikacja", "version": "1.0.0", "size_mb": 99.0}
CONTENT = b"model-bytes" * 1000


@pytest.fixture
def model_id(client):
    return client.post("/api/models", json=MODEL).json()["id"]


def upload(client, model_id, content=CONTENT, name="iris.pkl", **kwargs):
    return client.post(f"/api/models/{model_id}/file", files={"file": (name, content, "application/octet-stream")}, **kwargs)


def history(client, model_id):
    return client.get(f"/api/models/{model_id}/history").json()


def test_upload_stores_file_and_metadata(client, model_id, storage):
    response = upload(client, model_id)
    assert response.status_code == 200
    body = response.json()
    assert body["file_name"] == "iris.pkl"
    assert body["file_size"] == len(CONTENT)
    assert body["file_sha256"] == hashlib.sha256(CONTENT).hexdigest()
    assert body["size_mb"] == round(len(CONTENT) / 1024 / 1024, 3)  # rozmiar pochodzi z pliku
    assert "file_key" not in body  # wewnętrzna nazwa obiektu nie jest ujawniana
    (stored,) = storage.files.values()
    assert stored == CONTENT


def test_file_info_is_visible_in_model_details(client, user_client, model_id):
    upload(client, model_id)
    details = user_client.get(f"/api/models/{model_id}").json()
    assert details["file_name"] == "iris.pkl" and details["file_size"] == len(CONTENT)


def test_model_without_file_has_empty_file_fields(client, model_id):
    body = client.get(f"/api/models/{model_id}").json()
    assert body["file_name"] is None and body["file_size"] is None and body["file_sha256"] is None


def test_upload_is_recorded_in_history(client, model_id):
    upload(client, model_id)
    entry = history(client, model_id)[0]
    assert entry["action"] == "updated"
    assert entry["changes"]["file_name"] == {"from": None, "to": "iris.pkl"}
    assert entry["changes"]["size_mb"]["from"] == 99.0
    assert entry["user_email"] == "admin@example.com"


def test_replacing_file_removes_old_object(client, model_id, storage):
    upload(client, model_id, b"pierwsza wersja", "v1.pkl")
    (old_key,) = storage.files.keys()
    upload(client, model_id, b"druga wersja", "v2.onnx")
    assert old_key not in storage.files
    assert list(storage.files.values()) == [b"druga wersja"]
    assert history(client, model_id)[0]["changes"]["file_name"] == {"from": "v1.pkl", "to": "v2.onnx"}


def test_model_update_keeps_file(client, model_id):
    upload(client, model_id)
    client.put(f"/api/models/{model_id}", json={**MODEL, "version": "2.0.0"})
    body = client.get(f"/api/models/{model_id}").json()
    assert body["version"] == "2.0.0" and body["file_name"] == "iris.pkl"


def test_delete_file(client, model_id, storage):
    upload(client, model_id)
    response = client.delete(f"/api/models/{model_id}/file")
    assert response.status_code == 200
    assert response.json()["file_name"] is None
    assert storage.files == {}
    assert history(client, model_id)[0]["changes"]["file_name"] == {"from": "iris.pkl", "to": None}
    assert client.delete(f"/api/models/{model_id}/file").status_code == 404


def test_deleting_model_removes_its_file(client, model_id, storage):
    upload(client, model_id)
    assert len(storage.files) == 1
    assert client.delete(f"/api/models/{model_id}").status_code == 204
    assert storage.files == {}


@pytest.mark.parametrize("name", ["malware.exe", "skrypt.py", "bez-rozszerzenia", "archiwum.pkl.zip", ".pkl"])
def test_disallowed_file_types_return_400(client, model_id, storage, name):
    response = upload(client, model_id, name=name)
    assert response.status_code == 400
    assert storage.files == {}


def test_extension_check_ignores_case(client, model_id):
    assert upload(client, model_id, name="MODEL.PKL").status_code == 200


def test_path_in_filename_is_removed(client, model_id):
    body = upload(client, model_id, name="../../etc/passwd.pkl").json()
    assert body["file_name"] == "passwd.pkl"
    assert upload(client, model_id, name="C:\\Users\\jan\\model.onnx").json()["file_name"] == "model.onnx"


def test_empty_file_returns_400(client, model_id, storage):
    response = upload(client, model_id, content=b"")
    assert response.status_code == 400
    assert response.json() == {"detail": "Plik jest pusty"}
    assert storage.files == {}


def test_too_large_file_returns_413(client, model_id, storage):
    # limit w testach: 1 MB. Tuż nad limitem odrzuca serwis, dużo powyżej: oprogramowanie pośredniczące
    just_over = upload(client, model_id, content=b"x" * (1024 * 1024 + 10))
    far_over = upload(client, model_id, content=b"x" * (3 * 1024 * 1024))
    assert just_over.status_code == far_over.status_code == 413
    assert "maksymalnie 1 MB" in just_over.json()["detail"]
    assert storage.files == {}


def test_file_at_the_limit_is_accepted(client, model_id):
    assert upload(client, model_id, content=b"x" * (1024 * 1024)).status_code == 200


def test_missing_file_field_returns_400(client, model_id):
    assert client.post(f"/api/models/{model_id}/file").status_code == 400


def test_unknown_model_returns_404_and_stores_nothing(client, storage):
    assert upload(client, 9999).status_code == 404
    assert client.delete("/api/models/9999/file").status_code == 404
    assert storage.files == {}


def test_only_admin_can_change_files(client, user_client, anon_client, model_id):
    upload(client, model_id)
    assert upload(user_client, model_id).status_code == 403
    assert user_client.delete(f"/api/models/{model_id}/file").status_code == 403
    assert upload(anon_client, model_id).status_code == 401
    assert client.get(f"/api/models/{model_id}").json()["file_name"] == "iris.pkl"


def test_storage_failure_returns_502_and_changes_nothing(client, model_id, storage):
    storage.fail_upload = True
    response = upload(client, model_id)
    assert response.status_code == 502
    assert client.get(f"/api/models/{model_id}").json()["file_name"] is None
    assert len(history(client, model_id)) == 1  # tylko wpis o utworzeniu modelu


def test_failed_database_write_does_not_leave_orphan_file(client, model_id, storage, monkeypatch):
    def failing_add(self, *args, **kwargs):
        raise RuntimeError("awaria zapisu historii")

    monkeypatch.setattr(HistoryRepository, "add", failing_add)
    assert upload(client, model_id).status_code == 500
    monkeypatch.undo()
    assert storage.files == {}
    assert client.get(f"/api/models/{model_id}").json()["file_name"] is None


def test_upload_without_configured_storage_returns_503(client, model_id, monkeypatch):
    app.dependency_overrides.pop(get_file_storage)  # usuwamy atrapę magazynu...
    monkeypatch.setattr("app.api.deps.get_storage", lambda: None)  # ...i symulujemy brak konfiguracji
    response = upload(client, model_id)
    assert response.status_code == 503
    assert response.json() == {"detail": "Magazyn plików nie jest skonfigurowany"}