import React from "react";
import ReactDOM from "react-dom/client";
import App from "./App";
import "./utils/firebaseConfig"; // initialise Firebase on load

const root = ReactDOM.createRoot(document.getElementById("root"));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
