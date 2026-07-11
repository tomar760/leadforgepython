"""
LLMRouter: calls Google Gemini first (free tier). If Gemini's daily quota
looks exhausted, or a call fails for any reason, this automatically falls
back to NVIDIA NIM (also free, from build.nvidia.com). Tracks how many
requests + tokens each provider has used today, and which provider is
currently active — the dashboard reads all of this via GET /status.

This file has no dependency on CrewAI and can be tested completely on its
own:

    python llm_router.py
"""

import os
from datetime import date
from threading import Lock

import requests

GEMINI_MODEL = "gemini-flash-latest"          # alias Google keeps pointed at its current recommended free Flash model
NVIDIA_MODEL = "meta/llama-3.1-8b-instruct"   # swap for any model listed free at https://build.nvidia.com/models

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
NVIDIA_URL = "https://integrate.api.nvidia.com/v1/chat/completions"

# Gemini's free-tier daily request cap shifts occasionally — this is a
# conservative mid-2026 estimate. If the fallback triggers sooner or later
# than expected in practice, check the live number in Google AI Studio and
# update this constant.
GEMINI_DAILY_REQUEST_LIMIT = 1500


class LLMRouter:
    def __init__(self):
        self.gemini_key = os.environ.get("GEMINI_API_KEY", "")
        self.nvidia_key = os.environ.get("NVIDIA_API_KEY", "")
        self._lock = Lock()
        self._usage = {
            "date": str(date.today()),
            "gemini": {"requests": 0, "tokens": 0},
            "nvidia": {"requests": 0, "tokens": 0},
        }
        self.last_provider = None
        self.last_error = None

    # ---------- public API ----------

    def generate(self, prompt: str, system: str = "") -> dict:
        """Returns {"text", "provider", "tokens"}. Tries Gemini first;
        falls back to NVIDIA on any failure or once today's Gemini request
        budget looks used up."""
        self._roll_over_day_if_needed()

        gemini_looks_available = (
            bool(self.gemini_key)
            and self._usage["gemini"]["requests"] < GEMINI_DAILY_REQUEST_LIMIT
        )

        if gemini_looks_available:
            try:
                result = self._call_gemini(prompt, system)
                self.last_provider = "gemini"
                self.last_error = None
                return result
            except Exception as e:
                # Deliberately broad: a real 429, a network hiccup, a
                # changed response shape — all of it should fall through to
                # NVIDIA rather than stop the team from working.
                self.last_error = f"gemini: {e}"

        if not self.nvidia_key:
            raise RuntimeError(
                "Gemini is unavailable right now and no NVIDIA_API_KEY is "
                "configured. Add a free key from https://build.nvidia.com "
                "to enable the fallback."
            )

        result = self._call_nvidia(prompt, system)
        self.last_provider = "nvidia"
        self.last_error = None
        return result

    def record_external_usage(self, provider: str, tokens: int):
        """Lets other modules (like the CrewAI agent runner) fold their
        token usage into these same counters, so /status reflects everything,
        not just calls made directly through generate()."""
        self._roll_over_day_if_needed()
        with self._lock:
            self._usage[provider]["requests"] += 1
            self._usage[provider]["tokens"] += tokens
        self.last_provider = provider

    def status(self) -> dict:
        self._roll_over_day_if_needed()
        return {
            "date": self._usage["date"],
            "active_provider": self.last_provider or "none-yet",
            "last_error": self.last_error,
            "gemini": {
                **self._usage["gemini"],
                "daily_limit": GEMINI_DAILY_REQUEST_LIMIT,
                "requests_left": max(0, GEMINI_DAILY_REQUEST_LIMIT - self._usage["gemini"]["requests"]),
                "configured": bool(self.gemini_key),
            },
            "nvidia": {
                **self._usage["nvidia"],
                "configured": bool(self.nvidia_key),
            },
        }

    # ---------- internals ----------

    def _roll_over_day_if_needed(self):
        today = str(date.today())
        with self._lock:
            if self._usage["date"] != today:
                self._usage = {
                    "date": today,
                    "gemini": {"requests": 0, "tokens": 0},
                    "nvidia": {"requests": 0, "tokens": 0},
                }

    def _call_gemini(self, prompt, system):
        text_in = (system + "\n\n" + prompt) if system else prompt
        resp = requests.post(
            GEMINI_URL,
            headers={"Content-Type": "application/json", "x-goog-api-key": self.gemini_key},
            json={"contents": [{"parts": [{"text": text_in}]}]},
            timeout=45,
        )
        if resp.status_code == 429:
            raise RuntimeError("Gemini free-tier limit reached for today")
        resp.raise_for_status()
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        tokens = data.get("usageMetadata", {}).get("totalTokenCount", 0)
        with self._lock:
            self._usage["gemini"]["requests"] += 1
            self._usage["gemini"]["tokens"] += tokens
        return {"text": text, "provider": "gemini", "tokens": tokens}

    def _call_nvidia(self, prompt, system):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        resp = requests.post(
            NVIDIA_URL,
            headers={"Authorization": f"Bearer {self.nvidia_key}", "Content-Type": "application/json"},
            json={"model": NVIDIA_MODEL, "messages": messages, "max_tokens": 1024},
            timeout=45,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        tokens = data.get("usage", {}).get("total_tokens", 0)
        with self._lock:
            self._usage["nvidia"]["requests"] += 1
            self._usage["nvidia"]["tokens"] += tokens
        return {"text": text, "provider": "nvidia", "tokens": tokens}


# a single shared instance the rest of the app imports
router = LLMRouter()


if __name__ == "__main__":
    r = router.generate("Say hello in one short sentence.", system="You are Project Shepherd.")
    print(r)
    print(router.status())
