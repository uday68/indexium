import re
from typing import List, Tuple
from app.utils.text import STOPWORDS, normalize_text

_TOKEN_REGEX = re.compile(r"\b[a-z0-9]+(?:'[a-z0-9]+)?\b")


class Tokenizer:
    def __init__(self, remove_stopwords: bool = True, min_length: int = 2, max_length: int = 40):
        self.remove_stopwords = remove_stopwords
        self.min_length = min_length
        self.max_length = max_length

    def tokenize(self, text: str) -> List[str]:
        """Convert input text into a list of cleaned tokens."""
        normalized = normalize_text(text)
        raw_tokens = _TOKEN_REGEX.findall(normalized)
        tokens: List[str] = []
        for t in raw_tokens:
            if len(t) < self.min_length or len(t) > self.max_length:
                continue
            if self.remove_stopwords and t in STOPWORDS:
                continue
            tokens.append(t)
        return tokens

    def tokenize_with_positions(self, text: str) -> List[Tuple[str, int]]:
        """
        Tokenize text and return each token along with its integer position offset.
        Useful for positional inverted indexing and phrase search.
        """
        normalized = normalize_text(text)
        tokens: List[Tuple[str, int]] = []
        pos = 0
        for match in _TOKEN_REGEX.finditer(normalized):
            t = match.group()
            if len(t) < self.min_length or len(t) > self.max_length:
                pos += 1
                continue
            if self.remove_stopwords and t in STOPWORDS:
                pos += 1
                continue
            tokens.append((t, pos))
            pos += 1
        return tokens
