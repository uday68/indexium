import re
from typing import List, Set


class SnippetGenerator:
    """Generates context-rich snippets with highlighted query terms."""

    def __init__(self, max_length: int = 160):
        self.max_length = max_length

    def generate(self, text: str, query_terms: List[str]) -> str:
        if not text:
            return ""
        if not query_terms:
            return text[:self.max_length] + ("..." if len(text) > self.max_length else "")

        terms_set: Set[str] = {t.lower() for t in query_terms if t}
        if not terms_set:
            return text[:self.max_length] + ("..." if len(text) > self.max_length else "")

        # Split text into sentences or approximate chunks
        sentences = re.split(r"(?<=[.!?])\s+", text)
        best_sentence = ""
        max_matches = -1

        for s in sentences:
            s_lower = s.lower()
            matches = sum(1 for term in terms_set if term in s_lower)
            if matches > max_matches:
                max_matches = matches
                best_sentence = s

        target_text = best_sentence if best_sentence else text

        # Truncate if too long
        if len(target_text) > self.max_length:
            # Try to center around the first term match
            earliest_idx = len(target_text)
            for term in terms_set:
                idx = target_text.lower().find(term)
                if idx != -1 and idx < earliest_idx:
                    earliest_idx = idx

            start = max(0, earliest_idx - 40)
            end = min(len(target_text), start + self.max_length)
            snippet_part = target_text[start:end]
            prefix = "..." if start > 0 else ""
            suffix = "..." if end < len(target_text) else ""
            target_text = f"{prefix}{snippet_part}{suffix}"

        # Highlight terms using <b>
        pattern = re.compile(
            r"\b(" + "|".join(re.escape(t) for t in terms_set) + r")\b",
            re.IGNORECASE
        )
        highlighted = pattern.sub(r"<b>\1</b>", target_text)
        return highlighted
