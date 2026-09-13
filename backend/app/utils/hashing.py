import hashlib
from typing import List, Iterable


def sha256_hash(text: str) -> str:
    """Return hex sha256 of text."""
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def md5_hash(text: str) -> str:
    """Return hex md5 of text."""
    return hashlib.md5(text.encode("utf-8", errors="ignore")).hexdigest()


def simhash(tokens: Iterable[str], hash_bits: int = 64) -> int:
    """
    Calculate 64-bit SimHash fingerprint of a token stream for near-duplicate detection.
    """
    v = [0] * hash_bits
    for token in tokens:
        h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
        for i in range(hash_bits):
            bit = (h >> i) & 1
            if bit == 1:
                v[i] += 1
            else:
                v[i] -= 1
    
    fingerprint = 0
    for i in range(hash_bits):
        if v[i] > 0:
            fingerprint |= (1 << i)
    return fingerprint


def hamming_distance(h1: int, h2: int) -> int:
    """Calculate hamming distance between two integers (number of differing bits)."""
    x = h1 ^ h2
    return bin(x).count("1")
