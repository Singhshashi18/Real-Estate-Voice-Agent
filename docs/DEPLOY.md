# Deploy for a fixed public URL (no tunnel, no terminal)

Local tunnels change URL every restart. **Deploy the API once** and use a permanent URL in ElevenLabs.

Recommended: **[Render](https://render.com)** (free tier) — URL like `https://inbound-agent-api.onrender.com`

## 1. Push code to GitHub

Your repo must be on GitHub (Render connects to it).

## 2. Pack Google token for cloud

On your PC (after `python scripts/setup_google_auth.py`):

```powershell
python scripts/pack_google_token.py
```

Copy the one-line output — you'll paste it as `GOOGLE_TOKEN_JSON` on Render.

## 3. Deploy on Render

1. [dashboard.render.com](https://dashboard.render.com) → **New** → **Blueprint**
2. Connect your GitHub repo → Render reads `render.yaml`
3. Or **New Web Service** → Docker → point at this repo
4. Set **Environment Variables**:

| Variable | Value |
|----------|--------|
| `OPENAI_API_KEY` | your key |
| `API_PUBLIC_URL` | `https://YOUR-SERVICE-NAME.onrender.com` (set after first deploy) |
| `TELEPHONY_WEBHOOK_SECRET` | same secret as in ElevenLabs tools |
| `GOOGLE_TOKEN_JSON` | one line from `pack_google_token.py` |
| `ORGANIZER_NAME` | Sara |
| `COMPANY_NAME` | Karyan |
| `JWT_SECRET` | long random string |
| `FRONTEND_URL` | your frontend URL (optional) |

5. Deploy → copy your service URL
6. Update `API_PUBLIC_URL` to that exact URL → **Redeploy** once

## 4. Update ElevenLabs (one time only)

Tool URLs become permanent:

```
https://YOUR-SERVICE-NAME.onrender.com/api/telephony/tools/search_properties
... (same 6 tools)
```

Header on every tool:
```
Authorization: Bearer YOUR_TELEPHONY_WEBHOOK_SECRET
```

Re-run locally if you want a fresh kit file:
```powershell
# Set API_PUBLIC_URL in .env to your Render URL first
python scripts/export_elevenlabs_setup.py
```

## 5. Test

```powershell
curl https://YOUR-SERVICE-NAME.onrender.com/api/health
```

Call your Twilio number — tools hit Render, not your laptop.

## Notes

- **Free Render** sleeps after ~15 min idle — first webhook may be slow (~30s). Upgrade to Starter ($7/mo) for always-on.
- **No tunnel terminal** needed after deploy.
- Browser voice agent can still run locally; phone tools use the cloud API.
- Keep `TELEPHONY_WEBHOOK_SECRET` private.

## Alternatives

| Platform | Fixed URL | Always on |
|----------|-----------|-----------|
| Render (free) | Yes | Sleeps when idle |
| Render (Starter) | Yes | Yes |
| Railway | Yes | Pay-as-you-go |
| Fly.io | Yes | Free allowance |

Dockerfile in repo works on any of these.
