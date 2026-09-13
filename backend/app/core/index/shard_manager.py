from typing import List, Dict, Any, Optional
from app.core.index.inverted import InvertedIndex, Posting
from app.core.index.writer import IndexWriter
from app.core.index.reader import IndexReader
from app.core.parser.tokenizer import Tokenizer


class ShardManager:
    """
    Manages document partitioning across multiple index shards.
    Demonstrates distributed search engine sharding principles.
    """

    def __init__(self, num_shards: int = 4, tokenizer: Optional[Tokenizer] = None):
        self.num_shards = max(1, num_shards)
        self.tokenizer = tokenizer if tokenizer is not None else Tokenizer()
        self.shards: List[InvertedIndex] = [InvertedIndex() for _ in range(self.num_shards)]
        self.writers: List[IndexWriter] = [IndexWriter(shard, self.tokenizer) for shard in self.shards]
        self.readers: List[IndexReader] = [IndexReader(shard) for shard in self.shards]

    def _get_shard_id(self, doc_id: int) -> int:
        return doc_id % self.num_shards

    def add_document(self, doc_id: int, text: str, metadata: Optional[Dict[str, Any]] = None):
        shard_id = self._get_shard_id(doc_id)
        self.writers[shard_id].add_document(doc_id, text, metadata)

    def delete_document(self, doc_id: int):
        shard_id = self._get_shard_id(doc_id)
        self.writers[shard_id].delete_document(doc_id)

    @property
    def total_documents(self) -> int:
        return sum(reader.total_documents for reader in self.readers)

    @property
    def total_vocabulary(self) -> int:
        all_terms = set()
        for shard in self.shards:
            all_terms.update(shard.index.keys())
        return len(all_terms)

    def get_postings_aggregated(self, term: str) -> List[Posting]:
        """Aggregate postings for a term across all shards."""
        aggregated: List[Posting] = []
        for reader in self.readers:
            aggregated.extend(reader.get_postings(term))
        return aggregated

    def get_doc_metadata(self, doc_id: int) -> Optional[Dict[str, Any]]:
        shard_id = self._get_shard_id(doc_id)
        return self.readers[shard_id].get_doc_metadata(doc_id)
