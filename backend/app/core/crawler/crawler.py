import asyncio
import logging
from typing import List, Optional, Callable, Dict, Any
import httpx
from app.core.crawler.scheduler import CrawlScheduler
from app.core.crawler.deduplicator import Deduplicator
from app.core.crawler.robots import RobotsManager
from app.core.parser.html_parser import PageParser
from app.core.parser.tokenizer import Tokenizer
from app.core.index.writer import IndexWriter
from app.core.ranking.pagerank import LinkGraph

logger = logging.getLogger(__name__)


class WebCrawler:
    """
    Asynchronous web crawler with politeness rules, deduplication,
    link graph extraction, and direct pipeline integration with the indexer.
    """

    def __init__(
        self,
        index_writer: Optional[IndexWriter] = None,
        max_depth: int = 2,
        max_pages: int = 50,
        politeness_delay_sec: float = 0.2,
        user_agent: str = "IndexiumCrawler/1.0",
    ):
        self.max_depth = max_depth
        self.max_pages = max_pages
        self.scheduler = CrawlScheduler(politeness_delay_sec=politeness_delay_sec)
        self.deduplicator = Deduplicator()
        self.robots = RobotsManager(user_agent=user_agent)
        self.parser = PageParser()
        self.tokenizer = Tokenizer()
        self.index_writer = index_writer
        self.link_graph = LinkGraph()
        self.crawled_documents: List[Dict[str, Any]] = []
        self._doc_counter = 1

    def seed(self, urls: List[str]):
        """Seed the crawler frontier."""
        for url in urls:
            self.scheduler.push(url, priority=1, depth=0)

    async def crawl(
        self,
        on_document_indexed: Optional[Callable[[Dict[str, Any]], None]] = None,
    ) -> List[Dict[str, Any]]:
        """Main async crawl loop."""
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            while not self.scheduler.is_empty() and len(self.crawled_documents) < self.max_pages:
                item = self.scheduler.pop()
                if not item:
                    break
                url, depth = item

                if self.deduplicator.is_url_seen(url):
                    continue

                if not self.robots.is_allowed(url):
                    logger.info(f"Disallowed by robots.txt: {url}")
                    continue

                try:
                    self.scheduler.wait_if_needed(url)
                    response = await client.get(url, headers={"User-Agent": self.robots.user_agent})
                    if response.status_code != 200 or "text/html" not in response.headers.get("content-type", ""):
                        continue

                    html = response.text
                    parsed = self.parser.parse(html, base_url=str(response.url))
                    body_tokens = self.tokenizer.tokenize(parsed["body"])

                    if self.deduplicator.is_content_duplicate(parsed["body"]):
                        continue

                    doc_id = self._doc_counter
                    self._doc_counter += 1

                    self.deduplicator.record_document(str(response.url), parsed["body"], body_tokens, doc_id)
                    self.link_graph.add_node(str(response.url))

                    # Track outbound links for the PageRank link graph
                    for outlink in parsed["links"]:
                        self.link_graph.add_edge(str(response.url), outlink)
                        if depth + 1 <= self.max_depth and not self.deduplicator.is_url_seen(outlink):
                            self.scheduler.push(outlink, priority=depth + 2, depth=depth + 1)

                    doc_record = {
                        "id": doc_id,
                        "url": str(response.url),
                        "title": parsed["title"],
                        "body": parsed["body"],
                        "headings": parsed["headings"],
                        "links_count": len(parsed["links"]),
                    }
                    self.crawled_documents.append(doc_record)

                    # Ingest into the inverted index
                    if self.index_writer:
                        full_searchable_text = f"{parsed['title']} {' '.join(parsed['headings'])} {parsed['body']}"
                        self.index_writer.add_document(
                            doc_id=doc_id,
                            text=full_searchable_text,
                            metadata={
                                "url": str(response.url),
                                "title": parsed["title"],
                                "body": parsed["body"],
                            },
                        )

                    if on_document_indexed:
                        on_document_indexed(doc_record)

                except Exception as e:
                    logger.warning(f"Failed to crawl {url}: {e}")

        return self.crawled_documents
