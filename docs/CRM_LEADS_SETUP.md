# CRM / lead source integration

Central **leads store** that ingests contacts from **HubSpot**, deduplicates by phone,
and can **auto-call new leads** through the ElevenLabs outbound agent.

## Flow

```
HubSpot contacts ──sync──> leads table (dedupe by phone)
                                  │
                          new lead? ──yes──> ElevenLabs outbound call (Sara)
                                  │
                              stored + status tracked (new → calling → called/failed)
```

## 1. HubSpot setup

1. HubSpot → **Settings → Integrations → Private Apps → Create a private app**
2. Scopes: `crm.objects.contacts.read`
3. Copy the **access token**

## 2. `.env`

```env
HUBSPOT_ACCESS_TOKEN=pat-na1-xxxxxxxx
OUTBOUND_AUTO_CALL=true            # auto-call new leads on sync (default true)

# Required for auto-call to actually place calls:
ELEVENLABS_API_KEY=...
ELEVENLABS_OUTBOUND_AGENT_ID=agent_...
ELEVENLABS_PHONE_NUMBER_ID=phnum_...
```

If outbound isn't configured, leads still sync and store — they just won't be called.

## 3. Use it

Backend UI: `http://127.0.0.1:8000/leads` — sign in, **Sync from HubSpot**, or add a lead manually.

## API

All routes require `Authorization: Bearer <jwt>`.

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/leads/status` | HubSpot + outbound config check |
| `GET` | `/api/leads` | List leads (`?status=`, `?source=`) |
| `POST` | `/api/leads` | Add a lead manually (dedupe by phone) |
| `DELETE` | `/api/leads/{id}` | Delete a lead |
| `POST` | `/api/leads/{id}/call` | Manually place an outbound call |
| `POST` | `/api/leads/{id}/do-not-call` | Mark do-not-call (skips auto-call) |
| `POST` | `/api/leads/sync/hubspot` | Pull HubSpot contacts; auto-call new ones |

### Sync example

```bash
curl -X POST http://127.0.0.1:8000/api/leads/sync/hubspot \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"auto_call": true, "limit": 100}'
```

Response:

```json
{
  "source": "hubspot",
  "fetched": 42,
  "new_leads": 5,
  "updated_leads": 37,
  "auto_call": true,
  "calls": [{ "phone": "+9198...", "called": true, "conversation_id": "conv_..." }]
}
```

## Lead model

| Field | Notes |
|-------|-------|
| `phone` | Normalized to E.164 (10-digit → `+91`) — **dedupe key** |
| `name`, `email`, `property_id`, `budget`, `area`, `notes` | Passed to Sara as dynamic variables |
| `source` | `hubspot` / `manual` / `csv` / `webhook` |
| `external_id` | HubSpot contact ID |
| `status` | `new → calling → called / failed`, or `do_not_call` |

## Notes

- **Dedupe:** re-syncing updates existing leads instead of creating duplicates; only genuinely **new** phones trigger auto-call.
- **Auto-call safety:** `do_not_call` leads are never auto-called. Failures are recorded per lead, never crash the sync.
- **Compliance:** only call leads who consented (TRAI DND / TCPA). Use the DNC button to suppress.
