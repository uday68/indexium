from typing import Dict, Any
from app.core.observability.metrics import metrics
from app.services.index_service import index_service
from app.services.search_service import search_service


class MetricsService:
    def get_system_stats(self) -> Dict[str, Any]:
        stats = metrics.get_stats()
        stats.update({
            "index_documents_total": index_service.index.total_documents,
            "index_vocabulary_total": index_service.index.vocabulary_size,
            "index_avg_doc_length": round(index_service.index.average_document_length, 2),
            "cache_hit_rate": round(search_service.cache.hit_rate, 4),
        })
        return stats

    def get_prometheus_metrics(self) -> str:
        metrics.set_indexed_documents(index_service.index.total_documents)
        return metrics.to_prometheus()


metrics_service = MetricsService()
