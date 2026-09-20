# Indexium Frontend

React frontend for the **Indexium Search & Google Page Indexing Engine**. The application provides a Google-style search experience backed by the Indexium FastAPI service, including autocomplete, multiple ranking strategies, score explanations, document indexing, and web crawling controls.

## Features

- **Google-style search interface** with responsive landing and results views.
- **Autocomplete suggestions** powered by the backend prefix-trie endpoint.
- **Multiple ranking modes**: BM25, TF-IDF, and PageRank (Hybrid).
- **Highlighted result snippets** rendered from backend-generated HTML snippets.
- **Ranking explanations** showing ranker metadata, term frequency, IDF, term contributions, and additional factors.
- **Crawler controls** for starting a crawl with a seed URL and page limit.
- **Manual document indexing** directly from the browser.
- **Live index telemetry** showing indexed document and vocabulary totals.
- **Click telemetry** sent when a result is opened.
- **Tailwind CSS styling** with reusable UI primitives and Lucide icons.

## Tech Stack

- React 19
- TypeScript 5.9
- Vite with the Rolldown Vite distribution
- Tailwind CSS 4
- Lucide React
- ESLint 9

## Prerequisites

- Node.js 18 or later
- npm 9 or later
- The Indexium backend running locally on `http://localhost:8000`

## Getting Started

From the repository root:

```bash
cd indexium
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

The frontend currently expects the backend API at:

```text
http://localhost:8000/api/v1
```

Start the backend from the repository's `backend` directory according to [`backend/README.md`](../backend/README.md).

## Available Scripts

```bash
npm run dev       # Start the Vite development server with HMR
npm run build     # Type-check and create a production build
npm run lint      # Run ESLint
npm run preview   # Preview the production build locally
```

## Backend API Integration

The frontend communicates with these backend routes:

| Capability | Endpoint | Method |
|---|---|---|
| Search | `/api/v1/search` | `GET` |
| Autocomplete | `/api/v1/search/autocomplete` | `GET` |
| Ranking explanation | `/api/v1/explain` | `GET` |
| Index telemetry | `/api/v1/stats` | `GET` |
| Record result click | `/api/v1/search/click` | `POST` |
| Crawl web pages | `/api/v1/admin/crawl` | `POST` |
| Index a document | `/api/v1/admin/index` | `POST` |

Search requests include the query, selected ranker, a result limit of 10, and `explain=true`. Autocomplete requests are debounced by 200 milliseconds and are sent after at least two non-whitespace characters are entered.

## Project Structure

```text
indexium/
├── src/
│   ├── App.tsx                         # Main application layout and top-level state
│   ├── App.css                         # Application-specific styles
│   ├── index.css                       # Global styles and Tailwind entrypoint
│   ├── main.tsx                         # React application entrypoint
│   ├── Components/
│   │   ├── SearchQuery.tsx             # Search input, autocomplete, and ranker selector
│   │   ├── SearchResults.tsx            # Ranked result list and snippets
│   │   ├── ScoreExplainModal.tsx        # Ranking score explanation dialog
│   │   ├── AdminModal.tsx               # Crawl and manual indexing controls
│   │   ├── hooks/
│   │   │   └── useSearch.ts             # Search, autocomplete, explain, and click API logic
│   │   └── ui/
│   │       ├── button.tsx               # Reusable button component
│   │       └── input.tsx                # Reusable input component
│   ├── lib/
│   │   └── utils.ts                     # Shared class-name utilities
│   └── assets/                          # Static frontend assets
├── public/                              # Public static assets
├── index.html                           # Vite HTML entrypoint
├── package.json                         # Scripts and dependencies
├── vite.config.ts                       # Vite, React, Tailwind, and @ alias configuration
├── eslint.config.js                     # ESLint configuration
├── tsconfig.json                        # TypeScript project references
├── tsconfig.app.json                    # Application TypeScript configuration
└── tsconfig.node.json                   # Vite configuration TypeScript settings
```

## Development Notes

- API URLs are currently defined as `http://localhost:8000/api/v1` in `src/Components/hooks/useSearch.ts` and `src/Components/AdminModal.tsx`.
- The main application also requests telemetry from `http://localhost:8000/api/v1/stats`.
- Result snippets are rendered with `dangerouslySetInnerHTML` because the backend returns `<b>` tags for highlighted query terms. Only use this frontend with trusted or sanitized backend snippet output.
- The frontend does not include a separate API proxy configuration; ensure the backend allows requests from the Vite development origin.

## Production Build

```bash
cd indexium
npm run build
npm run preview
```

The generated static assets are written to `indexium/dist/`.

## Related Documentation

- [Repository overview](../README.md)
- [Backend documentation](../backend/README.md)
