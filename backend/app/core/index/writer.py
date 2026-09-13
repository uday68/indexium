import os
import threading
from typing import List, Tuple, Dict, Any, Optional
from app.core.index.inverted import InvertedIndex
from app.core.parser.tokenizer import Tokenizer


class IndexWriter:
    """Manages thread-safe writing, document indexing, and persistence of an InvertedIndex."""

    def __init__(self, index: Optional[InvertedIndex] = None, tokenizer: Optional[Tokenizer] = None):
        self.index = index if index is not None else InvertedIndex()
        self.tokenizer = tokenizer if tokenizer is not None else Tokenizer()
        self._lock = threading.RLock()

    def add_document(self, doc_id: int, text: str, metadata: Optional[Dict[str, Any]] = None):
        """Tokenize text and add document to the index under write lock."""
        tokens_with_positions = self.tokenizer.tokenize_with_positions(text)
        with self._lock:
            self.index.add_document(doc_id, tokens_with_positions, metadata)

    def add_documents_batch(self, batch: List[Tuple[int, str, Optional[Dict[str, Any]]]]):
        """Index a batch of documents in a single locked transaction."""
        with self._lock:
            for doc_id, text, metadata in batch:
                tokens = self.tokenizer.tokenize_with_positions(text)
                self.index.add_document(doc_id, tokens, metadata)

    def delete_document(self, doc_id: int):
        """Remove a document by ID."""
        with self._lock:
            self.index.remove_document(doc_id)

    def clear(self):
        """Reset the index."""
        with self._lock:
            self.index = InvertedIndex()

    def save_to_file(self, file_path: str):
        """Persist index to file atomically."""
        with self._lock:
            data = self.index.to_json()
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            tmp_path = f"{file_path}.tmp"
            with open(tmp_path, "w", encoding="utf-8") as f:
                f.write(data)
            if os.path.exists(file_path):
                os.replace(tmp_path, file_path)
            else:
                os.rename(tmp_path, file_path)
