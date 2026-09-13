import math
from typing import List, Dict, Any, Optional
from app.core.ranking.base import BaseRanker, ScoreExplanation, TermScore
from app.core.index.reader import IndexReader


class TFIDFRanker(BaseRanker):
    """Classic TF-IDF vector space relevance ranking."""

    def __init__(self):
        super().__init__(name="tf-idf")

    def _compute_idf(self, term: str, reader: IndexReader) -> float:
        total_docs = reader.total_documents
        df = reader.get_doc_frequency(term)
        # Smoothed inverse document frequency
        return math.log((1.0 + total_docs) / (1.0 + df)) + 1.0

    def score(
        self,
        query_terms: List[str],
        doc_id: int,
        reader: IndexReader,
        doc_metadata: Optional[Dict[str, Any]] = None,
    ) -> float:
        doc_length = reader.get_doc_length(doc_id)
        if doc_length == 0:
            return 0.0

        total_score = 0.0
        for term in query_terms:
            posting = reader.get_posting_for_doc(term, doc_id)
            if posting:
                tf = posting.term_frequency
                normalized_tf = tf / doc_length
                idf = self._compute_idf(term, reader)
                total_score += normalized_tf * idf

        return total_score

    def explain(
        self,
        query_terms: List[str],
        doc_id: int,
        reader: IndexReader,
        doc_metadata: Optional[Dict[str, Any]] = None,
    ) -> ScoreExplanation:
        doc_length = reader.get_doc_length(doc_id)
        term_scores: List[TermScore] = []
        total_score = 0.0

        for term in query_terms:
            posting = reader.get_posting_for_doc(term, doc_id)
            if posting:
                tf = posting.term_frequency
                norm_tf = (tf / doc_length) if doc_length > 0 else 0.0
                idf = self._compute_idf(term, reader)
                contrib = norm_tf * idf
                total_score += contrib
                term_scores.append(TermScore(term=term, tf=tf, idf=idf, contribution=contrib))
            else:
                idf = self._compute_idf(term, reader)
                term_scores.append(TermScore(term=term, tf=0, idf=idf, contribution=0.0))

        return ScoreExplanation(
            doc_id=doc_id,
            final_score=total_score,
            ranker_name=self.name,
            term_scores=term_scores,
            additional_factors={"doc_length": float(doc_length)},
            details=f"Calculated normalized TF-IDF across {len(term_scores)} query terms.",
        )
