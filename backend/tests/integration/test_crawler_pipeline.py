import pytest
from app.core.crawler.deduplicator import Deduplicator
from app.core.crawler.scheduler import CrawlScheduler
from app.core.crawler.robots import RobotsManager


def test_crawler_deduplication():
    dedup = Deduplicator()
    assert not dedup.is_url_seen("https://example.com/page1")
    dedup.mark_url_seen("https://example.com/page1")
    assert dedup.is_url_seen("https://example.com/page1")

    # Content duplicate
    content = "Sample web document content about search engines."
    assert not dedup.is_content_duplicate(content)
    dedup.record_document("https://example.com/page1", content, ["search", "engines"], 1)
    assert dedup.is_content_duplicate(content)


def test_crawler_scheduler():
    scheduler = CrawlScheduler(politeness_delay_sec=0.01)
    scheduler.push("https://example.com/high", priority=1, depth=0)
    scheduler.push("https://example.com/low", priority=5, depth=1)

    url, depth = scheduler.pop()
    assert url == "https://example.com/high"
    assert depth == 0
