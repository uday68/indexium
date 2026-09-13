from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, Query, HTTPException
from app.api.dependencies import get_search_service
from app.services.search_service import SearchService

router = APIRouter(prefix="/explain", tags=["Explainability"])


@router.get("", response_model=Dict[str, Any])
def explain_ranking_score(
    q: str = Query(..., description="Query terms to explain score for"),
    doc_id: int = Query(..., description="Document ID to explain"),
    ranker: Optional[str] = Query(None, description="Ranking algorithm: bm25, tfidf, pagerank"),
    service: SearchService = Depends(get_search_service),
):
    """Return transparent score breakdown explaining why a document received its ranking score."""
    explanation = service.explain(query=q, doc_id=doc_id, ranker_name=ranker)
    if not explanation:
        raise HTTPException(status_code=404, detail=f"Document #{doc_id} not found in index.")
    return explanation
