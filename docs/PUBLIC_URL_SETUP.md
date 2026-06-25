# Expose local backend for ElevenLabs webhooks

**For a URL that never changes and no open terminal:** deploy to the cloud → **`docs/DEPLOY.md`** (Render, ~10 min setup).

Local tunnels are only for quick testing — the URL changes every restart.

## Permanent fix (recommended)

Deploy once → fixed URL like `https://inbound-agent-api.onrender.com`  
Set ElevenLabs tool URLs **once**. No tunnel, no laptop needed for phone calls.

See **`docs/DEPLOY.md`**.

---

## Temporary local tunnels (testing only)

## Option A — Cloudflare Tunnel (recommended, free)

1. Download cloudflared: https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
2. Start your backend:
   ```powershell
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```
3. In another terminal:
   ```powershell
   cloudflared tunnel --url http://localhost:8000
   ```
4. Copy the `https://....trycloudflare.com` URL it prints.
5. Put in `.env`:
   ```env
   API_PUBLIC_URL=https://xxxx.trycloudflare.com
   ```
6. Re-run `python scripts/export_elevenlabs_setup.py` so tool URLs use the new host.

> URL changes each time you restart cloudflared (unless you set up a named tunnel).

---

## Option B — LocalTunnel (if you have Node.js)

```powershell
# Terminal 1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2
npx localtunnel --port 8000
```

Use the `https://....loca.lt` URL as `API_PUBLIC_URL`.

---

## Option C — Deploy backend (stable URL, best for real use)

Deploy FastAPI to **Railway**, **Render**, or **Fly.io** (free tiers exist).

Set env vars there (`OPENAI_API_KEY`, `TELEPHONY_WEBHOOK_SECRET`, Google tokens, etc.) and use the deployed URL:

```env
API_PUBLIC_URL=https://your-app.onrender.com
```

No tunnel needed while the service is running.

---

## Option D — ngrok

Only if you already use it:

```powershell
ngrok http 8000
```

---

## After you have a public URL

1. Update `.env` → `API_PUBLIC_URL`
2. Restart uvicorn
3. `python scripts/export_elevenlabs_setup.py`
4. Paste tool URLs into ElevenLabs (they must use the **same** `API_PUBLIC_URL`)

Test:

```powershell
curl https://YOUR-PUBLIC-URL/api/health
```

Should return `{"status":"ok",...}`.
