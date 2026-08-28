const jsonHeaders = { "Content-Type": "application/json" };

async function request(path, options = {}) {
  const response = await fetch(path, options);
  const contentType = response.headers.get("content-type") || "";
  let payload = null;

  if (contentType.includes("application/json")) {
    payload = await response.json();
  } else {
    payload = await response.text();
  }

  if (!response.ok) {
    const detail = payload && typeof payload === "object" ? payload.detail : payload;
    throw new Error(detail || `HTTP ${response.status}`);
  }

  return payload;
}

export const api = {
  health() {
    return request("/api/health");
  },

  state() {
    return request("/api/game/state");
  },

  mazes() {
    return request("/api/game/mazes");
  },

  loadMaze(name) {
    return request("/api/game/load", {
      method: "POST",
      headers: jsonHeaders,
      body: JSON.stringify({ name }),
    });
  },

  reset() {
    return request("/api/game/reset", { method: "POST" });
  },

  move(direction) {
    return request(`/api/game/move/${encodeURIComponent(direction)}`, { method: "POST" });
  },

  lms() {
    return request("/api/game/lms", { method: "POST" });
  },

  run(source) {
    return request("/api/interpreter/run", {
      method: "POST",
      headers: jsonHeaders,
      body: JSON.stringify({ source }),
    });
  },
};
