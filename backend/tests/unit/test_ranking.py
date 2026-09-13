from app.core.index.inverted import InvertedIndex
from app.core.index.writer import IndexWriter
from app.core.index.reader import IndexReader
from app.core.ranking.bm25 import BM25Ranker
from app.core.ranking.tfidf import TFIDFRanker
from app.core.ranking.pagerank import PageRankRanker, LinkGraph, PageRankCalculator


def test_bm25_and_tfidf_ranking():
    index = InvertedIndex()
    writer = IndexWriter(index)
    writer.add_document(1, "google search engine indexing algorithms")
    writer.add_document(2, "search engine optimization techniques")
    writer.add_document(3, "deep learning neural networks")

    reader = IndexReader(index)

    bm25 = BM25Ranker()
    score_doc1 = bm25.score(["google", "search"], 1, reader)
    score_doc2 = bm25.score(["google", "search"], 2, reader)
    score_doc3 = bm25.score(["google", "search"], 3, reader)

    # Document 1 has both "google" and "search", so it should score highest
    assert score_doc1 > score_doc2
    assert score_doc3 == 0.0

    tfidf = TFIDFRanker()
    tfidf_score1 = tfidf.score(["indexing"], 1, reader)
    assert tfidf_score1 > 0.0


def test_pagerank_stub_and_graph():
    graph = LinkGraph()
    graph.add_edge("https://a.com", "https://b.com")
    graph.add_edge("https://b.com", "https://c.com")
    graph.add_edge("https://c.com", "https://a.com")

    calc = PageRankCalculator()
    scores = calc.compute(graph)
    assert len(scores) == 3
    assert all(s > 0 for s in scores.values())

    ranker = PageRankRanker(pagerank_calculator=calc)
    assert ranker.name == "pagerank-hybrid"
