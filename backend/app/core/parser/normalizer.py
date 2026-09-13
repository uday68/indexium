import re
import unicodedata
from urllib.parse import urlparse, urlunparse, urljoin


def normalize_text(text: str) -> str:
    """
    Standardize text:
    - Unicode NFKD decomposition
    - Case folding to lowercase
    - Normalizing whitespace
    """
    if not text:
        return ""
    text = unicodedata.normalize("NFKD", text)
    text = text.lower()
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def normalize_url(url: str, base_url: str = "") -> str:
    """
    Standardize URL:
    - Resolve relative paths against base_url
    - Remove tracking fragments (#...)
    - Lowercase scheme and netloc
    - Strip trailing slashes unless root
    """
    if not url:
        return ""
    if base_url:
        url = urljoin(base_url, url)
    
    parsed = urlparse(url)
    scheme = parsed.scheme.lower() if parsed.scheme else "http"
    netloc = parsed.netloc.lower()
    path = parsed.path
    if path.endswith("/") and len(path) > 1:
        path = path.rstrip("/")
    if not path:
        path = "/"
    
    # Keep query parameters, discard fragment
    clean_url = urlunparse((scheme, netloc, path, parsed.params, parsed.query, ""))
    return clean_url
