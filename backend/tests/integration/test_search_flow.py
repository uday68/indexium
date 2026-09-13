from fastapi.testclient import TestClient
from app.main import app
from app.services.index_service import index_service

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_search_flow_end_to_end():
    # Ensure index has at least one document
    index_service.add_document(
        doc_id=99,
        title="PageRank and Inverted Index Architecture",
        body="Google page indexing relies on inverted files and hyperlink graph structures.",
        url="https://test.com/pagerank-architecture",
    )

    # 1. Search Query
    response = client.get("/api/v1/search?q=PageRank+architecture")
    assert response.status_code == 200
    data = response.json()
    assert data["total_hits"] > 0
    assert any("PageRank" in item["title"] for item in data["results"])

    # 2. Autocomplete
    ac_response = client.get("/api/v1/search/autocomplete?prefix=page")
    assert ac_response.status_code == 200
    suggestions = ac_response.json()
    assert isinstance(suggestions, list)

    # 3. Explain Score
    doc_id = data["results"][0]["doc_id"]
    explain_response = client.get(f"/api/v1/explain?q=PageRank&doc_id={doc_id}")
    assert explain_response.status_code == 200
    explain_data = explain_response.json()
    assert explain_data["doc_id"] == doc_id
    assert "final_score" in explain_data
