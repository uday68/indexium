// App.tsx
import React from "react";
import reactLogo from "./assets/react.svg";
import viteLogo from "/vite.svg";
import "./App.css";

import { SearchBar } from "./Components/SearchQuery";

function App(): JSX.Element {
  return (
    <>
      <SearchBar />
    </>
  );
}

export default App;
