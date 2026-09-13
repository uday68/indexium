import { useState } from "react";
import type { FC, FormEvent } from "react";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Globe, PlusCircle, CheckCircle, AlertCircle } from "lucide-react";

interface Props {
  isOpen: boolean;
  onClose: () => void;
  onRefreshStats: () => void;
}

const API_BASE = "http://localhost:8000/api/v1";

export const AdminModal: FC<Props> = ({ isOpen, onClose, onRefreshStats }) => {
  const [crawlUrl, setCrawlUrl] = useState("");
  const [maxPages, setMaxPages] = useState(10);
  const [status, setStatus] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  // Manual Document Addition
  const [docTitle, setDocTitle] = useState("");
  const [docUrl, setDocUrl] = useState("");
  const [docBody, setDocBody] = useState("");

  if (!isOpen) return null;

  const handleCrawl = async (e: FormEvent) => {
    e.preventDefault();
    if (!crawlUrl) return;
    setLoading(true);
    setStatus(null);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/admin/crawl`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ seed_urls: [crawlUrl], max_pages: maxPages }),
      });
      if (!res.ok) throw new Error(await res.text());
      setStatus(`Crawl job started for ${crawlUrl}`);
      setCrawlUrl("");
      setTimeout(onRefreshStats, 3000);
    } catch (err: any) {
      setError(err.message || "Failed to trigger crawl.");
    } finally {
      setLoading(false);
    }
  };

  const handleIndexDoc = async (e: FormEvent) => {
    e.preventDefault();
    if (!docTitle || !docBody) return;
    setLoading(true);
    setStatus(null);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/admin/index`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: docTitle,
          url: docUrl || `https://local.indexium/doc/${Date.now()}`,
          body: docBody,
        }),
      });
      if (!res.ok) throw new Error(await res.text());
      setStatus(`Document "${docTitle}" successfully indexed!`);
      setDocTitle("");
      setDocUrl("");
      setDocBody("");
      onRefreshStats();
    } catch (err: any) {
      setError(err.message || "Failed to index document.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <div className="bg-white dark:bg-zinc-900 border border-zinc-200 dark:border-zinc-800 rounded-xl shadow-2xl max-w-xl w-full p-6 text-zinc-900 dark:text-zinc-100 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center border-b border-zinc-200 dark:border-zinc-800 pb-3 mb-4">
          <div className="flex items-center gap-2">
            <Globe className="w-5 h-5 text-blue-500" />
            <h3 className="font-semibold text-lg">Crawler & Document Indexer</h3>
          </div>
          <button onClick={onClose} className="text-zinc-500 hover:text-zinc-700 text-lg font-bold">
            &times;
          </button>
        </div>

        {status && (
          <div className="flex items-center gap-2 text-sm bg-emerald-50 text-emerald-700 dark:bg-emerald-950/40 dark:text-emerald-300 p-3 rounded-lg border border-emerald-200 dark:border-emerald-900 mb-4">
            <CheckCircle className="w-4 h-4 flex-shrink-0" />
            <span>{status}</span>
          </div>
        )}

        {error && (
          <div className="flex items-center gap-2 text-sm bg-red-50 text-red-700 dark:bg-red-950/40 dark:text-red-300 p-3 rounded-lg border border-red-200 dark:border-red-900 mb-4">
            <AlertCircle className="w-4 h-4 flex-shrink-0" />
            <span>{error}</span>
          </div>
        )}

        {/* 1. Web Crawler Form */}
        <form onSubmit={handleCrawl} className="space-y-3 mb-6">
          <h4 className="font-medium text-sm text-zinc-700 dark:text-zinc-300">
            Crawl Live Web Pages (Googlebot Replication)
          </h4>
          <div className="flex gap-2">
            <Input
              type="url"
              placeholder="https://en.wikipedia.org/wiki/Search_engine"
              value={crawlUrl}
              onChange={(e) => setCrawlUrl(e.target.value)}
              className="flex-1"
            />
            <Input
              type="number"
              placeholder="Pages"
              value={maxPages}
              onChange={(e) => setMaxPages(Number(e.target.value))}
              className="w-20"
              min={1}
              max={50}
            />
            <Button type="submit" disabled={loading} className="bg-blue-600 hover:bg-blue-700 text-white">
              Crawl
            </Button>
          </div>
          <p className="text-xs text-zinc-400">
            The crawler respects robots.txt, computes SimHash fingerprints, and builds link graphs.
          </p>
        </form>

        <hr className="border-zinc-200 dark:border-zinc-800 my-4" />

        {/* 2. Direct Document Ingestion Form */}
        <form onSubmit={handleIndexDoc} className="space-y-3">
          <h4 className="font-medium text-sm text-zinc-700 dark:text-zinc-300 flex items-center gap-1.5">
            <PlusCircle className="w-4 h-4 text-emerald-500" />
            Manually Index a Document
          </h4>
          <Input
            type="text"
            placeholder="Document Title"
            value={docTitle}
            onChange={(e) => setDocTitle(e.target.value)}
            required
          />
          <Input
            type="url"
            placeholder="Document URL (optional)"
            value={docUrl}
            onChange={(e) => setDocUrl(e.target.value)}
          />
          <textarea
            placeholder="Document Content / Body..."
            value={docBody}
            onChange={(e) => setDocBody(e.target.value)}
            rows={4}
            required
            className="w-full text-sm p-3 rounded-lg border border-zinc-200 dark:border-zinc-700 bg-transparent focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
          <div className="flex justify-end">
            <Button type="submit" disabled={loading} className="bg-emerald-600 hover:bg-emerald-700 text-white">
              Index Document
            </Button>
          </div>
        </form>

        <div className="mt-6 flex justify-end">
          <Button onClick={onClose} className="bg-zinc-200 text-zinc-800 hover:bg-zinc-300 dark:bg-zinc-800 dark:text-zinc-200">
            Done
          </Button>
        </div>
      </div>
    </div>
  );
};
