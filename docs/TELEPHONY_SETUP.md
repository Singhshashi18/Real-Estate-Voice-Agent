# Phone agent — ElevenLabs dashboard setup

**You configure the agent and voice in ElevenLabs.** This backend only runs property search, booking, and calendar tools.

## Flow

```
Caller → Twilio number → ElevenLabs agent (you create + voice you pick)
                              ↓ server tools
                         /api/telephony/tools/*
```

## Step 1 — Public URL + backend `.env`

ElevenLabs tools need a **public HTTPS** URL to your machine. You do **not** need ngrok — see **`docs/PUBLIC_URL_SETUP.md`** (Cloudflare Tunnel, LocalTunnel, or deploy).

```env
API_PUBLIC_URL=https://YOUR-PUBLIC-HTTPS-URL
TELEPHONY_WEBHOOK_SECRET=pick-a-long-random-string
```

**Easiest free option (Windows):** install [cloudflared](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/), then:

```powershell
# Terminal 1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2
cloudflared tunnel --url http://localhost:8000
```

Copy the `https://....trycloudflare.com` URL into `API_PUBLIC_URL`, restart uvicorn, then export the setup kit again.

## Step 2 — Get copy-paste kit

```bash
python scripts/export_elevenlabs_setup.py
```

Or open in browser: `http://127.0.0.1:8000/api/telephony/setup-kit`

You get:
- **System prompt** (Sara / Karyan instructions)
- **First message**
- **6 server tool URLs** + auth header

## Step 3 — ElevenLabs dashboard

1. [elevenlabs.io](https://elevenlabs.io) → **Conversational AI** → **Create agent**
2. **Name** — e.g. `Karyan Receptionist — Sara`
3. **Voice** — browse voices and assign one (all in ElevenLabs UI)
4. **Language** — English
5. **First message** — paste from setup kit
6. **System prompt** — paste `agent.system_prompt` from setup kit
7. **Tools** → **Add webhook tool** for each:

| Tool name | Method | URL |
|-----------|--------|-----|
| `search_properties` | POST | `{API_PUBLIC_URL}/api/telephony/tools/search_properties` |
| `get_inventory_overview` | POST | `.../get_inventory_overview` |
| `get_property_details` | POST | `.../get_property_details` |
| `check_availability` | POST | `.../check_availability` |
| `validate_email` | POST | `.../validate_email` |
| `book_meeting` | POST | `.../book_meeting` |

**Every tool** → Request headers:

```
Authorization: Bearer YOUR_TELEPHONY_WEBHOOK_SECRET
```

## Step 4 — Twilio number in ElevenLabs

1. ElevenLabs → **Phone Numbers** → **Import from Twilio**
2. Enter Twilio **Account SID** + **Auth Token**
3. Select your number → **Assign** the agent you created

ElevenLabs configures Twilio webhooks automatically. Do not point Twilio voice URL at this server.

## Step 5 — Test

Call your Twilio number. Sara should answer with your ElevenLabs voice and can search properties + book visits.

## Optional `.env` (not required for phone)

```env
TWILIO_ACCOUNT_SID=AC...    # reference only; primary use is in ElevenLabs import
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...
ELEVENLABS_API_KEY=...      # only if you want GET /api/telephony/voices helper
```

## Browser agent

Unchanged — still uses OpenAI Realtime in the web app. Phone uses ElevenLabs only.
