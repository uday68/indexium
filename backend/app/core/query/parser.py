import re
from dataclasses import dataclass, field
from typing import List, Set
from app.core.parser.tokenizer import Tokenizer


@dataclass
class ParsedQuery:
    raw_query: str
    terms: List[str] = field(default_factory=list)
    phrases: List[List[str]] = field(default_factory=list)
    must_have_terms: Set[str] = field(default_factory=set)
    must_not_terms: Set[str] = field(default_factory=set)
    should_terms: Set[str] = field(default_factory=set)


class QueryParser:
    """Parses user search query strings into terms, phrases, and boolean constraints."""

    def __init__(self, tokenizer: Tokenizer = None):
        self.tokenizer = tokenizer if tokenizer is not None else Tokenizer()

    def parse(self, query_str: str) -> ParsedQuery:
        if not query_str:
            return ParsedQuery(raw_query="")

        raw = query_str.strip()
        parsed = ParsedQuery(raw_query=raw)

        # 1. Extract quoted phrases: "search engine"
        phrase_matches = re.findall(r'"([^"]+)"', raw)
        for p in phrase_matches:
            phrase_tokens = self.tokenizer.tokenize(p)
            if phrase_tokens:
                parsed.phrases.append(phrase_tokens)

        # Remove quoted phrases from raw query for remaining token processing
        unquoted = re.sub(r'"[^"]+"', " ", raw)

        # 2. Extract boolean or tagged terms: +term, -term, NOT term, OR term
        words = unquoted.split()
        i = 0
        while i < len(words):
            word = words[i]
            upper_word = word.upper()

            if upper_word == "NOT" and i + 1 < len(words):
                neg_tokens = self.tokenizer.tokenize(words[i + 1])
                parsed.must_not_terms.update(neg_tokens)
                i += 2
                continue
            elif upper_word == "AND":
                i += 1
                continue
            elif upper_word == "OR":
                i += 1
                continue
            elif word.startswith("-") and len(word) > 1:
                neg_tokens = self.tokenizer.tokenize(word[1:])
                parsed.must_not_terms.update(neg_tokens)
            elif word.startswith("+") and len(word) > 1:
                pos_tokens = self.tokenizer.tokenize(word[1:])
                parsed.must_have_terms.update(pos_tokens)
                parsed.terms.extend(pos_tokens)
            else:
                tokens = self.tokenizer.tokenize(word)
                parsed.should_terms.update(tokens)
                parsed.terms.extend(tokens)
            i += 1

        # Also add phrase tokens to main terms list if not present
        for phrase in parsed.phrases:
            for pt in phrase:
                if pt not in parsed.terms:
                    parsed.terms.append(pt)

        return parsed
