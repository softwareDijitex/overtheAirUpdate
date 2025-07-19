const isLocalhost =
  window.location.hostname === "localhost" ||
  window.location.hostname === "0.0.0.0";

export const API_BASE_URL = isLocalhost
  ? "http://localhost:8000"
  : "https://ontheflyupdate-cvg3c5dveqg3byav.canadacentral-01.azurewebsites.net";
