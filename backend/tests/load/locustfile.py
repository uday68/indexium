import random
from locust import HttpUser, task, between

QUERIES = [
    "search engine",
    "inverted index",
    "PageRank",
    "BM25",
    "web crawling",
    "information retrieval",
    "distributed sharding",
    "tokenization",
]


class IndexiumLoadUser(HttpUser):
    wait_time = between(0.1, 1.0)

    @task(5)
    def search(self):
        query = random.choice(QUERIES)
        self.client.get(f"/api/v1/search?q={query}&limit=10")

    @task(2)
    def autocomplete(self):
        prefix = random.choice(["sea", "inv", "pag", "bm", "web"])
        self.client.get(f"/api/v1/search/autocomplete?prefix={prefix}")

    @task(1)
    def stats(self):
        self.client.get("/api/v1/stats")
