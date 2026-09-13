from typing import List, Dict, Any, Optional
from app.core.ranking.base import BaseRanker, ScoreExplanation
from app.core.index.reader import IndexReader


class RankingExplainer:
    """Helper service to generate and format transparent score explanations."""

    def __init__(self, ranker: BaseRanker):
        self.ranker = ranker

    def explain(
        self,
        query_terms: List[str],
        doc_id: int,
        reader: IndexReader,
        doc_metadata: Optional[Dict[str, Any]] = None,
    ) -> ScoreExplanation:
        return self.ranker.explain(query_terms, doc_id, reader, doc_metadata)
