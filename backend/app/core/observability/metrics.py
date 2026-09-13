import time
import threading
from typing import Dict, List, Any


class MetricsCollector:
    """Collects search and indexing operational metrics, with Prometheus export support."""

    def __init__(self):
        self._lock = threading.RLock()
        self.query_count = 0
        self.crawl_count = 0
        self.indexed_doc_count = 0
        self.query_latencies_ms: List[float] = []
        self.start_time = time.time()

    def record_query(self, latency_ms: float):
        with self._lock:
            self.query_count += 1
            self.query_latencies_ms.append(latency_ms)
            if len(self.query_latencies_ms) > 10000:
                self.query_latencies_ms = self.query_latencies_ms[-5000:]

    def record_crawl(self, count: int = 1):
        with self._lock:
            self.crawl_count += count

    def set_indexed_documents(self, count: int):
        with self._lock:
            self.indexed_doc_count = count

    def get_stats(self) -> Dict[str, Any]:
        with self._lock:
            uptime = time.time() - self.start_time
            qps = (self.query_count / uptime) if uptime > 0 else 0.0

            latencies = sorted(self.query_latencies_ms)
            p50 = latencies[int(len(latencies) * 0.50)] if latencies else 0.0
            p95 = latencies[int(len(latencies) * 0.95)] if latencies else 0.0
            p99 = latencies[int(len(latencies) * 0.99)] if latencies else 0.0

            return {
                "uptime_seconds": round(uptime, 2),
                "total_queries": self.query_count,
                "qps": round(qps, 2),
                "latency_p50_ms": round(p50, 2),
                "latency_p95_ms": round(p95, 2),
                "latency_p99_ms": round(p99, 2),
                "total_crawled": self.crawl_count,
                "indexed_documents": self.indexed_doc_count,
            }

    def to_prometheus(self) -> str:
        stats = self.get_stats()
        lines = [
            "# HELP indexium_queries_total Total number of search queries executed",
            "# TYPE indexium_queries_total counter",
            f"indexium_queries_total {stats['total_queries']}",
            "# HELP indexium_query_qps Current queries per second",
            "# TYPE indexium_query_qps gauge",
            f"indexium_query_qps {stats['qps']}",
            "# HELP indexium_latency_p50_ms P50 latency in ms",
            "# TYPE indexium_latency_p50_ms gauge",
            f"indexium_latency_p50_ms {stats['latency_p50_ms']}",
            "# HELP indexium_latency_p95_ms P95 latency in ms",
            "# TYPE indexium_latency_p95_ms gauge",
            f"indexium_latency_p95_ms {stats['latency_p95_ms']}",
            "# HELP indexium_indexed_documents Total indexed documents",
            "# TYPE indexium_indexed_documents gauge",
            f"indexium_indexed_documents {stats['indexed_documents']}",
        ]
        return "\n".join(lines) + "\n"


# Global metrics collector instance
metrics = MetricsCollector()
