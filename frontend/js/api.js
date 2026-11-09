const localHosts = new Set(["localhost", "127.0.0.1"]);
const defaultApiBase = localHosts.has(window.location.hostname)
  ? "http://localhost:8000"
  : window.location.origin;
const API_BASE = window.TIENDA_API_URL || defaultApiBase;

export class StoreApi {
  constructor(baseUrl = API_BASE) {
    this.baseUrl = baseUrl.replace(/\/$/, "");
    this.accessToken = sessionStorage.getItem("tienda_access_token");
  }

  setAccessToken(token) {
    this.accessToken = token;
    if (token) sessionStorage.setItem("tienda_access_token", token);
    else sessionStorage.removeItem("tienda_access_token");
  }

  async request(path, { method = "GET", body, query } = {}) {
    const url = new URL(`${this.baseUrl}${path}`);
    if (query) {
      for (const [key, value] of Object.entries(query)) {
        if (value !== undefined && value !== null && value !== "") url.searchParams.set(key, value);
      }
    }
    const headers = new Headers({ Accept: "application/json" });
    if (this.accessToken) headers.set("Authorization", `Bearer ${this.accessToken}`);
    const options = { method, headers };
    if (body !== undefined) {
      headers.set("Content-Type", "application/json");
      options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);
    if (response.status === 204) return null;
    const payload = await response.json().catch(() => ({}));
    if (!response.ok) {
      const detail = Array.isArray(payload.detail)
        ? payload.detail.map((item) => item.msg).join(" ")
        : payload.detail;
      throw new Error(detail || `La solicitud falló (${response.status}).`);
    }
    return payload;
  }
}
