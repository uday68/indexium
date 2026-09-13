"""
========================================================================================
KEY COMPONENT — PAGERANK / LINK GRAPH RANKING ALGORITHM
========================================================================================
User Instruction: "keep out the key part which i will implement"

This file provides the structure, graph modeling, and interface for the core PageRank
link analysis algorithm. The core computation step is stubbed with explicit TODO markers
for your implementation.
========================================================================================
"""

from typing import Dict, List, Set, Any, Optional
from app.core.ranking.base import BaseRanker, ScoreExplanation, TermScore
from app.core.index.reader import IndexReader


class LinkGraph:
    """Directed graph representing hyperlinks between indexed web pages."""

    def __init__(self):
        # url -> set of target URLs it links to (outlinks)
        self.out_links: Dict[str, Set[str]] = {}
        # url -> set of source URLs linking to it (inlinks)
        self.in_links: Dict[str, Set[str]] = {}
        # All known URLs in graph
        self.nodes: Set[str] = set()

    def add_node(self, url: str):
        self.nodes.add(url)
        if url not in self.out_links:
            self.out_links[url] = set()
        if url not in self.in_links:
            self.in_links[url] = set()

    def add_edge(self, source_url: str, target_url: str):
        self.add_node(source_url)
        self.add_node(target_url)
        self.out_links[source_url].add(target_url)
        self.in_links[target_url].add(source_url)

    def get_out_degree(self, url: str) -> int:
        return len(self.out_links.get(url, set()))

    def get_in_links(self, url: str) -> Set[str]:
        return self.in_links.get(url, set())


class PageRankCalculator:
    """
    ===================================================================================
    TODO (FOR YOU TO IMPLEMENT):
    Implement the PageRank algorithm using power iteration or random walk with restart.
    
    Formula:
        PR(p_i) = (1 - d) / N + d * SUM_{p_j in M(p_i)} (PR(p_j) / L(p_j))
    
    Where:
        - d = damping factor (standard 0.85)
        - N = total number of pages in the graph
        - M(p_i) = set of pages that link to p_i (in-links)
        - L(p_j) = number of out-links on page p_j
        - iterations = number of iterations until convergence (e.g. max_iter=100, tol=1e-6)
    ===================================================================================
    """

    def __init__(self, damping_factor: float = 0.85, max_iterations: int = 100, tolerance: float = 1e-6):
        self.damping_factor = damping_factor
        self.max_iterations = max_iterations
        self.tolerance = tolerance
        self.scores: Dict[str, float] = {}

    def compute(self, graph: LinkGraph) -> Dict[str, float]:
        """
        Compute PageRank scores for all nodes in the given link graph.
        
        >>> USER IMPLEMENTATION GOES HERE <<<
        """
        N = len(graph.nodes)
        if N == 0:
            return {}

        # Default placeholder: Uniform score distribution (1.0 / N)
        # REPLACE THIS BLOCK WITH YOUR POWER-ITERATION OR RANDOM-WALK ALGORITHM:
        initial_score = 1.0 / N
        self.scores = {node: initial_score for node in graph.nodes}

        # -------------------------------------------------------------------------
        # TODO: Implement your iterative PageRank calculation loop here:
        # for iteration in range(self.max_iterations):
        #     ...
        # -------------------------------------------------------------------------

        return self.scores


class PageRankRanker(BaseRanker):
    """
    Hybrid Ranker combining BM25 textual relevance with PageRank link authority.
    Final Score = (1 - alpha) * BM25_score + alpha * (PageRank_score * weight)
    """

    def __init__(self, alpha: float = 0.3, pagerank_calculator: Optional[PageRankCalculator] = None):
        super().__init__(name="pagerank-hybrid")
        self.alpha = alpha
        self.calculator = pagerank_calculator if pagerank_calculator is not None else PageRankCalculator()

    def score(
        self,
        query_terms: List[str],
        doc_id: int,
        reader: IndexReader,
        doc_metadata: Optional[Dict[str, Any]] = None,
    ) -> float:
        # Basic textual relevance
        text_score = 0.0
        for term in query_terms:
            posting = reader.get_posting_for_doc(term, doc_id)
            if posting:
                text_score += posting.term_frequency

        # Graph link authority score from metadata or calculator
        url = doc_metadata.get("url", "") if doc_metadata else ""
        pr_score = self.calculator.scores.get(url, 0.0)

        return (1.0 - self.alpha) * text_score + (self.alpha * pr_score * 100.0)

    def explain(
        self,
        query_terms: List[str],
        doc_id: int,
        reader: IndexReader,
        doc_metadata: Optional[Dict[str, Any]] = None,
    ) -> ScoreExplanation:
        url = doc_metadata.get("url", "") if doc_metadata else ""
        pr_score = self.calculator.scores.get(url, 0.0)
        final = self.score(query_terms, doc_id, reader, doc_metadata)

        return ScoreExplanation(
            doc_id=doc_id,
            final_score=final,
            ranker_name=self.name,
            additional_factors={
                "alpha": self.alpha,
                "pagerank_score": pr_score,
                "url": 0.0,
            },
            details="Hybrid ranking combining textual matches with PageRank graph score (placeholder ready for your algorithm).",
        )
