"""
Defines the LeadForge 8-agent roster using CrewAI. run_agent_task() builds
a one-agent crew backed by Gemini, runs the task, and — if that fails for
any reason (including Gemini's quota running out) — automatically rebuilds
the same crew backed by NVIDIA NIM and retries once.
"""

import os
from crewai import Agent, Task, Crew, Process, LLM

from llm_router import router, GEMINI_MODEL, NVIDIA_MODEL


def _gemini_llm():
    # CrewAI's "native" gemini/ integration has a long history of bugs across
    # litellm versions (mangled model prefixes, "LLM Provider NOT provided"
    # errors, etc. — see crewAIInc/crewai issues #2645, #3702, #3109).
    # CrewAI's own docs recommend routing through Gemini's OpenAI-compatible
    # endpoint instead, which is far more reliable — same pattern as NVIDIA below.
    return LLM(
        model=f"openai/{GEMINI_MODEL}",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.environ.get("GEMINI_API_KEY", ""),
    )


def _nvidia_llm():
    # "openai/<model>" + a custom base_url is the standard way to point
    # CrewAI/LiteLLM at any OpenAI-compatible endpoint — which is exactly
    # what NVIDIA NIM advertises itself as.
    return LLM(
        model=f"openai/{NVIDIA_MODEL}",
        base_url="https://integrate.api.nvidia.com/v1",
        api_key=os.environ.get("NVIDIA_API_KEY", ""),
    )


AGENT_DEFINITIONS = {
    "shepherd": dict(
        role="Project Shepherd — Orchestrator",
        goal="Keep the other 7 LeadForge agents pointed at banaocv.in's goals, review their output, and decide what's ready for Aditya's Approval Queue.",
        backstory=(
            "You lead a small AI marketing & ops team for banaocv.in, an affordable ATS-friendly "
            "resume builder for freshers. You never contact a lead directly — you assign work to "
            "specialists and check their output before it reaches Aditya."
        ),
    ),
    "outreach": dict(
        role="Sales Outreach Specialist",
        goal="Write short, warm, honest messages to people who already engaged with banaocv.in (an abandoned draft, an opt-in signup), or to college placement cells about the Pro Team plan — never a cold stranger.",
        backstory=(
            "You write outreach for banaocv.in. Every message is for someone who already interacted "
            "with the product, or a placement cell that publishes its own contact info for exactly "
            "this kind of outreach. You never buy, scrape, or guess at leads."
        ),
    ),
    "growth": dict(
        role="Growth Hacker",
        goal="Propose zero-budget growth ideas for banaocv.in: referral mechanics and value-first community posts.",
        backstory="You've grown bootstrapped Indian consumer products with no ad budget, using referral loops and genuine community participation instead of spend.",
    ),
    "seo": dict(
        role="SEO Specialist",
        goal="Identify what freshers actually search for and turn that into ranking content and metadata for banaocv.in.",
        backstory="You've ranked resume and career sites in India by writing for real search intent instead of chasing generic keywords.",
    ),
    "content": dict(
        role="Content Creator & Social Media Strategist",
        goal="Script short-form video and social content aimed at Indian freshers and college students — relatable, current, a little funny.",
        backstory="You've written scripts that travel well in Indian college WhatsApp groups and Instagram — plain language, real pain points, no corporate tone.",
    ),
    "frontend": dict(
        role="Frontend Developer",
        goal="Turn feature requests for banaocv.in or the LeadForge dashboard into clear, specific implementation notes.",
        backstory="You build clean, fast, mobile-first interfaces and always flag exactly what a change will touch before it's built.",
    ),
    "data": dict(
        role="Data Extraction Agent",
        goal="Keep a clean, structured, consent-based record of who might want banaocv.in: opt-in signups, abandoned sessions, and a college placement-cell contact directory.",
        backstory=(
            "You only ever work with data people gave banaocv.in directly, or contact information "
            "colleges publish specifically for outside outreach. You never touch LinkedIn, Instagram, "
            "or anyone's private profile."
        ),
    ),
    "support": dict(
        role="Customer Support Responder",
        goal="Draft clear, kind replies to banaocv.in user questions and issues.",
        backstory="You've handled support for consumer products where the user is often stressed about a job deadline — calm, specific, fast.",
    ),
}


def _build_agent(key: str, llm: LLM) -> Agent:
    d = AGENT_DEFINITIONS[key]
    return Agent(role=d["role"], goal=d["goal"], backstory=d["backstory"], llm=llm, verbose=False)


def run_agent_task(agent_key: str, task_description: str, expected_output: str) -> dict:
    """Runs one task on one agent. Tries Gemini first, falls back to NVIDIA
    on failure. Returns {"output": str, "provider": "gemini"|"nvidia"}."""
    errors = {}
    for provider, build_llm in (("gemini", _gemini_llm), ("nvidia", _nvidia_llm)):
        try:
            agent = _build_agent(agent_key, build_llm())
            task = Task(description=task_description, expected_output=expected_output, agent=agent)
            crew = Crew(agents=[agent], tasks=[task], process=Process.sequential, verbose=False)
            result = crew.kickoff()

            tokens_used = 0
            try:
                tokens_used = result.token_usage.total_tokens
            except Exception:
                pass
            router.record_external_usage(provider, tokens_used)

            return {"output": str(result), "provider": provider}
        except Exception as e:
            errors[provider] = str(e)
            router.last_error = f"{provider}: {e}"
            continue
    # Both failed — surface both reasons clearly instead of only the last one.
    detail = " | ".join(f"{p}: {msg}" for p, msg in errors.items())
    router.last_error = detail
    raise RuntimeError(f"Both providers failed — {detail}")
