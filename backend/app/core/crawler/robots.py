import urllib.robotparser
from urllib.parse import urlparse, urljoin
from typing import Dict, Optional


class RobotsManager:
    """Fetches, caches, and verifies compliance with site robots.txt policies."""

    def __init__(self, user_agent: str = "IndexiumBot/1.0"):
        self.user_agent = user_agent
        self._parsers: Dict[str, urllib.robotparser.RobotFileParser] = {}

    def get_robots_url(self, url: str) -> str:
        parsed = urlparse(url)
        return urljoin(f"{parsed.scheme}://{parsed.netloc}", "/robots.txt")

    def is_allowed(self, url: str) -> bool:
        """Check whether the given URL is permissible under robots.txt."""
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"

        if domain not in self._parsers:
            rp = urllib.robotparser.RobotFileParser()
            robots_url = self.get_robots_url(url)
            rp.set_url(robots_url)
            try:
                rp.read()
            except Exception:
                # If robots.txt cannot be fetched or parsed, default to allowing
                rp.allow_all = True
            self._parsers[domain] = rp

        parser = self._parsers[domain]
        try:
            return parser.can_fetch(self.user_agent, url)
        except Exception:
            return True
