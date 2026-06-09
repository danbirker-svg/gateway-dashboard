/**
 * Gateway Dashboard — Frontend Logic
 * Polls the backend API and renders the dashboard.
 */

const REFRESH_INTERVAL = 5000; // 5 seconds
let refreshTimer = null;
let countdown = 0;

// ── Bootstrap ─────────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", () => {
  refreshAll();
  refreshTimer = setInterval(refreshAll, REFRESH_INTERVAL);
  startCountdown();
});

async function refreshAll() {
  await Promise.allSettled([
    fetchStatus(),
    fetchStats(),
    fetchChannels(),
    fetchSessions(),
    fetchMessages(),
  ]);
  countdown = REFRESH_INTERVAL / 1000;
}

// ── Countdown ─────────────────────────────────────────────────────────────

function startCountdown() {
  const el = document.getElementById("refresh-countdown");
  setInterval(() => {
    countdown = Math.max(0, countdown - 1);
    if (el) el.textContent = countdown + "s";
  }, 1000);
}

// ── API Fetch Helpers ─────────────────────────────────────────────────────

async function api(path) {
  try {
    const res = await fetch(path);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.warn(`[Dashboard] ${path} failed:`, err.message);
    return null;
  }
}

// ── Status ────────────────────────────────────────────────────────────────

async function fetchStatus() {
  const data = await api("/api/status");
  if (!data) return;

  // Gateway status badge
  const badge = document.getElementById("gateway-status");
  if (badge) {
    badge.textContent = data.online ? "● Online" : "● Offline";
    badge.className = "status-badge" + (data.online ? "" : " offline");
  }

  // Version
  const versionEl = document.getElementById("gateway-version");
  if (versionEl) versionEl.textContent = data.version || "—";

  // Uptime
  const uptimeEl = document.getElementById("gateway-uptime");
  if (uptimeEl) uptimeEl.textContent = "⏱ " + (data.uptime_display || "—");

  // Node
  const nodeEl = document.getElementById("node-name");
  if (nodeEl) nodeEl.textContent = data.node || "—";
}

// ── Stats ─────────────────────────────────────────────────────────────────

async function fetchStats() {
  const data = await api("/api/stats");
  if (!data) return;

  setText("stat-msgs", data.total_messages_24h?.toLocaleString() || "—");
  setText("stat-users", data.active_users_24h?.toLocaleString() || "—");
  setText("stat-latency", (data.api_latency_ms || "—") + " ms");
  setText("stat-errors", (data.error_rate_pct ?? "—") + "%");
  setText("stat-uptime", (data.uptime_pct_30d ?? "—") + "%");
}

// ── Channels ──────────────────────────────────────────────────────────────

async function fetchChannels() {
  const data = await api("/api/channels");
  if (!data || !data.channels) return;

  const list = document.getElementById("channels-list");
  if (!list) return;

  list.innerHTML = data.channels
    .map(
      (ch) => `
      <div class="channel-row">
        <div class="channel-left">
          <span class="channel-icon">${escapeHtml(ch.icon || "📡")}</span>
          <span class="channel-name">${escapeHtml(ch.name)}</span>
        </div>
        <div class="channel-meta">
          <span class="channel-msgs">${ch.msgs_24h?.toLocaleString() || 0} msgs</span>
          <span class="channel-dot ${escapeHtml(ch.status)}"></span>
        </div>
      </div>`
    )
    .join("");
}

// ── Sessions ──────────────────────────────────────────────────────────────

async function fetchSessions() {
  const data = await api("/api/sessions");
  if (!data) return;

  const totalEl = document.getElementById("sessions-total");
  if (totalEl) totalEl.textContent = data.total ?? "—";

  const breakdown = document.getElementById("sessions-breakdown");
  if (!breakdown || !data.by_channel) return;

  breakdown.innerHTML = data.by_channel
    .map(
      (s) =>
        `<span class="session-chip">
          <span class="count">${s.count}</span>
          <span class="label">${escapeHtml(s.channel)}</span>
        </span>`
    )
    .join("");
}

// ── Messages ──────────────────────────────────────────────────────────────

async function fetchMessages() {
  const data = await api("/api/messages?limit=20");
  if (!data || !data.messages) return;

  const feed = document.getElementById("messages-feed");
  if (!feed) return;

  feed.innerHTML = data.messages
    .map((m) => {
      const time = formatTime(m.ts);
      return `
      <div class="msg-row">
        <span class="msg-ts">${time}</span>
        <span class="msg-channel ${escapeHtml(m.channel)}">${escapeHtml(m.channel)}</span>
        <span class="msg-user">${escapeHtml(m.user)}</span>
        <span class="msg-text">${escapeHtml(m.text)}</span>
      </div>`;
    })
    .join("");
}

// ── Helpers ───────────────────────────────────────────────────────────────

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

function formatTime(iso) {
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  } catch {
    return "—";
  }
}
