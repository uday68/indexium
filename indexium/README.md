# Indexium Frontend — Interactive Search Interface

Modern, responsive web interface for the **Indexium Search & Google Page Indexing Engine**, built with React 19, TypeScript, Vite, and Tailwind CSS.

---

## Features

- **Google-Style Search Engine UI**: Minimalist search layout with animated transitions between hero state and search results view.
- **Prefix Autocomplete**: Real-time keystroke suggestions powered by the backend's Prefix Trie engine.
- **Dynamic Ranker Selection**: Instant switching between **BM25**, **TF-IDF**, and **PageRank (Hybrid)** ranking algorithms to compare search relevance.
- **Context Snippets**: Displays matched sentences with highlighted bold query keywords (`<b>...</b>`).
- **Explainability Modal**: Detailed mathematical score breakdowns showing individual term contributions, TF, IDF, and document length normalization factors.
- **Crawler & Indexer Controller**: In-browser modal to trigger live web crawling jobs or manually index documents.
- **Live System Telemetry**: Header displaying real-time total indexed documents, vocabulary size, and latency statistics.

---

## Getting Started

### Prerequisites
- Node.js 18+
- npm 9+

### Installation & Development

```bash
# Install dependencies
npm install

# Start development server (with HMR)
npm run dev
```

Visit `http://localhost:5173` to access the search interface.

### Production Build

```bash
# Type-check and build production bundle
npm run build

# Preview production build locally
npm run preview
```

---

## Project Structure

```
src/
├── App.tsx                      # Root application coordinating state, search, and modals
├── Components/
│   ├── SearchQuery.tsx          # Search bar with autocomplete dropdown and ranker toggle pills
│   ├── SearchResults.tsx        # Ranked results list with highlighted snippets and score chips
│   ├── ScoreExplainModal.tsx    # Ranking score breakdown modal
│   ├── AdminModal.tsx           # Web crawler and document indexing modal
│   ├── hooks/
│   │   └── useSearch.ts         # Search state, autocomplete debouncing, and API integration
│   └── ui/                      # Reusable UI component library (Button, Input)
└── main.tsx                     # React entrypoint
```
