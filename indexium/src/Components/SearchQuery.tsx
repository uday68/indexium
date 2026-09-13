import { useRef, useEffect } from "react";
import type { FC, ChangeEvent, FormEvent } from "react";
import { Input } from "./ui/input";
import { Button } from "./ui/button";
import { Search, X, Loader2 } from "lucide-react";

interface Props {
  query: string;
  setQuery: (q: string) => void;
  ranker: string;
  setRanker: (r: string) => void;
  suggestions: string[];
  showSuggestions: boolean;
  setShowSuggestions: (s: boolean) => void;
  loading: boolean;
  onSearch: (q?: string) => void;
  onSubmit: (e: FormEvent<HTMLFormElement>) => void;
}

export const SearchBar: FC<Props> = ({
  query,
  setQuery,
  ranker,
  setRanker,
  suggestions,
  showSuggestions,
  setShowSuggestions,
  loading,
  onSearch,
  onSubmit,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  const onChange = (e: ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value);
  };

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setShowSuggestions(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [setShowSuggestions]);

  return (
    <div ref={containerRef} className="w-full max-w-2xl mx-auto relative">
      <form onSubmit={onSubmit} className="flex items-center gap-2">
        <div className="relative flex-1">
          <Search className="absolute left-3.5 top-3 h-4 w-4 text-zinc-400" />
          <Input
            type="text"
            value={query}
            onChange={onChange}
            onFocus={() => setShowSuggestions(suggestions.length > 0)}
            placeholder="Search indexed web pages..."
            className="pl-10 pr-10 py-5 text-base rounded-full border-zinc-200 dark:border-zinc-700 shadow-sm focus-visible:ring-2 focus-visible:ring-blue-500"
          />
          {query && (
            <button
              type="button"
              onClick={() => setQuery("")}
              className="absolute right-3.5 top-3 text-zinc-400 hover:text-zinc-600"
            >
              <X className="h-4 w-4" />
            </button>
          )}

          {/* Autocomplete Suggestions Dropdown */}
          {showSuggestions && suggestions.length > 0 && (
            <div className="absolute top-full left-0 right-0 mt-1.5 bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl shadow-lg z-50 overflow-hidden text-left">
              {suggestions.map((s, idx) => (
                <button
                  key={idx}
                  type="button"
                  onClick={() => {
                    setQuery(s);
                    setShowSuggestions(false);
                    onSearch(s);
                  }}
                  className="w-full px-4 py-2.5 text-sm flex items-center gap-2 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-100 dark:hover:bg-zinc-800 transition-colors"
                >
                  <Search className="h-3.5 w-3.5 text-zinc-400" />
                  <span>{s}</span>
                </button>
              ))}
            </div>
          )}
        </div>

        <Button
          type="submit"
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 text-white rounded-full px-6 py-5 shadow-sm font-medium"
        >
          {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : "Search"}
        </Button>
      </form>

      {/* Ranker Selector */}
      <div className="flex items-center justify-center gap-3 mt-3 text-xs">
        <span className="text-zinc-400 font-medium">Ranker:</span>
        {[
          { id: "bm25", label: "BM25" },
          { id: "tfidf", label: "TF-IDF" },
          { id: "pagerank", label: "PageRank (Hybrid)" },
        ].map((r) => (
          <button
            key={r.id}
            type="button"
            onClick={() => setRanker(r.id)}
            className={`px-3 py-1 rounded-full transition-colors ${
              ranker === r.id
                ? "bg-blue-100 text-blue-700 dark:bg-blue-900/50 dark:text-blue-300 font-semibold"
                : "text-zinc-500 hover:bg-zinc-100 dark:hover:bg-zinc-800"
            }`}
          >
            {r.label}
          </button>
        ))}
      </div>
    </div>
  );
};
