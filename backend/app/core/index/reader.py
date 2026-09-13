import os
from typing import List, Dict, Optional, Any
from app.core.index.inverted import InvertedIndex, Posting


class IndexReader:
    """Provides read-only access and search queries into an InvertedIndex."""

    def __init__(self, index: InvertedIndex):
        self.index = index

    @classmethod
    def load_from_file(cls, file_path: str) -> "IndexReader":
        """Load an InvertedIndex snapshot from disk."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Index file not found: {file_path}")
        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read()
        index = InvertedIndex.from_json(data)
        return cls(index)

    def get_postings(self, term: str) -> List[Posting]:
        return self.index.get_postings(term)

    def get_posting_for_doc(self, term: str, doc_id: int) -> Optional[Posting]:
        term_map = self.index.index.get(term, {})
        return term_map.get(doc_id)

    def get_doc_frequency(self, term: str) -> int:
        return self.index.get_doc_frequency(term)

    def get_collection_frequency(self, term: str) -> int:
        return self.index.get_collection_frequency(term)

    def get_doc_length(self, doc_id: int) -> int:
        return self.index.doc_lengths.get(doc_id, 0)

    def get_doc_metadata(self, doc_id: int) -> Optional[Dict[str, Any]]:
        return self.index.get_metadata(doc_id)

    @property
    def total_documents(self) -> int:
        return self.index.total_documents

    @property
    def average_document_length(self) -> float:
        return self.index.average_document_length

    @property
    def vocabulary_size(self) -> int:
        return self.index.vocabulary_size
