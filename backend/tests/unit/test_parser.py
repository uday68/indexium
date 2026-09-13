from app.core.parser.tokenizer import Tokenizer
from app.core.parser.normalizer import normalize_text, normalize_url
from app.core.parser.html_parser import PageParser
from app.core.parser.snippet import SnippetGenerator
from app.core.query.parser import QueryParser


def test_normalizer():
    assert normalize_text("  Hello   WORLD!\n\t") == "hello world!"
    assert normalize_url("about.html", base_url="https://example.com/page/") == "https://example.com/page/about.html"
    assert normalize_url("https://example.com/test/#fragment") == "https://example.com/test"


def test_tokenizer():
    tokenizer = Tokenizer(remove_stopwords=True)
    tokens = tokenizer.tokenize("The quick brown fox jumps over the lazy dog.")
    assert "the" not in tokens
    assert "quick" in tokens
    assert "fox" in tokens

    pos_tokens = tokenizer.tokenize_with_positions("Search engine indexing")
    assert len(pos_tokens) == 3
    assert pos_tokens[0] == ("search", 0)


def test_html_parser():
    html = """
    <html>
      <head><title>Test Page Title</title></head>
      <body>
        <h1>Main Header</h1>
        <p>This is a paragraph with <a href="/subpage">a link</a>.</p>
        <script>var x = 10;</script>
      </body>
    </html>
    """
    parser = PageParser()
    parsed = parser.parse(html, base_url="https://test.org")
    assert parsed["title"] == "Test Page Title"
    assert "main header" in parsed["body"]
    assert "var x" not in parsed["body"]  # script ignored
    assert "https://test.org/subpage" in parsed["links"]


def test_snippet_generator():
    text = "Information retrieval is the science of searching for information in a document. Modern search engines index billions of pages."
    generator = SnippetGenerator(max_length=80)
    snippet = generator.generate(text, ["search", "engines"])
    assert "<b>search</b>" in snippet.lower()
    assert "<b>engines</b>" in snippet.lower()


def test_query_parser():
    parser = QueryParser()
    res = parser.parse('"inverted index" +ranking -crawler')
    assert ["inverted", "index"] in res.phrases
    assert "ranking" in res.must_have_terms
    assert "crawler" in res.must_not_terms
