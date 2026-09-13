import { useState, useCallback, useEffect } from "react";
import type { FormEvent } from "react";

export interface SearchResultItem {
  doc_id: number;
  score: number;
  title: string;
  url: string;
  snippet: string;
  explanation?: any;
}

export interface ScoreExplanation {
  doc_id: number;
  final_score: number;
  ranker_name: string;
  term_scores?: Array<{
    term: string;
    tf: number;
    idf: number;
    contribution: number;
  }>;
  additional_factors?: Record<string, number>;
  details?: string;
}

const API_BASE = "http://localhost:8000/api/v1";

export const useSearch = () => {
  const [query, setQuery] = useState("");
  const [ranker, setRanker] = useState("bm25");
  const [results, setResults] = useState<SearchResultItem[]>([]);
  const [totalHits, setTotalHits] = useState(0);
  const [executionTimeMs, setExecutionTimeMs] = useState(0);
  const [suggestion, setSuggestion] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Autocomplete
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Explain modal
  const [selectedExplain, setSelectedExplain] = useState<ScoreExplanation | null>(null);
  const [explainLoading, setExplainLoading] = useState(false);

  const executeSearch = useCallback(
    async (searchQuery?: string, selectedRanker?: string) => {
      const q = (searchQuery ?? query).trim();
      const r = selectedRanker ?? ranker;
      if (!q) return;

      setLoading(true);
      setError(null);
      setShowSuggestions(false);

      try {
        const url = `${API_BASE}/search?q=${encodeURIComponent(q)}&ranker=${encodeURIComponent(r)}&limit=10&explain=true`;
        const res = await fetch(url);
        if (!res.ok) {
          throw new Error(`Server returned ${res.status}: ${res.statusText}`);
        }
        const data = await res.json();
        setResults(data.results || []);
        setTotalHits(data.total_hits || 0);
        setExecutionTimeMs(data.execution_time_ms || 0);
        setSuggestion(data.suggestion || null);
      } catch (err: any) {
        setError(err.message || "Failed to fetch search results.");
        setResults([]);
      } finally {
        setLoading(false);
      }
    },
    [query, ranker]
  );

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    executeSearch();
  };

  // Autocomplete fetch on query change
  useEffect(() => {
    const trimmed = query.trim();
    if (trimmed.length < 2) {
      setSuggestions([]);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const res = await fetch(
          `${API_BASE}/search/autocomplete?prefix=${encodeURIComponent(trimmed)}&limit=5`
        );
        if (res.ok) {
          const data = await res.json();
          setSuggestions(data);
          setShowSuggestions(true);
        }
      } catch {
        setSuggestions([]);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [query]);

  const fetchExplain = async (docId: number) => {
    setExplainLoading(true);
    try {
      const url = `${API_BASE}/explain?q=${encodeURIComponent(query)}&doc_id=${docId}&ranker=${encodeURIComponent(ranker)}`;
      const res = await fetch(url);
      if (res.ok) {
        const data = await res.json();
        setSelectedExplain(data);
      }
    } catch {
      setSelectedExplain(null);
    } finally {
      setExplainLoading(false);
    }
  };

  const recordClick = async (docId: number) => {
    try {
      await fetch(`${API_BASE}/search/click`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, doc_id: docId }),
      });
    } catch {
      // Telemetry best-effort
    }
  };

  return {
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
    explainLoading,
    executeSearch,
    handleSubmit,
    fetchExplain,
    recordClick,
  };
};