# Connect Twilio number + ElevenLabs agent (step by step)

Your backend handles **tools only** (property search, booking, calendar).  
**ElevenLabs** handles voice + conversation. **Twilio** is linked inside ElevenLabs.

```
Phone call → Twilio (+16614864467)
              → ElevenLabs agent (Sara + voice you pick)
                    → POST webhooks to your backend tools
                          → Karyan listings / Google Calendar
```

**Before you start:** backend running + public URL reachable (tunnel or deploy).

```powershell
uvicorn app.main:app --host 0.0.0.0 --port 8000
# + your tunnel if testing locally
```

Open your copy-paste file: **`data/elevenlabs_setup_kit.json`** (or run `python scripts/export_elevenlabs_setup.py`).

---

## Part 1 — Create the agent in ElevenLabs

1. Go to [elevenlabs.io](https://elevenlabs.io) → sign in  
2. Left menu → **Conversational AI** → **Agents**  
3. Click **Create agent** / **New agent**

### Agent settings

| Field | What to paste |
|-------|----------------|
| **Name** | `Karyan Receptionist — Sara` |
| **Language** | English |
| **First message** | From `elevenlabs_setup_kit.json` → `agent.first_message` |
| **System prompt** | From `elevenlabs_setup_kit.json` → `agent.system_prompt` (long text) |

### Voice

1. In the agent editor → **Voice** tab  
2. Browse voices → pick one (e.g. female, warm)  
3. **Save** — voice lives only in ElevenLabs, not in `.env`

---

## Part 2 — Add server tools (webhooks)

Each tool is a **webhook** ElevenLabs calls when Sara needs data.

1. Agent editor → **Tools** (or **Integrations** → **Server tools** / **Webhooks**)  
2. Click **Add tool** → choose **Webhook** / **Custom API**  
3. Repeat for all **6 tools** below

### Auth header (same on every tool)

| Header name | Value |
|-------------|--------|
| `Authorization` | `Bearer karyan-telephony-7f3a9c2e1b8d4f6a` |

(Must match `TELEPHONY_WEBHOOK_SECRET` in your `.env`.)

### Tool 1 — `search_properties`

- **URL:** `https://YOUR-PUBLIC-URL/api/telephony/tools/search_properties`  
- **Method:** `POST`  
- **Body parameters (JSON):**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `location` | string | no | Ghaziabad, Noida, Gurugram… |
| `bhk` | string | no | e.g. `2 BHK` |
| `budget` | string | no | e.g. `50 lakh` |
| `max_budget_lakhs` | number | no | e.g. `50` (lakhs, not rupees) |
| `property_type` | string | no | apartment, villa, plot |
| `query` | string | no | keywords |

### Tool 2 — `get_inventory_overview`

- **URL:** `.../api/telephony/tools/get_inventory_overview`  
- **Method:** `POST`  
- **Body:** empty `{}` or no parameters

### Tool 3 — `get_property_details`

- **URL:** `.../api/telephony/tools/get_property_details`  
- **Method:** `POST`  
- **Body:**

| Parameter | Type | Required |
|-----------|------|----------|
| `property_id` | string | yes (e.g. `KR-101`) |

### Tool 4 — `check_availability`

- **URL:** `.../api/telephony/tools/check_availability`  
- **Method:** `POST`  
- **Body:**

| Parameter | Type | Required |
|-----------|------|----------|
| `date` | string | yes — `YYYY-MM-DD` |
| `preferred_time` | string | no — `HH:MM` 24h IST |

### Tool 5 — `validate_email`

- **URL:** `.../api/telephony/tools/validate_email`  
- **Method:** `POST`  
- **Body:**

| Parameter | Type | Required |
|-----------|------|----------|
| `email` | string | yes — as caller said it |

### Tool 6 — `book_meeting`

- **URL:** `.../api/telephony/tools/book_meeting`  
- **Method:** `POST`  
- **Body:**

| Parameter | Type | Required |
|-----------|------|----------|
| `name` | string | yes |
| `email` | string | yes |
| `date` | string | yes — `YYYY-MM-DD` |
| `time` | string | yes — `HH:MM` IST |
| `property_id` | string | no |
| `property_name` | string | no |

4. **Save** the agent after all tools are added.

> **Do not add `end_call`** as a webhook — phone calls end when the caller hangs up.

---

## Part 3 — Connect Twilio number

Do this **in ElevenLabs**, not Twilio console (for this setup).

1. ElevenLabs → **Phone Numbers** (under Conversational AI)  
2. **Import** / **Add number** → **Twilio**  
3. Enter from your Twilio console:
   - **Account SID** — starts with `AC...`
   - **Auth Token**
4. Select your number: **+16614864467**  
5. **Assign agent** → pick **Karyan Receptionist — Sara**  
6. Save

ElevenLabs updates Twilio webhooks automatically.  
**Do not** set Twilio Voice URL to your backend — ElevenLabs owns the call.

---

## Part 4 — Test

### A. Test backend tool (on your PC)

```powershell
curl -X POST "http://127.0.0.1:8000/api/telephony/tools/get_inventory_overview" `
  -H "Authorization: Bearer karyan-telephony-7f3a9c2e1b8d4f6a" `
  -H "Content-Type: application/json" `
  -d "{}"
```

You should get JSON with Karyan listings.

### B. Test via public URL (what ElevenLabs uses)

```powershell
curl -X POST "https://YOUR-PUBLIC-URL/api/telephony/tools/get_inventory_overview" `
  -H "Authorization: Bearer karyan-telephony-7f3a9c2e1b8d4f6a" `
  -H "Content-Type: application/json" `
  -d "{}"
```

If this fails, ElevenLabs tools will fail too — fix tunnel/backend first.

### C. Test phone call

1. Call **+16614864467** from your mobile  
2. Sara should greet you in your chosen ElevenLabs voice  
3. Say: *"I'm looking for a 2 BHK in Ghaziabad around 50 lakh"*  
4. She should call `search_properties` and read results

---

## Checklist

- [ ] Agent created in ElevenLabs with prompt + first message  
- [ ] Voice selected in ElevenLabs  
- [ ] All 6 webhook tools added with correct URLs  
- [ ] `Authorization: Bearer ...` header on every tool  
- [ ] Backend running; public URL works (`/api/health`)  
- [ ] Twilio number imported in ElevenLabs and agent assigned  
- [ ] Test call works

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Call connects but Sara can't search properties | Tool URL wrong, or backend/tunnel down. Test curl to public URL. |
| `401 Unauthorized` on tools | Bearer token in ElevenLabs ≠ `TELEPHONY_WEBHOOK_SECRET` in `.env` |
| Call doesn't reach agent | Number not assigned to agent in ElevenLabs Phone Numbers |
| Booking fails | Run `python scripts/setup_google_auth.py` locally; calendar token must work on server |
| Sara speaks Hindi | Add to prompt: "English only" (already in setup kit prompt) |

---

## What you configure where

| Thing | Where |
|-------|--------|
| Agent personality + prompt | ElevenLabs agent editor |
| Voice | ElevenLabs voice picker |
| Twilio number → agent | ElevenLabs Phone Numbers |
| Property search + booking logic | Your backend (already built) |
| Tool webhook URLs | ElevenLabs tools → point to `/api/telephony/tools/...` |

Your current URLs are in **`data/elevenlabs_setup_kit.json`** → `server_tools` array.
