"""
Real activity log + a background scheduler that runs a couple of agents
automatically every few minutes — so the dashboard has genuine output to
show instead of only reacting to manual button clicks.

Deliberately simple for now: everything lives in memory, so a redeploy or
a Render free-tier restart clears it. The natural upgrade once banaocv.in's
own data source is wired in is to swap this for something persistent (a
Google Sheet, matching how the House of Panchhi HR system stores data,
would be a very natural fit here too).
"""

import threading
import time
from datetime import datetime

from agents_config import run_agent_task

MAX_LOG_ENTRIES = 200
RUN_EVERY_SECONDS = 600  # 10 minutes — easy to change once this feels right

activity_log = []
_log_lock = threading.Lock()

# Only agents that don't need banaocv.in's real data yet — Growth Hacker
# and Content Creator can produce genuinely useful output on their own.
SCHEDULED_TASKS = [
    {
        "agent": "growth",
        "label": "Growth Hacker",
        "task": (
            "Come up with one specific, zero-budget growth idea banaocv.in "
            "could try this week to get more freshers signing up. Be concrete, "
            "not generic — name the actual mechanic."
        ),
        "expected_output": "2-3 sentences describing one specific, actionable idea.",
    },
    {
        "agent": "content",
        "label": "Content Creator",
        "task": (
            "Write one short Instagram Reel concept (a hook line plus what "
            "happens in the video) aimed at Indian college freshers about a "
            "resume mistake. Relatable, a little funny, no corporate tone."
        ),
        "expected_output": "A hook line, then 2-3 sentences describing the Reel.",
    },
]


def _log(agent_key: str, label: str, text: str, provider: str):
    with _log_lock:
        activity_log.append({
            "time": datetime.now().strftime("%H:%M:%S"),
            "agent": agent_key,
            "label": label,
            "text": text,
            "provider": provider,
        })
        while len(activity_log) > MAX_LOG_ENTRIES:
            activity_log.pop(0)


def _run_once():
    for item in SCHEDULED_TASKS:
        try:
            result = run_agent_task(item["agent"], item["task"], item["expected_output"])
            _log(item["agent"], item["label"], result["output"], result["provider"])
        except Exception as e:
            _log(item["agent"], item["label"], f"Run failed: {e}", "none")


def _scheduler_loop(interval_seconds: int):
    while True:
        _run_once()
        time.sleep(interval_seconds)


def start_scheduler(interval_seconds: int = RUN_EVERY_SECONDS):
    """Runs both scheduled agents once immediately, then again every
    interval_seconds, forever, in a background thread."""
    t = threading.Thread(target=_scheduler_loop, args=(interval_seconds,), daemon=True)
    t.start()


def get_activity():
    with _log_lock:
        return list(reversed(activity_log))  # newest first
