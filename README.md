# INBOUND-AGENT — Karyan Realty Voice Receptionist

AI voice receptionist **Sara** for **Karyan Realty** (NCR). Helps callers find properties, answer questions, and book site visits with Google Calendar + Meet invites.

Two channels:

| Channel | Voice | How |
|---------|--------|-----|
| **Browser** | OpenAI Realtime (`shimmer`) | Next.js app → WebRTC |
| **Phone** | ElevenLabs (voice you pick) | Twilio number → ElevenLabs agent → backend webhooks |

No LangChain / LangGraph — OpenAI Realtime (browser) + ElevenLabs Conversational AI (phone), with plain Python tool services.

---

## Features

- Natural English receptionist (property search, budget in lakh/crore, BHK, NCR areas)
- Karyan knowledge base (`data/karyan_knowledge_base.json`)
- Google Calendar availability + booking (Mon–Fri 9 AM–9 PM IST)
- Gmail confirmation after booking
- JWT auth + dashboard UI (Next.js)
- Phone agent: ElevenLabs tools → `/api/telephony/tools/*`

---

## Tech stack

**Backend:** Python, FastAPI, Uvicorn  
**Frontend:** Next.js, React, TypeScript, Tailwind CSS  
**Browser voice:** OpenAI Realtime API (WebRTC), Whisper  
**Phone voice:** ElevenLabs Conversational AI + Twilio  
**Integrations:** Google Calendar API, Gmail API, Google OAuth  

---

## Prerequisites

- Python 3.11+
- Node.js 18+ (frontend)
- OpenAI API key (Realtime access)
- Google Cloud: Calendar API + Gmail API, `credentials.json`
- **Phone (optional):** Twilio number, ElevenLabs account

---

## Quick start — local

### 1. Backend

```bash
cd INBOUND-AGENT
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

Copy `.env.example` → `.env` and set at minimum:

```env
OPENAI_API_KEY=sk-...
ORGANIZER_NAME=Sara
COMPANY_NAME=Karyan
JWT_SECRET=change-me
FRONTEND_URL=http://127.0.0.1:3001
API_PUBLIC_URL=http://127.0.0.1:8000
```

Place `credentials.json` in the project root. Authorize Google (one-time):

```bash
python scripts/setup_google_auth.py
```

Run API:

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

Open [http://127.0.0.1:3001](http://127.0.0.1:3001) → sign up / log in → **Inbound** → talk to Sara.

### 3. Legacy browser UI (no auth)

[http://127.0.0.1:8000/legacy](http://127.0.0.1:8000/legacy)

---

## Phone agent — Twilio + ElevenLabs

Agent personality and **voice are configured in the ElevenLabs dashboard**. This repo provides the **tool webhooks** (search, booking, calendar).

> **Live number:** `+1 (661) 486-4467` is provisioned and **attached to the inbound agent**. Inbound calls route through Twilio (`voice_url → https://api.us.elevenlabs.io/twilio/inbound_call`) to the ElevenLabs Conversational AI agent. Status: `in-use` (voice + SMS enabled).

**Start here:** [`docs/ELEVENLABS_CONNECT.md`](docs/ELEVENLABS_CONNECT.md)

Short version:

1. Run backend (+ public URL if testing locally — see [`docs/PUBLIC_URL_SETUP.md`](docs/PUBLIC_URL_SETUP.md))
2. Set `TELEPHONY_WEBHOOK_SECRET` in `.env`
3. Run `python scripts/export_elevenlabs_setup.py` → copy from `data/elevenlabs_setup_kit.json`
4. ElevenLabs → create agent, pick voice, paste prompt, add **6 webhook tools**
5. ElevenLabs → **Phone Numbers** → import Twilio → assign agent

Tool auth header on every ElevenLabs webhook:

```
Authorization: Bearer YOUR_TELEPHONY_WEBHOOK_SECRET
```

| Tool | Endpoint |
|------|----------|
| `search_properties` | `POST /api/telephony/tools/search_properties` |
| `get_inventory_overview` | `POST /api/telephony/tools/get_inventory_overview` |
| `get_property_details` | `POST /api/telephony/tools/get_property_details` |
| `check_availability` | `POST /api/telephony/tools/check_availability` |
| `validate_email` | `POST /api/telephony/tools/validate_email` |
| `book_meeting` | `POST /api/telephony/tools/book_meeting` |

For a **fixed public URL** (no tunnel): [`docs/DEPLOY.md`](docs/DEPLOY.md) (Render / Docker).

---

## Project structure

```
app/
  main.py                    # FastAPI app
  config.py                  # Settings from .env
  routes/
    auth.py, oauth.py        # JWT + social login
    session.py               # OpenAI Realtime WebRTC session
    tools.py                 # Browser tool API
    telephony.py             # ElevenLabs webhook tools
    twilio.py                # Optional Twilio status / fallback
  services/
    openai_session.py        # Sara instructions + Realtime tools
    knowledge_base.py        # Property search
    calendar_service.py      # Availability + booking
    tool_executor.py         # Shared tool logic (browser + phone)
    elevenlabs_service.py    # Setup kit export
    booking_email.py         # Gmail confirmations
data/
  karyan_knowledge_base.json
  elevenlabs_setup_kit.json  # Generated — paste into ElevenLabs
frontend/                    # Next.js UI
docs/
  ELEVENLABS_CONNECT.md      # Phone setup (main guide)
  DEPLOY.md                  # Permanent public URL
  PUBLIC_URL_SETUP.md        # Local tunnels
scripts/
  setup_google_auth.py
  export_elevenlabs_setup.py
  pack_google_token.py       # Cloud deploy helper
```

---

## Environment variables

| Variable | Required | Purpose |
|----------|----------|---------|
| `OPENAI_API_KEY` | Yes | Browser Realtime agent |
| `ORGANIZER_NAME` | No | Agent name (default Sara) |
| `COMPANY_NAME` | No | Branding |
| `JWT_SECRET` | Yes (prod) | Auth tokens |
| `FRONTEND_URL` | No | OAuth redirects, CORS |
| `API_PUBLIC_URL` | Phone | Base URL for ElevenLabs tool webhooks |
| `TELEPHONY_WEBHOOK_SECRET` | Phone | Bearer token for `/api/telephony/tools/*` |
| `GOOGLE_TOKEN_JSON` | Cloud | One-line token for deploy (see `pack_google_token.py`) |
| `TWILIO_*` | Optional | Reference; primary use is ElevenLabs import |
| `ELEVENLABS_API_KEY` | Optional | `/api/telephony/voices` helper only |

See [`.env.example`](.env.example) for the full list.

---

## API endpoints

| Endpoint | Auth | Description |
|----------|------|-------------|
| `GET /api/health` | No | Health check |
| `POST /api/session` | JWT | OpenAI Realtime SDP exchange |
| `POST /api/tools/*` | No | Browser agent tools |
| `POST /api/telephony/tools/{name}` | Bearer | ElevenLabs phone tools |
| `GET /api/telephony/setup-kit` | No | Prompt + tool URLs for ElevenLabs |

---

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Realtime / SDP errors | Check `OPENAI_API_KEY`, model `gpt-realtime` in `.env` |
| Calendar / booking fails | Run `python scripts/setup_google_auth.py`; approve Gmail scope |
| Phone tools return 401 | Match `TELEPHONY_WEBHOOK_SECRET` in `.env` and ElevenLabs tool header |
| Phone tools timeout | Backend down or public URL unreachable |
| Sara speaks Hindi (browser) | Instructions enforce English; start a new session |
| No confirmation email | Re-run `setup_google_auth.py` with Gmail permission |

---

## License

Private / project use.
