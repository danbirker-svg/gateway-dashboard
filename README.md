# Gateway Dashboard

A clean, dark-themed web dashboard for monitoring a Hermes Agent gateway.  
Think Grafana-lite — real-time status, channels, sessions, and message feed.

![Dashboard Screenshot](docs/screenshot.png)

## Features

- **Gateway Status** — online/offline indicator with uptime, version, and node info
- **Connected Channels** — Telegram, Discord, Slack, WhatsApp, Web with message counts
- **Active Sessions** — per-channel session breakdown
- **Recent Messages** — live-scrolling feed of the last 20 gateway messages
- **Dark Theme** — clean, professional design inspired by Grafana

## Quickstart

```bash
# 1. Clone
git clone https://github.com/danbirker-svg/gateway-dashboard.git
cd gateway-dashboard

# 2. Install
pip install -r requirements.txt

# 3. Run
python server.py

# 4. Open
open http://localhost:8000
```

Or with uvicorn directly:

```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

## Architecture

```
gateway-dashboard/
├── server.py             # FastAPI backend (API + static serving)
├── static/
│   ├── index.html        # Dashboard UI
│   ├── style.css         # Dark theme styles
│   └── app.js            # Dashboard logic (fetch + rendering)
├── requirements.txt
├── LICENSE               # MIT
└── README.md
```

The backend serves both the static dashboard and a REST API that the frontend
polls via `fetch()`. When a real Hermes gateway is running at `GATEWAY_URL`,
the backend can proxy live data. Without one, it falls back to realistic mock
data for demos and development.

## Configuration

| Env Variable    | Default                  | Description                       |
|-----------------|--------------------------|-----------------------------------|
| `GATEWAY_URL`   | `http://localhost:8100`  | Hermes gateway status endpoint    |

## API Endpoints

| Endpoint         | Description                          |
|------------------|--------------------------------------|
| `GET /api/status`  | Gateway health, uptime, version    |
| `GET /api/channels`| Connected channels + message counts |
| `GET /api/sessions`| Active sessions per transport       |
| `GET /api/messages`| Recent message feed (default 20)    |
| `GET /api/stats`   | Aggregated 24h metrics              |

## License

MIT — see [LICENSE](LICENSE)
