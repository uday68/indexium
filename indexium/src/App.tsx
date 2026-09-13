import { useState, useEffect } from "react";
import type { FormEvent } from "react";
import "./App.css";
import { SearchBar } from "./Components/SearchQuery";
import { SearchResults } from "./Components/SearchResults";
import { ScoreExplainModal } from "./Components/ScoreExplainModal";
import { AdminModal } from "./Components/AdminModal";
import { useSearch } from "./Components/hooks/useSearch";
import { Database, Plus, Sparkles } from "lucide-react";

function App() {
  const {
    query,
    setQuery,
    ranker,
    setRanker,
    results,
    totalHits,
    executionTimeMs,
    suggestion,
    loading,
    error,
    suggestions,
    showSuggestions,
    setShowSuggestions,
    selectedExplain,
    setSelectedExplain,
    executeSearch,
    handleSubmit,
    fetchExplain,
    recordClick,
  } = useSearch();

  const [hasSearched, setHasSearched] = useState(false);
  const [isAdminOpen, setIsAdminOpen] = useState(false);
  const [stats, setStats] = useState<{
    index_documents_total?: number;
    index_vocabulary_total?: number;
    qps?: number;
  }>({});

  const fetchStats = async () => {
    try {
      const res = await fetch("http://localhost:8000/api/v1/stats");
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch {
      // Backend may be starting
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleFormSubmit = (e: FormEvent<HTMLFormElement>) => {
    setHasSearched(true);
    handleSubmit(e);
  };

  const handleSuggestionClick = (s: string) => {
    setQuery(s);
    setHasSearched(true);
    executeSearch(s);
  };

  return (
    <div className="min-h-screen bg-white dark:bg-zinc-950 text-zinc-900 dark:text-zinc-100 flex flex-col justify-between">
      {/* Top Header */}
      <header className="p-4 flex justify-between items-center border-b border-zinc-100 dark:border-zinc-900">
        <div className="flex items-center gap-2 text-sm text-zinc-500 font-medium">
          <Database className="w-4 h-4 text-blue-500" />
          <span>
            {stats.index_documents_total ?? 0} docs indexed &bull; {stats.index_vocabulary_total ?? 0} terms
          </span>
        </div>
        <button
          onClick={() => setIsAdminOpen(true)}
          className="flex items-center gap-1.5 text-xs bg-zinc-100 dark:bg-zinc-800 hover:bg-zinc-200 dark:hover:bg-zinc-700 px-3 py-1.5 rounded-full font-medium transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
          Crawl / Add Data
        </button>
      </header>

      {/* Main Content Area */}
      <main
        className={`flex-1 flex flex-col items-center px-4 transition-all duration-300 ${
          hasSearched ? "pt-8" : "pt-28"
        }`}
      >
        {/* Brand Logo */}
        <div className="mb-8 text-center select-none">
          <h1 className="text-5xl font-extrabold tracking-tight bg-gradient-to-r from-blue-600 via-indigo-600 to-cyan-500 bg-clip-text text-transparent">
            Indexium
          </h1>
          <p className="text-xs text-zinc-400 mt-2 font-medium tracking-wide uppercase flex items-center justify-center gap-1">
            <Sparkles className="w-3.5 h-3.5 text-blue-500" />
            Distributed Page Indexing & Search Engine
          </p>
        </div>

        {/* Search Input Bar */}
        <SearchBar
          query={query}
          setQuery={setQuery}
          ranker={ranker}
          setRanker={(r) => {
            setRanker(r);
            if (hasSearched) executeSearch(query, r);
          }}
          suggestions={suggestions}
          showSuggestions={showSuggestions}
          setShowSuggestions={setShowSuggestions}
          loading={loading}
          onSearch={(q) => {
            setHasSearched(true);
            executeSearch(q);
          }}
          onSubmit={handleFormSubmit}
        />

        {/* Error notification */}
        {error && (
          <div className="mt-4 p-3 text-sm text-red-600 bg-red-50 dark:bg-red-950/40 rounded-lg max-w-lg text-center">
            {error}
          </div>
        )}

        {/* Search Results List */}
        {hasSearched && (
          <SearchResults
            results={results}
            totalHits={totalHits}
            executionTimeMs={executionTimeMs}
            suggestion={suggestion}
            onSelectSuggestion={handleSuggestionClick}
            onExplainDoc={(docId) => fetchExplain(docId)}
            onResultClick={(docId) => recordClick(docId)}
          />
        )}
      </main>

      {/* Footer */}
      <footer className="py-4 text-center text-xs text-zinc-400 border-t border-zinc-100 dark:border-zinc-900 mt-12">
        <p>Indexium &bull; Google Page Indexing Replication &bull; BM25 / TF-IDF / PageRank Hybrid</p>
      </footer>

      {/* Score Explanation Modal */}
      <ScoreExplainModal
        explanation={selectedExplain}
        onClose={() => setSelectedExplain(null)}
      />

      {/* Crawler / Indexer Modal */}
      <AdminModal
        isOpen={isAdminOpen}
        onClose={() => setIsAdminOpen(false)}
        onRefreshStats={fetchStats}
      />
    </div>
  );
}

export default App;
