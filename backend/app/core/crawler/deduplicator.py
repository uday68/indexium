from typing import Set, Dict, List
from app.utils.hashing import sha256_hash, simhash, hamming_distance
from app.core.parser.normalizer import normalize_url


class Deduplicator:
    """Detects duplicate URLs and near-duplicate document contents."""

    def __init__(self, simhash_threshold: int = 3):
        self.seen_urls: Set[str] = set()
        self.seen_content_hashes: Set[str] = set()
        # simhash fingerprint -> doc_id
        self.simhashes: Dict[int, int] = {}
        self.simhash_threshold = simhash_threshold

    def is_url_seen(self, url: str) -> bool:
        norm_url = normalize_url(url)
        return norm_url in self.seen_urls

    def mark_url_seen(self, url: str):
        norm_url = normalize_url(url)
        self.seen_urls.add(norm_url)

    def is_content_duplicate(self, text: str) -> bool:
        c_hash = sha256_hash(text)
        return c_hash in self.seen_content_hashes

    def is_near_duplicate(self, tokens: List[str]) -> bool:
        if not tokens:
            return False
        sh = simhash(tokens)
        for existing_sh in self.simhashes.keys():
            if hamming_distance(sh, existing_sh) <= self.simhash_threshold:
                return True
        return False

    def record_document(self, url: str, text: str, tokens: List[str], doc_id: int):
        self.mark_url_seen(url)
        self.seen_content_hashes.add(sha256_hash(text))
        if tokens:
            sh = simhash(tokens)
            self.simhashes[sh] = doc_id
