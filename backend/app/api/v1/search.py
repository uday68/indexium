from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from app.api.dependencies import get_search_service
from app.services.search_service import SearchService
from app.core.query.executor import SearchResponse
from app.models.click_log import ClickLogCreate

router = APIRouter(prefix="/search", tags=["Search"])


@router.get("", response_model=SearchResponse)
def search_documents(
    q: str = Query(..., description="The query string to search for"),
    ranker: Optional[str] = Query(None, description="Ranking algorithm: bm25, tfidf, pagerank"),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    explain: bool = Query(False, description="Include transparent score explanation"),
    service: SearchService = Depends(get_search_service),
):
    """Execute ranked search across indexed documents."""
    return service.search(query=q, ranker_name=ranker, limit=limit, offset=offset, explain=explain)


@router.get("/autocomplete", response_model=List[str])
def autocomplete_query(
    prefix: str = Query(..., min_length=1),
    limit: int = Query(5, ge=1, le=20),
    service: SearchService = Depends(get_search_service),
):
    """Return prefix-matching query suggestions."""
    return service.autocomplete(prefix=prefix, max_results=limit)


@router.post("/click")
def record_click(
    click_data: ClickLogCreate,
):
    """Record document click for CTR tracking."""
    # Click log can be persisted to DB or telemetry
    return {"status": "recorded", "query": click_data.query, "doc_id": click_data.doc_id}
