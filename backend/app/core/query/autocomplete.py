from typing import List, Dict, Tuple


class TrieNode:
    def __init__(self):
        self.children: Dict[str, "TrieNode"] = {}
        self.is_end_of_word: bool = False
        self.frequency: int = 0
        self.full_word: str = ""


class AutocompleteTrie:
    """Prefix tree (Trie) for real-time query and search suggestions."""

    def __init__(self):
        self.root = TrieNode()

    def insert(self, word: str, frequency: int = 1):
        if not word:
            return
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end_of_word = True
        node.frequency += frequency
        node.full_word = word.lower()

    def search_prefix(self, prefix: str, max_results: int = 5) -> List[str]:
        if not prefix:
            return []

        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return []
            node = node.children[char]

        # Gather words under this node sorted by frequency
        results: List[Tuple[int, str]] = []
        self._dfs(node, results)
        results.sort(key=lambda x: x[0], reverse=True)
        return [word for _, word in results[:max_results]]

    def _dfs(self, node: TrieNode, results: List[Tuple[int, str]]):
        if node.is_end_of_word:
            results.append((node.frequency, node.full_word))
        for child in node.children.values():
            self._dfs(child, results)
