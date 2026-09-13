from typing import List, Optional
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from pydantic import BaseModel
from app.api.dependencies import get_index_service, get_crawl_service, get_search_service
from app.services.index_service import IndexService
from app.services.crawl_service import CrawlService
from app.services.search_service import SearchService
from app.models.document import DocumentCreate

router = APIRouter(prefix="/admin", tags=["Admin & Crawl"])


class CrawlRequest(BaseModel):
    seed_urls: List[str]
    max_pages: Optional[int] = 20


@router.post("/index")
def index_document(
    doc: DocumentCreate,
    index_svc: IndexService = Depends(get_index_service),
    search_svc: SearchService = Depends(get_search_service),
):
    """Add a new document directly to the inverted index."""
    doc_id = index_svc.index.total_documents + 1
    index_svc.add_document(doc_id=doc_id, title=doc.title, body=doc.body, url=doc.url)
    index_svc.save_index()
    search_svc._refresh_autocomplete()
    search_svc.cache.clear()
    return {"status": "indexed", "doc_id": doc_id, "url": doc.url}


@router.post("/crawl")
async def trigger_crawl(
    crawl_req: CrawlRequest,
    background_tasks: BackgroundTasks,
    crawl_svc: CrawlService = Depends(get_crawl_service),
):
    """Trigger a web crawling job on provided seed URLs."""
    if crawl_svc.is_running:
        raise HTTPException(status_code=400, detail="A crawl job is already running.")

    # Run in background task
    background_tasks.add_task(crawl_svc.run_crawl, crawl_req.seed_urls, crawl_req.max_pages)
    return {"status": "crawl_started", "seed_urls": crawl_req.seed_urls}


@router.post("/clear")
def clear_index(
    index_svc: IndexService = Depends(get_index_service),
    search_svc: SearchService = Depends(get_search_service),
):
    """Clear all documents from the inverted index and reset caches."""
    index_svc.clear()
    search_svc.cache.clear()
    return {"status": "index_cleared"}
