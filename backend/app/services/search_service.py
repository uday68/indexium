import time
import logging
from typing import List, Dict, Any, Optional
from app.services.index_service import index_service
from app.core.query.executor import QueryExecutor, SearchResponse, SearchResultItem
from app.core.query.rewrite import QueryRewriter
from app.core.query.autocomplete import AutocompleteTrie
from app.core.cache.redis_client import CacheClient
from app.core.ranking.bm25 import BM25Ranker
from app.core.ranking.tfidf import TFIDFRanker
from app.core.ranking.pagerank import PageRankRanker
from app.core.observability.metrics import metrics
from app.config.settings import settings
from app.config.feature_flags import feature_flags

logger = logging.getLogger(__name__)


class SearchService:
    """Service orchestrating search queries, caching, ranking, and autocomplete."""

    def __init__(self):
        self.cache = CacheClient(redis_url=settings.REDIS_URL)
        self.rankers = {
            "bm25": BM25Ranker(),
            "tfidf": TFIDFRanker(),
            "pagerank": PageRankRanker(),
        }
        self.rewriter = QueryRewriter()
        self.autocomplete_trie = AutocompleteTrie()
        self._refresh_autocomplete()

    def _refresh_autocomplete(self):
        """Populate autocomplete trie from indexed terms."""
        for term, postings in index_service.index.index.items():
            freq = sum(p.term_frequency for p in postings.values())
            self.autocomplete_trie.insert(term, frequency=freq)

    def search(
        self,
        query: str,
        ranker_name: Optional[str] = None,
        limit: int = 10,
        offset: int = 0,
        explain: bool = False,
    ) -> SearchResponse:
        start_time = time.time()
        clean_query = query.strip()
        if not clean_query:
            return SearchResponse(query="", total_hits=0, execution_time_ms=0.0, results=[])

        chosen_ranker = self.rankers.get(ranker_name or settings.DEFAULT_RANKER, self.rankers["bm25"])
        cache_key = f"search:{clean_query}:{chosen_ranker.name}:{limit}:{offset}:{explain}"

        # 1. Check Cache
        if feature_flags.is_enabled("enable_caching") and not explain:
            cached = self.cache.get(cache_key)
            if cached:
                elapsed_ms = (time.time() - start_time) * 1000
                metrics.record_query(elapsed_ms)
                items = [SearchResultItem(**item) for item in cached["results"]]
                return SearchResponse(
                    query=clean_query,
                    total_hits=cached["total_hits"],
                    execution_time_ms=round(elapsed_ms, 2),
                    results=items,
                    suggestion=cached.get("suggestion"),
                )

        # 2. Execute Query
        executor = QueryExecutor(reader=index_service.reader, default_ranker=chosen_ranker)
        results = executor.execute(clean_query, ranker=chosen_ranker, limit=limit, offset=offset, explain=explain)

        # 3. Spell check / Suggestion
        suggestion = None
        if feature_flags.is_enabled("enable_spell_suggestions") and not results:
            suggestion = self.rewriter.rewrite_query(clean_query, index_service.reader)

        elapsed_ms = (time.time() - start_time) * 1000
        metrics.record_query(elapsed_ms)

        # Cache results
        if feature_flags.is_enabled("enable_caching") and not explain:
            cache_payload = {
                "total_hits": len(results),
                "results": [
                    {
                        "doc_id": r.doc_id,
                        "score": r.score,
                        "title": r.title,
                        "url": r.url,
                        "snippet": r.snippet,
                        "explanation": r.explanation,
                    }
                    for r in results
                ],
                "suggestion": suggestion,
            }
            self.cache.set(cache_key, cache_payload, ttl_sec=settings.CACHE_TTL_SECONDS)

        return SearchResponse(
            query=clean_query,
            total_hits=len(results),
            execution_time_ms=round(elapsed_ms, 2),
            results=results,
            suggestion=suggestion,
        )

    def autocomplete(self, prefix: str, max_results: int = 5) -> List[str]:
        return self.autocomplete_trie.search_prefix(prefix, max_results=max_results)

    def explain(self, query: str, doc_id: int, ranker_name: Optional[str] = None) -> Optional[Dict[str, Any]]:
        chosen_ranker = self.rankers.get(ranker_name or settings.DEFAULT_RANKER, self.rankers["bm25"])
        tokens = index_service.tokenizer.tokenize(query)
        meta = index_service.reader.get_doc_metadata(doc_id)
        if not meta:
            return None
        explanation = chosen_ranker.explain(tokens, doc_id, index_service.reader, meta)
        return explanation.to_dict()


search_service = SearchService()
