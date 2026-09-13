from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from app.core.index.reader import IndexReader


@dataclass
class TermScore:
    term: str
    tf: int
    idf: float
    contribution: float


@dataclass
class ScoreExplanation:
    doc_id: int
    final_score: float
    ranker_name: str
    term_scores: List[TermScore] = field(default_factory=list)
    additional_factors: Dict[str, float] = field(default_factory=dict)
    details: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "final_score": round(self.final_score, 4),
            "ranker_name": self.ranker_name,
            "term_scores": [
                {
                    "term": ts.term,
                    "tf": ts.tf,
                    "idf": round(ts.idf, 4),
                    "contribution": round(ts.contribution, 4),
                }
                for ts in self.term_scores
            ],
            "additional_factors": {k: round(v, 4) for k, v in self.additional_factors.items()},
            "details": self.details,
        }


@dataclass
class ScoredDocument:
    doc_id: int
    score: float
    explanation: Optional[ScoreExplanation] = None


class BaseRanker(ABC):
    """Abstract base class for all ranking algorithms."""

    def __init__(self, name: str = "base"):
        self.name = name

    @abstractmethod
    def score(
        self,
        query_terms: List[str],
        doc_id: int,
        reader: IndexReader,
        doc_metadata: Optional[Dict[str, Any]] = None,
    ) -> float:
        """Compute the numerical relevance score for a document given a query."""
        pass

    @abstractmethod
    def explain(
        self,
        query_terms: List[str],
        doc_id: int,
        reader: IndexReader,
        doc_metadata: Optional[Dict[str, Any]] = None,
    ) -> ScoreExplanation:
        """Provide detailed transparent breakdown of the scoring calculation."""
        pass
