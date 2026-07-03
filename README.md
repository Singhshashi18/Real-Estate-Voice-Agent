# Inbound Receptionist Agent
<img width="1252" height="631" alt="image" src="https://github.com/user-attachments/assets/f9ed9a6c-0075-4634-9bee-4f007e335774" />
<img width="1240" height="626" alt="image" src="https://github.com/user-attachments/assets/17365b73-c938-4370-8ced-72c8efd76b8a" />
<img width="1243" height="642" alt="image" src="https://github.com/user-attachments/assets/270c3b7a-8d2c-41f8-a0ad-d87d861dfd59" />
<img width="1253" height="640" alt="image" src="https://github.com/user-attachments/assets/cbc340d4-5cfe-4174-a434-564363f7fce3" />
<img width="1269" height="587" alt="image" src="https://github.com/user-attachments/assets/5aca08b1-92d8-471a-9680-77129be60357" />



AI voice receptionist **Sara** for **Karyan Realty** (NCR). Sara helps callers find properties, answers questions, and books 30-minute site visits on Google Calendar with **Google Meet** invites — over the **browser** and over the **phone**.

## Channels

| Channel | Voice | How |
|---------|-------|-----|
| **Browser (inbound)** | OpenAI Realtime (`shimmer`) | Next.js app → WebRTC |
| **Phone (inbound)** | ElevenLabs (voice you pick) | Twilio number → ElevenLabs agent → backend webhooks |
| **Phone (outbound)** | ElevenLabs (Sara, outbound persona) | CSV leads → ElevenLabs batch calling → Twilio |

> **Live number:** `+1 (661) 486-4467` is provisioned and **attached to the agent**. Inbound calls route through Twilio (`voice_url → https://api.us.elevenlabs.io/twilio/inbound_call`) to the ElevenLabs Conversational AI agent, and the same number is used as caller ID for outbound follow-up calls. Status: `in-use` (voice + SMS enabled).

No LangChain / LangGraph — OpenAI Realtime (browser) + ElevenLabs Conversational AI (phone), with plain Python tool services.

## What it does

1. Voice conversation in the browser (OpenAI Realtime API) or over the phone (ElevenLabs)
2. Searches the Karyan knowledge base (property, budget in lakh/crore, BHK, NCR areas)
3. Collects caller **name** and **email**
4. Checks your Google Calendar availability (Mon–Fri, 9 AM–9 PM IST, up to 14 days ahead)
5. Books the meeting and emails a **Google Calendar invite** with **Google Meet**
6. **Outbound:** follows up on property leads via ElevenLabs batch calling (CSV upload)

## Prerequisites

- Python 3.11+
- Node.js 18+ (frontend)
- OpenAI API key with Realtime API access
- Google Cloud OAuth client credentials as `credentials.json` in the project root
- Google Calendar API + Gmail API enabled for your project
- **Phone (optional):** Twilio number, ElevenLabs account + API key

## Setup

```bash
cd INBOUND-AGENT 
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and set your values:

```env
OPENAI_API_KEY=sk-...
ORGANIZER_NAME=Sara
COMPANY_NAME=Karyan

# Phone (optional)
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+16614864467

# ElevenLabs (phone + outbound)
ELEVENLABS_API_KEY=...
ELEVENLABS_OUTBOUND_AGENT_ID=agent_...
ELEVENLABS_PHONE_NUMBER_ID=phnum_...

# Public URL for tool webhooks + Bearer secret for /api/telephony/tools/*
API_PUBLIC_URL=https://your-public-url
TELEPHONY_WEBHOOK_SECRET=your-strong-secret
```

Place your `credentials.json` in the project root (same folder as `.env`).

Authorize Google Calendar (one-time — opens browser):

```bash
python scripts/setup_google_auth.py
```

This creates `token.json`.

## Run locally

```bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000), click **Start call**, allow microphone access, and talk to the agent.


Example flow:

- "I'd like to book a meeting"
- Agent asks for your name and email
- "How about Thursday at 2 PM?" 
- Agent checks availability, confirms, books, and sends the invite

## Phone agent — Twilio + ElevenLabs (inbound)

Agent personality and **voice are configured in the ElevenLabs dashboard**. This repo provides the **tool webhooks** (search, booking, calendar).

The Karyan number `+1 (661) 486-4467` is already imported into ElevenLabs and assigned to the inbound agent.

Short version:

1. Run backend (+ public URL if testing locally)
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

## Outbound agent — ElevenLabs batch calling

Follow-up calls to property leads via **ElevenLabs batch calling** + Twilio (`+1 661 486 4467` as caller ID). Uses a **separate outbound ElevenLabs agent** with the Sara persona and a follow-up prompt.

```
CSV upload → FastAPI /api/outbound/campaigns
    → ElevenLabs POST /v1/convai/batch-calling/submit
    → Twilio dials each lead
    → ElevenLabs outbound agent (Sara) → tool webhooks
```

Setup:

1. `python scripts/export_elevenlabs_outbound_setup.py` → `data/elevenlabs_outbound_setup_kit.json`
2. ElevenLabs → create a **separate outbound agent**, paste prompt + first message
3. Add the same **6 webhook tools**, enable dynamic variables (`customer_name`, `customer_email`, `property_id`, `budget`, `area`, `notes`)
4. Assign `+16614864467`, then set `ELEVENLABS_OUTBOUND_AGENT_ID` and `ELEVENLABS_PHONE_NUMBER_ID` in `.env`
5. Open `http://127.0.0.1:8000/outbound`, sign in, upload a CSV, and start calls

CSV columns — `phone` (required), plus optional `name`, `email`, `property_id`, `budget`, `area`, `notes`. Sample: `data/sample_outbound_leads.csv`. Indian 10-digit numbers are auto-normalized to `+91...`.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/outbound/status` | Config check |
| `GET` | `/api/outbound/setup-kit` | Outbound prompt + tools JSON |
| `POST` | `/api/outbound/parse-csv` | Upload CSV → preview leads |
| `POST` | `/api/outbound/campaigns` | Submit batch to ElevenLabs |
| `GET` | `/api/outbound/campaigns` | List campaigns |
| `POST` | `/api/outbound/campaigns/{id}/refresh` | Sync status from ElevenLabs |
| `POST` | `/api/outbound/campaigns/{id}/cancel` | Cancel batch |

Full guide: `docs/OUTBOUND_SETUP.md`. Only call leads who consented to contact (TRAI DND / TCPA).

## Project structure

```
app/
  main.py                 # FastAPI app
  config.py               # Settings from .env
  routes/
    session.py            # OpenAI Realtime session token
    tools.py              # Calendar tool endpoints (browser)
    telephony.py          # ElevenLabs webhook tools (phone)
    twilio.py             # Optional Twilio status / fallback
    outbound.py           # Outbound campaigns (CSV → batch calling)
  services/
    calendar_service.py   # Availability + booking logic
    booking_email.py      # Gmail confirmation emails
    google_auth.py        # Google OAuth
    knowledge_base.py     # Property search + company info
    openai_session.py     # Agent instructions + tools
    elevenlabs_service.py # ElevenLabs tool/webhook definitions
    elevenlabs_outbound.py# ElevenLabs batch calling client
    outbound_prompt.py    # Outbound Sara prompt
    outbound_service.py   # CSV parsing + campaign storage
static/
  index.html              # Voice test UI
  app.js                  # WebRTC + tool handling
  style.css
  outbound.html           # Outbound campaigns UI
scripts/
  setup_google_auth.py            # One-time Google auth
  export_elevenlabs_setup.py      # Inbound ElevenLabs setup kit
  export_elevenlabs_outbound_setup.py  # Outbound ElevenLabs setup kit
data/
  karyan_knowledge_base.json      # NCR listings
  elevenlabs_setup_kit.json       # Generated — paste into ElevenLabs
  sample_outbound_leads.csv       # Sample outbound leads
docs/
  OUTBOUND_SETUP.md               # Outbound calling guide
```

## Troubleshooting

- **Missing credentials.json** — download OAuth client JSON from Google Cloud Console (Desktop app type works for local auth).
- **Calendar 403** — ensure Calendar API is enabled and you completed `setup_google_auth.py`.
- **Realtime session fails** — confirm your OpenAI key has access to the Realtime model in `.env`.
- **No audio** — use Chrome/Edge, allow mic permissions, and use HTTPS or localhost.
- **Phone tools return 401** — match `TELEPHONY_WEBHOOK_SECRET` in `.env` and the ElevenLabs tool header.
- **Phone tools timeout** — backend down or `API_PUBLIC_URL` unreachable.
- **Outbound not configured** — set `ELEVENLABS_API_KEY`, `ELEVENLABS_OUTBOUND_AGENT_ID`, and `ELEVENLABS_PHONE_NUMBER_ID` in `.env`.
