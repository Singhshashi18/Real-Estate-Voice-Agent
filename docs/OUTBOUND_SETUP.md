# Outbound agent — ElevenLabs batch calling

Follow-up calls to property leads via **ElevenLabs batch calling** + Twilio (`+1 661 486 4467`).

## Architecture

```
CSV upload (dashboard) → FastAPI /api/outbound/campaigns
    → ElevenLabs POST /v1/convai/batch-calling/submit
    → Twilio dials each lead
    → ElevenLabs outbound agent (Sara)
    → Tool webhooks → /api/telephony/tools/*
```

## 1. ElevenLabs dashboard — separate outbound agent

1. Run: `python scripts/export_elevenlabs_outbound_setup.py`
2. Open `data/elevenlabs_outbound_setup_kit.json`
3. ElevenLabs → **Conversational AI** → **Create agent** (outbound Sara)
4. Paste **system prompt** + **first message**
5. Add the same **6 webhook tools** as inbound (Bearer `TELEPHONY_WEBHOOK_SECRET`)
6. Enable dynamic variables: `customer_name`, `customer_email`, `property_id`, `budget`, `area`, `notes`
7. **Phone Numbers** → use existing Twilio import (`+16614864467`)

Copy from dashboard:

- **Agent ID** → `ELEVENLABS_OUTBOUND_AGENT_ID`
- **Phone number ID** → `ELEVENLABS_PHONE_NUMBER_ID`

List phone numbers via API:

```bash
curl -H "xi-api-key: $ELEVENLABS_API_KEY" https://api.elevenlabs.io/v1/convai/phone-numbers
```

## 2. `.env` (add these)

```env
ELEVENLABS_API_KEY=your-key
ELEVENLABS_OUTBOUND_AGENT_ID=agent_...
ELEVENLABS_PHONE_NUMBER_ID=phnum_...
TELEPHONY_WEBHOOK_SECRET=...
API_PUBLIC_URL=https://your-public-url
```

## 3. CSV format

Required: `phone`  
Optional: `name`, `email`, `property_id`, `budget`, `area`, `notes`

Sample: `data/sample_outbound_leads.csv`

| phone | name | email | property_id | budget | area | notes |
|-------|------|-------|-------------|--------|------|-------|
| +919876543210 | Rahul | ... | KR-101 | 52 lakh | Ghaziabad | ... |

Indian 10-digit numbers are auto-normalized to `+91...`.

## 4. API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/outbound/status` | Config check |
| GET | `/api/outbound/setup-kit` | Prompt + tools JSON |
| POST | `/api/outbound/parse-csv` | Upload CSV → preview leads |
| POST | `/api/outbound/campaigns` | Submit batch to ElevenLabs |
| GET | `/api/outbound/campaigns` | List campaigns |
| GET | `/api/outbound/campaigns/{id}` | Campaign detail |
| POST | `/api/outbound/campaigns/{id}/refresh` | Sync status from ElevenLabs |
| POST | `/api/outbound/campaigns/{id}/cancel` | Cancel batch |

All routes require `Authorization: Bearer <jwt>`.

## 5. Submit campaign (example)

```bash
# Login first, then:
curl -X POST http://127.0.0.1:8000/api/outbound/campaigns \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name":"Karyan follow-up Mar 2026","leads":[{"phone":"+919876543210","name":"Rahul","budget":"50 lakh"}]}'
```

## 6. Compliance

Only call leads who consented to contact. Respect local telemarketing rules (India TRAI DND, US TCPA, etc.).
