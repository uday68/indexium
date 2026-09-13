import logging
from typing import List, Dict, Any, Optional
from app.core.crawler.crawler import WebCrawler
from app.services.index_service import index_service
from app.services.search_service import search_service
from app.core.observability.metrics import metrics
from app.config.settings import settings

logger = logging.getLogger(__name__)


class CrawlService:
    """Manages background crawl jobs and pipeline execution."""

    def __init__(self):
        self.crawler = WebCrawler(
            index_writer=index_service.writer,
            max_depth=settings.CRAWLER_MAX_DEPTH,
            max_pages=settings.CRAWLER_MAX_PAGES,
            politeness_delay_sec=settings.CRAWLER_POLITENESS_DELAY,
            user_agent=settings.CRAWLER_USER_AGENT,
        )
        self.is_running = False

    async def run_crawl(self, seed_urls: List[str], max_pages: Optional[int] = None) -> List[Dict[str, Any]]:
        self.is_running = True
        try:
            if max_pages:
                self.crawler.max_pages = max_pages
            self.crawler.seed(seed_urls)
            docs = await self.crawler.crawl()
            metrics.record_crawl(len(docs))
            metrics.set_indexed_documents(index_service.index.total_documents)
            
            # Save index snapshot and refresh autocomplete
            index_service.save_index()
            search_service._refresh_autocomplete()
            search_service.cache.clear()
            return docs
        finally:
            self.is_running = False


crawl_service = CrawlService()
