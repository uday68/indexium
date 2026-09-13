import type { FC } from "react";
import type { SearchResultItem } from "./hooks/useSearch";
import { ExternalLink, Info } from "lucide-react";

interface Props {
  results: SearchResultItem[];
  totalHits: number;
  executionTimeMs: number;
  suggestion?: string | null;
  onSelectSuggestion?: (s: string) => void;
  onExplainDoc: (docId: number) => void;
  onResultClick: (docId: number) => void;
}

export const SearchResults: FC<Props> = ({
  results,
  totalHits,
  executionTimeMs,
  suggestion,
  onSelectSuggestion,
  onExplainDoc,
  onResultClick,
}) => {
  return (
    <div className="w-full max-w-2xl mx-auto mt-6 text-left">
      {/* Stats bar */}
      <div className="text-xs text-zinc-500 mb-4 flex items-center justify-between border-b border-zinc-200 dark:border-zinc-800 pb-2">
        <span>
          About {totalHits} results ({executionTimeMs} ms)
        </span>
      </div>

      {/* Did you mean suggestion */}
      {suggestion && (
        <div className="mb-4 text-sm text-red-500">
          Did you mean:{" "}
          <button
            onClick={() => onSelectSuggestion && onSelectSuggestion(suggestion)}
            className="text-blue-600 hover:underline font-semibold"
          >
            {suggestion}
          </button>
          ?
        </div>
      )}

      {/* No results message */}
      {results.length === 0 && !suggestion && (
        <div className="text-zinc-500 text-center py-12">
          <p className="text-base font-medium">No matching documents found.</p>
          <p className="text-sm mt-1 text-zinc-400">
            Try broader keywords or search for "search engine", "inverted index", or "pagerank".
          </p>
        </div>
      )}

      {/* Result Cards */}
      <div className="space-y-6">
        {results.map((item) => (
          <div key={item.doc_id} className="group">
            <div className="flex items-center gap-2 text-xs text-zinc-500 mb-1">
              <span className="truncate max-w-md">{item.url}</span>
              <span className="bg-zinc-100 dark:bg-zinc-800 px-2 py-0.5 rounded text-[10px] font-mono font-medium text-zinc-600 dark:text-zinc-400">
                score: {item.score.toFixed(3)}
              </span>
            </div>

            <h3 className="text-lg font-medium text-blue-600 dark:text-blue-400 group-hover:underline flex items-center gap-1.5">
              <a
                href={item.url}
                target="_blank"
                rel="noreferrer"
                onClick={() => onResultClick(item.doc_id)}
              >
                {item.title}
              </a>
              <ExternalLink className="w-3.5 h-3.5 opacity-0 group-hover:opacity-100 transition-opacity text-zinc-400" />
            </h3>

            {/* Snippet with highlighted bold HTML */}
            <p
              className="text-sm text-zinc-600 dark:text-zinc-300 mt-1 line-clamp-3 leading-relaxed [&>b]:font-bold [&>b]:text-zinc-900 dark:[&>b]:text-zinc-100"
              dangerouslySetInnerHTML={{ __html: item.snippet }}
            />

            {/* Explain Score Button */}
            <div className="mt-2">
              <button
                onClick={() => onExplainDoc(item.doc_id)}
                className="inline-flex items-center gap-1 text-xs text-zinc-400 hover:text-blue-500 transition-colors"
              >
                <Info className="w-3 h-3" />
                Why this result?
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
