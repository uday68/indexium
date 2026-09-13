import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.services.index_service import index_service
from app.services.search_service import search_service

SAMPLE_CORPUS = [
    {
        "id": 1,
        "title": "Google Search Architecture Overview",
        "url": "https://google.com/search-architecture",
        "body": "The Google search engine architecture features crawling spiders like Googlebot, an indexer that produces inverted index postings, and ranking models incorporating PageRank link authority.",
    },
    {
        "id": 2,
        "title": "Inverted Index and Posting Compression",
        "url": "https://nlp.stanford.edu/IR-book/html/htmledition/an-inverted-index-1.html",
        "body": "An inverted index consists of a dictionary of terms and posting lists. For each term, the list records the document IDs and term positions. Techniques like delta encoding and variable-byte compression minimize memory footprints.",
    },
    {
        "id": 3,
        "title": "PageRank Link Analysis Algorithm",
        "url": "https://infolab.stanford.edu/~backrub/google.html",
        "body": "PageRank interprets a hyperlink from page A to page B as a vote by page A for page B. Votes cast by pages that are themselves important weigh more heavily and decide the ranking order of search results.",
    },
    {
        "id": 4,
        "title": "Probabilistic Relevance and BM25",
        "url": "https://en.wikipedia.org/wiki/Okapi_BM25",
        "body": "BM25 balances term frequency and document length saturation. It prevents long documents with repeated keywords from dominating query relevance scores.",
    },
    {
        "id": 5,
        "title": "Web Crawling and Politeness Policies",
        "url": "https://en.wikipedia.org/wiki/Web_crawler",
        "body": "Polite crawlers respect robots.txt rules, implement per-host request rate limits, and use URL deduplication to avoid crawl traps and duplicate indexing.",
    },
    {
        "id": 6,
        "title": "Query Parsing and Boolean Information Retrieval",
        "url": "https://en.wikipedia.org/wiki/Boolean_model_of_information_retrieval",
        "body": "Boolean queries with AND, OR, and NOT operators execute set intersections and unions across posting lists to evaluate matching documents.",
    },
    {
        "id": 7,
        "title": "Distributed Inverted Index Sharding",
        "url": "https://en.wikipedia.org/wiki/Shard_(database_architecture)",
        "body": "Sharding distributes document collections across multiple cluster nodes. Scatter-gather executors send queries to all shards in parallel and merge the top scored candidates.",
    },
]


def seed():
    print(f"Seeding {len(SAMPLE_CORPUS)} sample documents into Indexium...")
    for doc in SAMPLE_CORPUS:
        index_service.add_document(
            doc_id=doc["id"],
            title=doc["title"],
            body=doc["body"],
            url=doc["url"],
        )
    index_service.save_index()
    search_service._refresh_autocomplete()
    print(f"Index successfully seeded! Total documents in index: {index_service.index.total_documents}")
    print(f"Vocabulary size: {index_service.index.vocabulary_size} terms")


if __name__ == "__main__":
    seed()
