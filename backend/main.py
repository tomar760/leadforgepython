"""
LeadForge backend API. Exposes:
  GET  /status                   -> which LLM provider is active + usage today
  GET  /agents                   -> the 8-agent roster
  POST /agents/{agent_key}/run   -> run one task through that agent (Gemini, falls back to NVIDIA)

Run locally:   uvicorn main:app --reload
Deploy:        see README.md for the Render steps.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from llm_router import router
from agents_config import AGENT_DEFINITIONS, run_agent_task
from activity import start_scheduler, get_activity

app = FastAPI(title="LeadForge Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your dashboard's real origin once it has one
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def _on_startup():
    start_scheduler()  # runs Growth Hacker + Content Creator now, then every 10 min


@app.get("/")
def root():
    return {"service": "LeadForge backend", "status": "running"}


@app.get("/status")
def status():
    return router.status()


@app.get("/activity")
def activity():
    return get_activity()


@app.get("/agents")
def list_agents():
    return [{"id": key, "role": d["role"], "goal": d["goal"]} for key, d in AGENT_DEFINITIONS.items()]


class RunRequest(BaseModel):
    task: str
    expected_output: str = "A clear, complete response."


@app.post("/agents/{agent_key}/run")
def run_agent(agent_key: str, body: RunRequest):
    if agent_key not in AGENT_DEFINITIONS:
        raise HTTPException(404, f"No agent called '{agent_key}'. Try one of {list(AGENT_DEFINITIONS)}")
    try:
        return run_agent_task(agent_key, body.task, body.expected_output)
    except Exception as e:
        raise HTTPException(500, str(e))
