from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from app.core.index.reader import IndexReader
from app.core.ranking.base import BaseRanker, ScoreExplanation
from app.core.ranking.bm25 import BM25Ranker
from app.core.query.parser import QueryParser, ParsedQuery
from app.core.parser.snippet import SnippetGenerator


@dataclass
class SearchResultItem:
    doc_id: int
    score: float
    title: str
    url: str
    snippet: str
    explanation: Optional[Dict[str, Any]] = None


@dataclass
class SearchResponse:
    query: str
    total_hits: int
    execution_time_ms: float
    results: List[SearchResultItem] = field(default_factory=list)
    suggestion: Optional[str] = None


class QueryExecutor:
    """Evaluates parsed queries against the InvertedIndex and returns ranked search results."""

    def __init__(
        self,
        reader: IndexReader,
        default_ranker: Optional[BaseRanker] = None,
        query_parser: Optional[QueryParser] = None,
        snippet_generator: Optional[SnippetGenerator] = None,
    ):
        self.reader = reader
        self.ranker = default_ranker if default_ranker is not None else BM25Ranker()
        self.query_parser = query_parser if query_parser is not None else QueryParser()
        self.snippet_generator = snippet_generator if snippet_generator is not None else SnippetGenerator()

    def _matches_phrase(self, phrase_tokens: List[str], doc_id: int) -> bool:
        """Verify that phrase tokens appear contiguously in doc_id."""
        if not phrase_tokens:
            return True

        # Retrieve postings for each token in the phrase
        postings = [self.reader.get_posting_for_doc(t, doc_id) for t in phrase_tokens]
        if any(p is None for p in postings):
            return False

        # Check for contiguous positions: pos, pos+1, pos+2...
        first_positions = postings[0].positions
        for start_pos in first_positions:
            match = True
            for offset, p in enumerate(postings[1:], start=1):
                if (start_pos + offset) not in p.positions:
                    match = False
                    break
            if match:
                return True
        return False

    def execute(
        self,
        query_str: str,
        ranker: Optional[BaseRanker] = None,
        limit: int = 10,
        offset: int = 0,
        explain: bool = False,
    ) -> List[SearchResultItem]:
        active_ranker = ranker or self.ranker
        parsed = self.query_parser.parse(query_str)
        if not parsed.terms:
            return []

        # Find candidate documents
        candidate_docs: Set[int] = set()

        # Handle must_have terms (+term)
        if parsed.must_have_terms:
            first = True
            for term in parsed.must_have_terms:
                postings = self.reader.get_postings(term)
                term_doc_ids = {p.doc_id for p in postings}
                if first:
                    candidate_docs = term_doc_ids
                    first = False
                else:
                    candidate_docs &= term_doc_ids
        else:
            # Union of documents containing any query term
            for term in parsed.terms:
                postings = self.reader.get_postings(term)
                for p in postings:
                    candidate_docs.add(p.doc_id)

        # Exclude must_not terms (-term)
        for neg_term in parsed.must_not_terms:
            neg_postings = self.reader.get_postings(neg_term)
            for p in neg_postings:
                candidate_docs.discard(p.doc_id)

        # Verify phrase constraints
        if parsed.phrases:
            filtered_candidates = set()
            for doc_id in candidate_docs:
                if all(self._matches_phrase(phrase, doc_id) for phrase in parsed.phrases):
                    filtered_candidates.add(doc_id)
            candidate_docs = filtered_candidates

        # Score candidate documents
        scored_items = []
        for doc_id in candidate_docs:
            meta = self.reader.get_doc_metadata(doc_id) or {}
            score = active_ranker.score(parsed.terms, doc_id, self.reader, meta)
            if score > 0:
                explanation = None
                if explain:
                    exp = active_ranker.explain(parsed.terms, doc_id, self.reader, meta)
                    explanation = exp.to_dict()

                body_text = meta.get("body", "") or meta.get("content", "")
                snippet = self.snippet_generator.generate(body_text, parsed.terms)

                scored_items.append(
                    SearchResultItem(
                        doc_id=doc_id,
                        score=score,
                        title=meta.get("title", f"Document #{doc_id}"),
                        url=meta.get("url", f"https://example.com/doc/{doc_id}"),
                        snippet=snippet,
                        explanation=explanation,
                    )
                )

        # Sort descending by score
        scored_items.sort(key=lambda x: x.score, reverse=True)
        return scored_items[offset : offset + limit]
