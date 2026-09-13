from app.db.session import get_db
from app.services.search_service import search_service, SearchService
from app.services.index_service import index_service, IndexService
from app.services.crawl_service import crawl_service, CrawlService
from app.services.metrics_service import metrics_service, MetricsService


def get_search_service() -> SearchService:
    return search_service


def get_index_service() -> IndexService:
    return index_service


def get_crawl_service() -> CrawlService:
    return crawl_service


def get_metrics_service() -> MetricsService:
    return metrics_service
