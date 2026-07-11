# LeadForge Backend

The Python backend for LeadForge — 8 CrewAI agents for banaocv.in, backed by
Google Gemini (free tier) with automatic fallback to NVIDIA NIM (also free)
the moment Gemini's daily quota runs out.

## What you need before deploying
1. **Gemini API key** — from aistudio.google.com (you already have this)
2. **NVIDIA API key** — free, from build.nvidia.com:
   - Sign up (no credit card)
   - Verify your phone number (required for key generation)
   - Generate a key — it starts with `nvapi-`
3. A **GitHub repo** to push this folder to
4. A free **Render** account (render.com), connected to that GitHub repo

## Run locally first (optional but recommended)
```
pip install -r requirements.txt
cp .env.example .env      # then fill in your two real keys
uvicorn main:app --reload
```
Visit http://localhost:8000/status — you should see `"configured": true` for
Gemini (and for NVIDIA once you've added that key too).

## Deploy to Render (free)
1. Push this folder to a GitHub repo
2. On render.com: **New → Web Service** → connect that repo
3. Render should auto-detect Python. If it asks:
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Under **Environment**, add `GEMINI_API_KEY` and `NVIDIA_API_KEY` with your
   real keys (never commit real keys to GitHub — `.env` is for local use only)
5. Deploy. Render gives you a live URL, something like
   `https://leadforge-backend.onrender.com`
6. Paste that URL into the dashboard's Settings panel (new "Backend URL"
   field) so the dashboard can show live provider + usage status

## Files
- `llm_router.py` — the Gemini → NVIDIA fallback logic + usage tracking
- `agents_config.py` — the 8 agent definitions (CrewAI) and the same fallback
  applied to actual agent task runs
- `main.py` — the API the dashboard talks to

## Honest current scope
This gives you a working 8-agent backend with real LLM calls and real
automatic failover. It does **not** yet pull real data from banaocv.in
(signups, abandoned sessions, placement-cell list) — that's the next piece,
and needs read access to banaocv.in's own database or a small API on that
side to expose it safely.
