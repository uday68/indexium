import time
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.index_service import index_service
from app.services.search_service import search_service
from scripts.seed_data import seed


def benchmark():
    print("=== Indexium Search Engine Benchmark ===")
    seed()

    # 1. Indexing Benchmark
    docs_to_index = 500
    print(f"\n[1] Running indexing benchmark ({docs_to_index} synthetic documents)...")
    start = time.time()
    for i in range(100, 100 + docs_to_index):
        index_service.add_document(
            doc_id=i,
            title=f"Synthetic Web Document #{i}",
            body=f"This document discusses information retrieval, search engines, inverted index postings, BM25 ranking, and distributed systems node #{i}.",
            url=f"https://benchmark.example.com/docs/{i}",
        )
    index_duration = time.time() - start
    docs_per_sec = docs_to_index / index_duration if index_duration > 0 else 0
    print(f"Indexing completed in {index_duration:.3f}s ({docs_per_sec:.1f} docs/sec)")

    # 2. Query Latency & QPS Benchmark
    queries = [
        "search engine",
        "inverted index",
        "PageRank algorithm",
        "BM25 ranking",
        "distributed sharding",
        "web crawler",
        "information retrieval",
        "synthetic document",
    ]
    iterations = 200
    print(f"\n[2] Running query latency benchmark ({iterations} queries across {len(queries)} terms)...")

    latencies = []
    start = time.time()
    for i in range(iterations):
        q = queries[i % len(queries)]
        t0 = time.time()
        res = search_service.search(q, limit=10)
        t1 = time.time()
        latencies.append((t1 - t0) * 1000)

    total_time = time.time() - start
    qps = iterations / total_time if total_time > 0 else 0
    latencies.sort()
    p50 = latencies[int(len(latencies) * 0.50)]
    p95 = latencies[int(len(latencies) * 0.95)]
    p99 = latencies[int(len(latencies) * 0.99)]

    print(f"Throughput: {qps:.1f} QPS")
    print(f"Latency P50: {p50:.2f} ms")
    print(f"Latency P95: {p95:.2f} ms")
    print(f"Latency P99: {p99:.2f} ms")
    print("\nBenchmark completed successfully!")


if __name__ == "__main__":
    benchmark()
