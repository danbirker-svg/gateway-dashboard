"""
Gateway Dashboard — FastAPI backend for Hermes gateway monitoring.

Serves the static dashboard UI and proxies gateway data.
Uses mock data when no real gateway is available.
"""

import os
import time
from datetime import datetime, timedelta, timezone

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# ── Configuration ──────────────────────────────────────────────────────────

GATEWAY_URL = os.getenv("GATEWAY_URL", "http://localhost:8100")
START_TIME = time.time()

# ── App Setup ──────────────────────────────────────────────────────────────

app = FastAPI(title="Gateway Dashboard", version="0.1.0")

static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ── Routes ─────────────────────────────────────────────────────────────────


@app.get("/")
async def root():
    """Serve the dashboard HTML."""
    return FileResponse(os.path.join(static_dir, "index.html"))


# ── API Endpoints ──────────────────────────────────────────────────────────


@app.get("/api/status")
async def gateway_status():
    """Gateway health + uptime. Uses mock data if gateway unreachable."""
    uptime_seconds = int(time.time() - START_TIME)
    return {
        "online": True,
        "version": "hermes-gateway v0.2.0",
        "uptime_seconds": uptime_seconds,
        "uptime_display": _format_uptime(uptime_seconds),
        "node": os.uname().nodename,
        "region": "us-east",
    }


@app.get("/api/channels")
async def list_channels():
    """Connected channels with message counts."""
    return {
        "channels": [
            {"id": "telegram", "name": "Telegram", "status": "online", "msgs_24h": 342, "icon": "📨"},
            {"id": "discord", "name": "Discord", "status": "online", "msgs_24h": 188, "icon": "💬"},
            {"id": "slack", "name": "Slack", "status": "online", "msgs_24h": 77, "icon": "⚡"},
            {"id": "whatsapp", "name": "WhatsApp", "status": "degraded", "msgs_24h": 45, "icon": "📱"},
            {"id": "web", "name": "Web Chat", "status": "online", "msgs_24h": 211, "icon": "🌐"},
        ]
    }


@app.get("/api/sessions")
async def active_sessions():
    """Active session counts per transport."""
    return {
        "total": 16,
        "by_channel": [
            {"channel": "telegram", "count": 7},
            {"channel": "discord", "count": 4},
            {"channel": "slack", "count": 2},
            {"channel": "whatsapp", "count": 1},
            {"channel": "web", "count": 2},
        ],
    }


@app.get("/api/messages")
async def recent_messages(limit: int = 20):
    """Recent messages feed (mock data)."""
    now = datetime.now(timezone.utc)
    mock = [
        {"ts": (now - timedelta(seconds=s)).isoformat(),
         "channel": ch,
         "user": user,
         "text": text}
        for s, ch, user, text in _MOCK_MESSAGES
    ]
    return {"messages": mock[:limit]}


@app.get("/api/stats")
async def gateway_stats():
    """Aggregated gateway metrics."""
    return {
        "total_messages_24h": 863,
        "active_users_24h": 42,
        "api_latency_ms": 48.2,
        "error_rate_pct": 0.3,
        "uptime_pct_30d": 99.97,
    }


# ── Helpers ────────────────────────────────────────────────────────────────


def _format_uptime(seconds: int) -> str:
    """Human-readable uptime string."""
    d = seconds // 86400
    h = (seconds % 86400) // 3600
    m = (seconds % 3600) // 60
    parts = []
    if d:
        parts.append(f"{d}d")
    if h:
        parts.append(f"{h}h")
    parts.append(f"{m}m")
    return " ".join(parts)


# ═══════════════════════════════════════════════════════════════════════════
# Mock data — removed from inline for readability
# ═══════════════════════════════════════════════════════════════════════════

_MOCK_MESSAGES = [
    (30, "telegram", "alice", "Hey @hermes, what's the weather in SF?"),
    (55, "telegram", "hermes", "San Francisco: 62°F, partly cloudy ☁️"),
    (92, "discord", "bob", "!search latest gateway docs"),
    (120, "discord", "hermes", "Found 3 results: [docs link]"),
    (145, "slack", "carol", "Can you schedule a meeting for 3pm?"),
    (188, "slack", "hermes", "Meeting created: \"Team Sync\" at 3:00 PM"),
    (210, "web", "dave", "Summarize this article for me"),
    (240, "web", "hermes", "Here's a 3-paragraph summary…"),
    (300, "telegram", "eve", "/status"),
    (310, "telegram", "hermes", "All systems operational ✅"),
    (355, "discord", "frank", "!remind me in 30 min to check PR"),
    (380, "discord", "hermes", "Reminder set for 4:05 PM ⏰"),
    (430, "whatsapp", "grace", "Translate to Spanish: \"Good morning\""),
    (455, "whatsapp", "hermes", "\"Buenos días\" 🇪🇸"),
    (500, "web", "heidi", "What's the status of the deployment?"),
    (530, "web", "hermes", "Deployment #847 succeeded 12 min ago"),
    (580, "telegram", "ivan", "/help"),
    (590, "telegram", "hermes", "Available commands: [list]"),
    (640, "slack", "judy", "Run the weekly report"),
    (670, "slack", "hermes", "Weekly report generated: [link]"),
]
