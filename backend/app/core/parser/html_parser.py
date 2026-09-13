from html.parser import HTMLParser
from typing import Dict, List, Set, Any
from app.core.parser.normalizer import normalize_url, normalize_text


class _InternalHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title_parts: List[str] = []
        self.in_title = False
        
        self.body_parts: List[str] = []
        self.in_ignored_tag = False
        self.ignored_tags = {"script", "style", "noscript", "svg", "canvas", "iframe"}
        
        self.headings: List[str] = []
        self.in_heading = False
        self.current_heading: List[str] = []
        
        self.meta_description: str = ""
        self.meta_keywords: str = ""
        
        self.links: Set[str] = set()

    def handle_starttag(self, tag: str, attrs: List[tuple]):
        attr_dict = {k.lower(): (v or "") for k, v in attrs}
        tag = tag.lower()

        if tag in self.ignored_tags:
            self.in_ignored_tag = True
            return

        if tag == "title":
            self.in_title = True
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.in_heading = True
            self.current_heading = []
        elif tag == "meta":
            name = attr_dict.get("name", "").lower()
            content = attr_dict.get("content", "")
            if name == "description":
                self.meta_description = content
            elif name == "keywords":
                self.meta_keywords = content
        elif tag == "a":
            href = attr_dict.get("href", "").strip()
            if href and not href.startswith("javascript:") and not href.startswith("mailto:"):
                self.links.add(href)

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if tag in self.ignored_tags:
            self.in_ignored_tag = False
        elif tag == "title":
            self.in_title = False
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.in_heading = False
            heading_text = " ".join(self.current_heading).strip()
            if heading_text:
                self.headings.append(heading_text)
            self.current_heading = []

    def handle_data(self, data: str):
        if self.in_ignored_tag:
            return
        clean_data = data.strip()
        if not clean_data:
            return
        
        if self.in_title:
            self.title_parts.append(clean_data)
        elif self.in_heading:
            self.current_heading.append(clean_data)
            self.body_parts.append(clean_data)
        else:
            self.body_parts.append(clean_data)


class PageParser:
    """Parses raw HTML into structured page data: title, content, links, and headings."""

    def parse(self, html: str, base_url: str = "") -> Dict[str, Any]:
        parser = _InternalHTMLParser()
        try:
            parser.feed(html)
        except Exception:
            pass  # Resilient to malformed HTML

        title = " ".join(parser.title_parts).strip()
        body_text = normalize_text(" ".join(parser.body_parts))
        
        # Resolve links against base URL
        resolved_links = []
        for raw_link in parser.links:
            norm_link = normalize_url(raw_link, base_url=base_url)
            if norm_link and norm_link.startswith(("http://", "https://")):
                resolved_links.append(norm_link)

        return {
            "title": title or "Untitled Document",
            "body": body_text,
            "headings": parser.headings,
            "description": parser.meta_description,
            "keywords": parser.meta_keywords,
            "links": sorted(list(set(resolved_links))),
        }
