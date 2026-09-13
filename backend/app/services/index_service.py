import os
import logging
from typing import Dict, Any, Optional
from app.core.index.inverted import InvertedIndex
from app.core.index.writer import IndexWriter
from app.core.index.reader import IndexReader
from app.core.parser.tokenizer import Tokenizer
from app.config.settings import settings

logger = logging.getLogger(__name__)


class IndexService:
    """Singleton service managing the global InvertedIndex, IndexWriter, and IndexReader."""

    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or settings.INDEX_STORAGE_PATH
        self.tokenizer = Tokenizer()
        self.index = InvertedIndex()
        self.writer = IndexWriter(self.index, self.tokenizer)
        self.reader = IndexReader(self.index)
        self._load_existing_index()

    def _load_existing_index(self):
        if self.storage_path and os.path.exists(self.storage_path):
            try:
                self.reader = IndexReader.load_from_file(self.storage_path)
                self.index = self.reader.index
                self.writer = IndexWriter(self.index, self.tokenizer)
                logger.info(f"Loaded {self.index.total_documents} documents from {self.storage_path}")
            except Exception as e:
                logger.warning(f"Could not load index snapshot: {e}")

    def add_document(self, doc_id: int, title: str, body: str, url: str, extra: Optional[Dict[str, Any]] = None):
        full_text = f"{title} {body}"
        meta = {
            "title": title,
            "body": body,
            "url": url,
            **(extra or {})
        }
        self.writer.add_document(doc_id, full_text, meta)

    def save_index(self):
        if self.storage_path:
            self.writer.save_to_file(self.storage_path)

    def clear(self):
        self.writer.clear()
        self.index = self.writer.index
        self.reader = IndexReader(self.index)


index_service = IndexService()
