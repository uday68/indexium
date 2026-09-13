from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import json


@dataclass
class Posting:
    doc_id: int
    term_frequency: int = 1
    positions: List[int] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "term_frequency": self.term_frequency,
            "positions": self.positions
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Posting":
        return cls(
            doc_id=data["doc_id"],
            term_frequency=data["term_frequency"],
            positions=data.get("positions", [])
        )


class InvertedIndex:
    """
    In-memory Inverted Index supporting term frequencies, positional postings,
    document lengths, and metadata lookups.
    """

    def __init__(self):
        # term -> {doc_id: Posting}
        self.index: Dict[str, Dict[int, Posting]] = {}
        # doc_id -> document length (total token count)
        self.doc_lengths: Dict[int, int] = {}
        # doc_id -> document metadata (url, title, snippet, etc.)
        self.doc_metadata: Dict[int, Dict[str, Any]] = {}

    @property
    def total_documents(self) -> int:
        return len(self.doc_lengths)

    @property
    def vocabulary_size(self) -> int:
        return len(self.index)

    @property
    def average_document_length(self) -> float:
        if not self.doc_lengths:
            return 0.0
        return sum(self.doc_lengths.values()) / len(self.doc_lengths)

    def add_document(self, doc_id: int, tokens_with_positions: List[tuple], metadata: Optional[Dict[str, Any]] = None):
        """Index a single document with its token sequence."""
        self.doc_lengths[doc_id] = len(tokens_with_positions)
        if metadata:
            self.doc_metadata[doc_id] = metadata

        term_positions: Dict[str, List[int]] = {}
        for token, pos in tokens_with_positions:
            if token not in term_positions:
                term_positions[token] = []
            term_positions[token].append(pos)

        for term, positions in term_positions.items():
            if term not in self.index:
                self.index[term] = {}
            self.index[term][doc_id] = Posting(
                doc_id=doc_id,
                term_frequency=len(positions),
                positions=positions
            )

    def remove_document(self, doc_id: int):
        """Remove a document from the index."""
        if doc_id in self.doc_lengths:
            del self.doc_lengths[doc_id]
        if doc_id in self.doc_metadata:
            del self.doc_metadata[doc_id]

        empty_terms = []
        for term, postings in self.index.items():
            if doc_id in postings:
                del postings[doc_id]
                if not postings:
                    empty_terms.append(term)
        for term in empty_terms:
            del self.index[term]

    def get_postings(self, term: str) -> List[Posting]:
        """Return postings list for a given term."""
        postings_map = self.index.get(term, {})
        return list(postings_map.values())

    def get_doc_frequency(self, term: str) -> int:
        """Return the number of documents containing term."""
        return len(self.index.get(term, {}))

    def get_collection_frequency(self, term: str) -> int:
        """Return total occurrences of term across all documents."""
        postings = self.index.get(term, {})
        return sum(p.term_frequency for p in postings.values())

    def get_metadata(self, doc_id: int) -> Optional[Dict[str, Any]]:
        return self.doc_metadata.get(doc_id)

    def to_json(self) -> str:
        """Serialize index to JSON string."""
        serializable_index = {}
        for term, postings in self.index.items():
            serializable_index[term] = {
                str(doc_id): p.to_dict() for doc_id, p in postings.items()
            }
        data = {
            "index": serializable_index,
            "doc_lengths": {str(k): v for k, v in self.doc_lengths.items()},
            "doc_metadata": {str(k): v for k, v in self.doc_metadata.items()}
        }
        return json.dumps(data)

    @classmethod
    def from_json(cls, json_str: str) -> "InvertedIndex":
        """Deserialize index from JSON string."""
        instance = cls()
        data = json.loads(json_str)
        instance.doc_lengths = {int(k): v for k, v in data.get("doc_lengths", {}).items()}
        instance.doc_metadata = {int(k): v for k, v in data.get("doc_metadata", {}).items()}
        
        raw_index = data.get("index", {})
        for term, postings in raw_index.items():
            instance.index[term] = {
                int(doc_id): Posting.from_dict(p_data)
                for doc_id, p_data in postings.items()
            }
        return instance
