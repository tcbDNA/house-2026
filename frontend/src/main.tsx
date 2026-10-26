import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import { fetchDefaults } from "./api";
import { applyModelDefaults } from "./types";
import "./index.css";

// The default scenario depends on backend settings, so install it before the
// first render (App reads the defaults synchronously when parsing the URL).
fetchDefaults()
  .then(applyModelDefaults)
  .catch((e) => console.warn("using built-in defaults:", e))
  .finally(() => {
    ReactDOM.createRoot(document.getElementById("root")!).render(
      <React.StrictMode>
        <App />
      </React.StrictMode>,
    );
  });
