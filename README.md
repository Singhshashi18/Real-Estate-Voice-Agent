# Inbound Receptionist Agent
<img width="1252" height="631" alt="image" src="https://github.com/user-attachments/assets/f9ed9a6c-0075-4634-9bee-4f007e335774" />
<img width="1240" height="626" alt="image" src="https://github.com/user-attachments/assets/17365b73-c938-4370-8ced-72c8efd76b8a" />
<img width="1243" height="642" alt="image" src="https://github.com/user-attachments/assets/270c3b7a-8d2c-41f8-a0ad-d87d861dfd59" />
<img width="1253" height="640" alt="image" src="https://github.com/user-attachments/assets/cbc340d4-5cfe-4174-a434-564363f7fce3" />
<img width="1269" height="587" alt="image" src="https://github.com/user-attachments/assets/5aca08b1-92d8-471a-9680-77129be60357" />
 
 

Phase 1 browser voice agent that schedules 30-minute meetings on your Google Calendar and sends calendar invites with Google Meet.

## What it does

1. Voice conversation in the browser (OpenAI Realtime API)
2. Collects caller **name** and **email**
3. Checks your Google Calendar availability (Mon–Fri, 9 AM–9 PM IST, up to 14 days ahead)
4. Books the meeting and emails a **Google Calendar invite** with **Google Meet**

## Prerequisites

- Python 3.11+
- OpenAI API key with Realtime API access
- Google Cloud OAuth client credentials as `credentials.json` in the project root
- Google Calendar API enabled for your project

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
ORGANIZER_NAME=Your Name
COMPANY_NAME=Your Company
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

## Project structure

```
app/
  main.py                 # FastAPI app
  config.py               # Settings from .env
  routes/
    session.py            # OpenAI Realtime session token
    tools.py              # Calendar tool endpoints
  services/
    calendar_service.py   # Availability + booking logic
    google_auth.py        # Google OAuth
    openai_session.py     # Agent instructions + tools
static/
  index.html              # Voice test UI
  app.js                  # WebRTC + tool handling
  style.css
scripts/
  setup_google_auth.py    # One-time Google auth
```

## Phase 2 (later)

Twilio voice will plug into the same backend tool endpoints (`check-availability`, `book-meeting`) so calendar and booking logic stay unchanged.

## Troubleshooting

- **Missing credentials.json** — download OAuth client JSON from Google Cloud Console (Desktop app type works for local auth).
- **Calendar 403** — ensure Calendar API is enabled and you completed `setup_google_auth.py`.
- **Realtime session fails** — confirm your OpenAI key has access to the Realtime model in `.env`.
- **No audio** — use Chrome/Edge, allow mic permissions, and use HTTPS or localhost.
