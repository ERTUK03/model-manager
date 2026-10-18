import pytest

FRAMEWORKS = ["scikit-learn", "XGBoost", "PyTorch", "TensorFlow", "ONNX"]


def make(client, name, **overrides):
    payload = {
        "name": name,
        "description": f"Opis modelu {name}",
        "framework": "ONNX",
        "task": "Klasyfikacja",
        "version": "1.0.0",
        "status": "draft",
        **overrides,
    }
    response = client.post("/api/models", json=payload)
    assert response.status_code == 201, response.text
    return response.json()


def names(response):
    return [item["name"] for item in response.json()["items"]]


@pytest.fixture
def many(client):
    for i in range(25):
        make(client, f"model-{i:02d}", framework=FRAMEWORKS[i % 5], status=["draft", "published", "archived"][i % 3])


def test_response_has_pagination_metadata(client, many):
    body = client.get("/api/models").json()
    assert body["total"] == 25
    assert body["page"] == 1
    assert body["page_size"] == 10
    assert body["pages"] == 3
    assert len(body["items"]) == 10


def test_pages_cover_all_items_without_duplicates(client, many):
    seen = []
    for page in (1, 2, 3):
        seen += names(client.get(f"/api/models?page={page}&page_size=10"))
    assert len(seen) == 25
    assert len(set(seen)) == 25


def test_last_page_is_partial_and_out_of_range_page_is_empty(client, many):
    assert len(client.get("/api/models?page=3").json()["items"]) == 5
    beyond = client.get("/api/models?page=99").json()
    assert beyond["items"] == [] and beyond["total"] == 25


def test_empty_database_returns_zero_pages(client):
    body = client.get("/api/models").json()
    assert body == {"items": [], "total": 0, "page": 1, "page_size": 10, "pages": 0}


def test_default_order_is_newest_first(client, many):
    assert names(client.get("/api/models?page_size=3")) == ["model-24", "model-23", "model-22"]


def test_sort_by_name(client, many):
    assert names(client.get("/api/models?sort=name&order=asc&page_size=2")) == ["model-00", "model-01"]
    assert names(client.get("/api/models?sort=name&order=desc&page_size=2")) == ["model-24", "model-23"]


def test_sort_puts_missing_values_last_in_both_directions(client):
    make(client, "bez-dokladnosci")
    make(client, "niska", accuracy=0.2)
    make(client, "wysoka", accuracy=0.9)
    assert names(client.get("/api/models?sort=accuracy&order=desc")) == ["wysoka", "niska", "bez-dokladnosci"]
    assert names(client.get("/api/models?sort=accuracy&order=asc")) == ["niska", "wysoka", "bez-dokladnosci"]


def test_filter_by_framework_and_status(client, many):
    onnx = client.get("/api/models?framework=ONNX&page_size=100").json()
    assert onnx["total"] == 5
    assert all(item["framework"] == "ONNX" for item in onnx["items"])

    published = client.get("/api/models?status=published&page_size=100").json()
    assert published["total"] == 8
    assert all(item["status"] == "published" for item in published["items"])

    both = client.get("/api/models?framework=ONNX&status=published&page_size=100").json()
    assert 0 < both["total"] < 5
    assert all(i["framework"] == "ONNX" and i["status"] == "published" for i in both["items"])


def test_search_matches_name_or_description_case_insensitively(client):
    make(client, "Sentiment-PL", description="Analiza opinii")
    make(client, "iris", description="Klasyfikator SENTYMENTU irysów")
    make(client, "inny", description="coś zupełnie innego")
    assert sorted(names(client.get("/api/models?search=sentiment"))) == ["Sentiment-PL"]
    assert sorted(names(client.get("/api/models?search=SENTYMENT"))) == ["iris"]
    assert sorted(names(client.get("/api/models?search=opinii"))) == ["Sentiment-PL"]
    assert client.get("/api/models?search=nic-takiego").json()["total"] == 0


def test_search_treats_wildcards_literally(client):
    make(client, "model_a")
    make(client, "modelXa")
    make(client, "100%-pewny")
    assert names(client.get("/api/models?search=model_a")) == ["model_a"]
    assert names(client.get("/api/models?search=%25")) == ["100%-pewny"]


def test_empty_search_is_ignored_and_search_is_trimmed(client):
    make(client, "iris")
    assert client.get("/api/models?search=").json()["total"] == 1
    assert client.get("/api/models?search=%20iris%20").json()["total"] == 1


def test_filters_combine_with_pagination_total(client, many):
    body = client.get("/api/models?framework=ONNX&page_size=2&page=2").json()
    assert body["total"] == 5 and body["pages"] == 3 and len(body["items"]) == 2


@pytest.mark.parametrize(
    "query",
    [
        "page=0",
        "page=abc",
        "page_size=0",
        "page_size=101",
        "sort=password",
        "order=sideways",
        "framework=Nieznany",
        "status=inny",
        "nieznany=1",
        "search=" + "a" * 101,
    ],
)
def test_invalid_query_returns_400(client, query):
    response = client.get(f"/api/models?{query}")
    assert response.status_code == 400
    assert response.json()["errors"]
