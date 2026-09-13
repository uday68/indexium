from typing import List, Optional, Set
from app.core.index.reader import IndexReader
from app.core.parser.tokenizer import Tokenizer


def levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate the Levenshtein distance between two strings."""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


class QueryRewriter:
    """Provides query expansion and spell-correction suggestions."""

    def __init__(self, tokenizer: Optional[Tokenizer] = None):
        self.tokenizer = tokenizer if tokenizer is not None else Tokenizer()

    def suggest_correction(self, term: str, vocabulary: Set[str], max_distance: int = 2) -> Optional[str]:
        if term in vocabulary:
            return None  # Term is already correct

        best_match = None
        min_dist = max_distance + 1

        for candidate in vocabulary:
            if abs(len(candidate) - len(term)) > max_distance:
                continue
            dist = levenshtein_distance(term, candidate)
            if dist < min_dist:
                min_dist = dist
                best_match = candidate

        return best_match if min_dist <= max_distance else None

    def rewrite_query(self, query: str, reader: IndexReader) -> Optional[str]:
        """Suggests a corrected query string if any term appears misspelled."""
        tokens = self.tokenizer.tokenize(query)
        if not tokens:
            return None

        vocab = set(reader.index.index.keys())
        rewritten_tokens = []
        has_change = False

        for t in tokens:
            suggestion = self.suggest_correction(t, vocab)
            if suggestion:
                rewritten_tokens.append(suggestion)
                has_change = True
            else:
                rewritten_tokens.append(t)

        if has_change:
            return " ".join(rewritten_tokens)
        return None
