const isLocalhost =
  window.location.hostname === "localhost" ||
  window.location.hostname === "0.0.0.0";

// In production the React app and FastAPI backend share the same Azure App Service origin.
export const API_BASE_URL = isLocalhost ? "http://localhost:8000" : "";
