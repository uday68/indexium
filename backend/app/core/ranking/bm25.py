import math
from typing import List, Dict, Any, Optional
from app.core.ranking.base import BaseRanker, ScoreExplanation, TermScore
from app.core.index.reader import IndexReader


class BM25Ranker(BaseRanker):
    """
    Okapi BM25 probabilistic relevance ranking.
    k1 controls term frequency saturation, b controls document length normalization.
    """

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        super().__init__(name="bm25")
        self.k1 = k1
        self.b = b

    def _compute_idf(self, term: str, reader: IndexReader) -> float:
        N = reader.total_documents
        n = reader.get_doc_frequency(term)
        # Probabilistic IDF with smoothing to prevent negative values
        return math.log(((N - n + 0.5) / (n + 0.5)) + 1.0)

    def score(
        self,
        query_terms: List[str],
        doc_id: int,
        reader: IndexReader,
        doc_metadata: Optional[Dict[str, Any]] = None,
    ) -> float:
        doc_len = reader.get_doc_length(doc_id)
        avg_doc_len = reader.average_document_length or 1.0

        total_score = 0.0
        for term in query_terms:
            posting = reader.get_posting_for_doc(term, doc_id)
            if not posting:
                continue

            tf = posting.term_frequency
            idf = self._compute_idf(term, reader)
            
            numerator = tf * (self.k1 + 1.0)
            denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / avg_doc_len))
            contrib = idf * (numerator / denominator)
            total_score += contrib

        return total_score

    def explain(
        self,
        query_terms: List[str],
        doc_id: int,
        reader: IndexReader,
        doc_metadata: Optional[Dict[str, Any]] = None,
    ) -> ScoreExplanation:
        doc_len = reader.get_doc_length(doc_id)
        avg_doc_len = reader.average_document_length or 1.0
        term_scores: List[TermScore] = []
        total_score = 0.0

        for term in query_terms:
            idf = self._compute_idf(term, reader)
            posting = reader.get_posting_for_doc(term, doc_id)
            if posting:
                tf = posting.term_frequency
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / avg_doc_len))
                contrib = idf * (numerator / denominator)
                total_score += contrib
                term_scores.append(TermScore(term=term, tf=tf, idf=idf, contribution=contrib))
            else:
                term_scores.append(TermScore(term=term, tf=0, idf=idf, contribution=0.0))

        return ScoreExplanation(
            doc_id=doc_id,
            final_score=total_score,
            ranker_name=self.name,
            term_scores=term_scores,
            additional_factors={
                "k1": self.k1,
                "b": self.b,
                "doc_len": float(doc_len),
                "avg_doc_len": float(avg_doc_len),
            },
            details=f"Calculated BM25 score with k1={self.k1}, b={self.b}.",
        )
