import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings
from app.config.logging import setup_app_logging
from app.core.observability.tracing import set_current_trace_id, generate_trace_id
from app.db.session import init_db
from app.services.index_service import index_service
from app.services.search_service import search_service
from app.api.v1.search import router as search_router
from app.api.v1.explain import router as explain_router
from app.api.v1.stats import router as stats_router
from app.api.v1.admin import router as admin_router

setup_app_logging()


def seed_default_corpus():
    """Seed initial high-quality technical corpus if index is empty."""
    if index_service.index.total_documents > 0:
        return

    sample_docs = [
        (
            1,
            "Introduction to Search Engines and Web Crawling",
            "A search engine is an information retrieval system designed to help find information stored on a computer system. Web crawlers systematically browse the World Wide Web for indexing.",
            "https://en.wikipedia.org/wiki/Search_engine",
        ),
        (
            2,
            "Inverted Index Data Structure",
            "An inverted index is a database index storing a mapping from content, such as words or numbers, to its locations in a document or a set of documents. It allows very fast full-text searches.",
            "https://en.wikipedia.org/wiki/Inverted_index",
        ),
        (
            3,
            "The PageRank Algorithm and Link Analysis",
            "PageRank is an algorithm used by Google Search to rank web pages in their search engine results. It works by counting the number and quality of links to a page to determine an estimate of how important the website is.",
            "https://en.wikipedia.org/wiki/PageRank",
        ),
        (
            4,
            "Okapi BM25 Ranking Function",
            "BM25 is a ranking function used by search engines to estimate the relevance of documents to a given search query. It is based on the probabilistic retrieval framework developed in the 1970s and 1980s by Stephen Robertson, Karen Sparck Jones, and others.",
            "https://en.wikipedia.org/wiki/Okapi_BM25",
        ),
        (
            5,
            "Distributed Systems and Query Processing",
            "Modern distributed search engines shard inverted index partitions across hundreds of server nodes to support high query throughput and low latency query execution at scale.",
            "https://en.wikipedia.org/wiki/Distributed_computing",
        ),
        (
            6,
            "Natural Language Processing and Tokenization",
            "Tokenization is the process of breaking a stream of textual documents into words, phrases, symbols, or other meaningful elements called tokens.",
            "https://en.wikipedia.org/wiki/Lexical_analysis",
        ),
    ]

    for doc_id, title, body, url in sample_docs:
        index_service.add_document(doc_id=doc_id, title=title, body=body, url=url)

    index_service.save_index()
    search_service._refresh_autocomplete()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()
    seed_default_corpus()
    yield
    # Shutdown


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Indexium: Production-Grade Google Page Indexing and Search Engine Replication",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def trace_and_timing_middleware(request: Request, call_next):
    trace_id = request.headers.get("X-Trace-Id", generate_trace_id())
    set_current_trace_id(trace_id)
    start_time = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start_time) * 1000
    response.headers["X-Trace-Id"] = trace_id
    response.headers["X-Response-Time-Ms"] = str(round(duration_ms, 2))
    return response


# Mount API V1 routers
app.include_router(search_router, prefix=settings.API_V1_PREFIX)
app.include_router(explain_router, prefix=settings.API_V1_PREFIX)
app.include_router(stats_router, prefix=settings.API_V1_PREFIX)
app.include_router(admin_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
def root():
    return {
        "project": "Indexium",
        "status": "online",
        "docs_url": "/docs",
        "api_v1": settings.API_V1_PREFIX,
    }


@app.get("/health")
def health():
    return {"status": "healthy", "indexed_documents": index_service.index.total_documents}
