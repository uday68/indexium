import os
import tempfile
from app.core.index.inverted import InvertedIndex
from app.core.index.writer import IndexWriter
from app.core.index.reader import IndexReader
from app.core.index.shard_manager import ShardManager
from app.core.parser.tokenizer import Tokenizer


def test_inverted_index_add_and_retrieve():
    index = InvertedIndex()
    tokenizer = Tokenizer()
    tokens1 = tokenizer.tokenize_with_positions("fast distributed search engine")
    tokens2 = tokenizer.tokenize_with_positions("fast web crawler")

    index.add_document(doc_id=1, tokens_with_positions=tokens1, metadata={"title": "Search Engine"})
    index.add_document(doc_id=2, tokens_with_positions=tokens2, metadata={"title": "Crawler"})

    assert index.total_documents == 2
    assert index.get_doc_frequency("fast") == 2
    assert index.get_doc_frequency("distributed") == 1

    postings = index.get_postings("fast")
    assert len(postings) == 2


def test_index_writer_and_reader_persistence():
    index = InvertedIndex()
    writer = IndexWriter(index)
    writer.add_document(doc_id=1, text="python machine learning", metadata={"title": "ML"})
    writer.add_document(doc_id=2, text="python search engine", metadata={"title": "Search"})

    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        writer.save_to_file(tmp_path)
        reader = IndexReader.load_from_file(tmp_path)
        assert reader.total_documents == 2
        assert reader.get_doc_frequency("python") == 2
        assert reader.get_doc_metadata(1)["title"] == "ML"
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


def test_shard_manager():
    sm = ShardManager(num_shards=3)
    sm.add_document(1, "distributed systems", metadata={"title": "DS"})
    sm.add_document(2, "distributed computing", metadata={"title": "DC"})
    sm.add_document(3, "cloud infrastructure", metadata={"title": "Cloud"})

    assert sm.total_documents == 3
    postings = sm.get_postings_aggregated("distributed")
    assert len(postings) == 2
