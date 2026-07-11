# LeadForge AI Agency — Project Spec

**Status:** Requirements gathering — no code written yet, pending Aditya's explicit go-ahead
**Last updated:** July 5, 2026

---

## 1. Business Context

- **Product:** banaocv.in — an affordable, ATS-friendly resume builder aimed at freshers and students.
- **Goal:** Build "LeadForge," an 8-agent AI backend that automates marketing, sales, and operations for banaocv.in.
- **Interface:** A private "CEO Admin Dashboard" where Aditya monitors agents, reviews real-time activity, and approves/edits/rejects agent-drafted output before it goes out (Human-in-the-Loop).

## 2. Reference Materials Provided

**`agency-agents-main.zip`** — this is **"The Agency"** (github.com/msitarzewski/agency-agents), MIT licensed. Important finding: **it is not a runtime framework.** It's a library of ~250 markdown "expert persona" system prompts meant to be installed into AI coding tools (Claude Code, Cursor, Copilot, Gemini CLI, etc.) so a developer gets specialized help *while coding*. There is no autonomous execution engine, scheduler, scraper, or messaging code anywhere in it — just persona prompts plus install/convert tooling.

- Several of LeadForge's 8 agent names are clearly drawn from this repo's filenames: `project-management-project-shepherd.md`, `specialized/sales-outreach.md`, `specialized/sales-data-extraction-agent.md`, `marketing/marketing-growth-hacker.md`, `marketing/marketing-seo-specialist.md`, `marketing-social-media-strategist.md` + `marketing-content-creator.md`, `engineering/engineering-frontend-developer.md`, `support/support-support-responder.md`.
- Notably, in the *source* material: "Sales Data Extraction Agent" parses internal Excel sales reports (MTD/YTD) — it has nothing to do with scraping external platforms. "Sales Outreach" describes ethical, research-based B2B methodology (personalize from real research, never misrepresent, no spray-and-pray, respect the prospect's time) — it does not describe or endorse scraping or mass automated DMs anywhere. Those specifics were added on top by whoever drafted the LeadForge brief.
- **Practical use going forward:** won't be the runtime backend, but individual persona files are good seed text for our own CrewAI agents' `goal`/`backstory` fields, and can optionally be installed into a coding tool for extra help while building LeadForge itself.

**`Nexus • CEO AI Command Center`** (HTML mockup) — visual/structural reference for LeadForge's dashboard. Currently pure front-end mockup: all data is fake, generated client-side via JS arrays/`setInterval`, no backend wired up.

## 3. Dashboard Design Direction (from Nexus reference)

- Dark theme, glassmorphism panels, neon accents (emerald/blue/amber/red), Inter + JetBrains Mono fonts.
- **Top bar:** brand mark, live system-status pill, notifications, profile.
- **Left sidebar:** agent roster (status dot: active/idle/blocked + task count + mini progress bar), fleet health (CPU, token budget, task success rate).
- **Main grid:** KPI cards with sparklines; real-time activity/log feed (terminal-style, filterable per agent, pause/resume); Approval Queue panel (Approve/Edit/Reject, priority badge, confidence %).
- **Bottom:** multi-series performance chart; scheduled-missions timeline.
- Aditya wants this visual language carried forward, rebuilt around the real 8 agents with real data, with room for Claude's own design judgment on top.

## 4. The 8 Agents

| # | Agent | Role | Status |
|---|-------|------|--------|
| 1 | **Project Shepherd** (Orchestrator) | Assigns tasks to the other 7, checks work, routes output to Approval Queue | ✅ Buildable as-is |
| 2 | **Sales Outreach Specialist** | Drafts short, high-converting messages offering free resume creation | ⚠️ Buildable — compliant channels only (see §7) |
| 3 | **Growth Hacker** | Zero-budget viral loops, referral mechanics, growth experiments | ✅ Buildable as-is |
| 4 | **SEO Specialist** | Keyword strategy, meta tags, SEO to rank banaocv.in | ✅ Buildable as-is |
| 5 | **Content Creator & Social Media Strategist** | Reels/Shorts scripts, trending formats + humor for freshers | ✅ Buildable as-is |
| 6 | **Frontend Developer** | HTML/Tailwind/JS for dashboard & website features | ✅ Buildable as-is |
| 7 | **Data Extraction Agent** | Builds structured lead databases | ⚠️ Buildable — compliant sources only (see §7) |
| 8 | **Customer Support Responder** | Drafts replies to user queries about the resume builder | ✅ Buildable as-is |

## 5. Technical Requirements So Far

- **Backend framework:** CrewAI (Python) recommended — its role/goal/backstory model plus hierarchical process maps directly onto "Orchestrator manages 7 specialist agents." (Independent recommendation — not something the zip validates one way or other, since it contains no runtime code.)
- **LLM provider:** Google AI Studio (Gemini) free-tier API key. Needs a dedicated **Settings/Model Config** section in the dashboard where Aditya pastes the key, which then powers all 8 agents' LLM calls.
- **Hosting:** Decided — **Render** (free tier). Deploys directly from Aditya's GitHub repo (push to deploy, no Docker/CLI needed), no credit card required, native Python support. Trade-off: free web services sleep after 15 min of inactivity (~30-60s cold start on the next request) — acceptable for now since the dashboard isn't yet serving live customers 24/7. CrewAI is Python, so it could never have run on Google Apps Script the way the House of Panchhi HR system's backend does.
- Dashboard needs to move from fake `setInterval` data to real agent-driven data.

## 6. Open Questions

- [x] ~~Where does the Python backend run~~ → **Render (free tier)**, see §5.
- [x] ~~Direction for Data Extraction + Sales Outreach agents~~ → **Decided.** Own-site opt-ins (ATS Score Checker, abandoned sessions) + college placement-cell directory only. LinkedIn Sales Navigator dropped entirely — it needs an attended human session to run safely, which conflicts with Aditya's requirement that the system keep working even when he isn't there. See `leadforge-overview.md` for the friend-facing writeup.
- [x] ~~Does banaocv.in have opt-in capture~~ → **Confirmed (checked live site).** Google/email signup+login already exists, resumes already save to account. ATS Score Checker exists but is currently **Premium-only** (₹99), not free — can't use it as a free lead magnet as originally assumed without building a lightweight free version first.
- [x] ~~banaocv.in tech stack~~ → Looks like a plain multi-page HTML/JS site (`editor.html`, `templates.html`, no SPA framework signature) — same style as the House of Panchhi HR system. Uses Razorpay for payments.
- [x] **Major finding:** banaocv.in already has a **"Pro Team" ₹299/month tier** built specifically for placement cells (bulk resume generation, up to 10 team members, analytics dashboard, API access, contact via pro@banaocv.in). Sales Outreach's placement-cell pitch has a real, already-priced product to sell — nothing new to build there.

## 7. Flagged Considerations

**Data Extraction Agent + Sales Outreach Specialist, as originally scoped** (scrape LinkedIn/Instagram/job portals → send automated "personalized" DMs at scale) carry two real risks:

1. **Platform ToS:** LinkedIn's and Instagram's User Agreements explicitly prohibit automated scraping and automated messaging. Easy for their systems to detect; account bans/restrictions are a real possibility, which would hurt the banaocv.in brand directly.
2. **Legal/regulatory:** India's IT Act and the 2023 DPDP Act restrict collecting personal data without consent and sending unsolicited commercial messages. Separately, recipients would reasonably believe a human researched them individually when the message is actually templated bulk output from scraped data.

**Plan:** Claude won't build the LinkedIn/Instagram scraping or automated mass-DM mechanics. Everything else about these two roles — message copywriting, lead-data schema, Approval Queue integration, and compliant acquisition channels — is fully in scope and achieves the same underlying goal.

**Concrete compliant redesign, given banaocv.in's specific audience (freshers concentrated in identifiable colleges):**

1. **College placement-cell (TPO) partnerships — likely the highest-leverage channel.** Every college publishes placement-cell contact info specifically for outside companies/services to reach out — public B2B contact info, not scraped personal data. One partnership puts banaocv.in in front of an entire graduating batch at once.
2. **On-site opt-in capture.** The SEO + Content agents are already planned to drive organic traffic; convert it with on-site lead magnets ("Free ATS Score Checker", "Free Resume Review") that ask for name + email — fully consent-based.
3. **Abandoned-session recovery.** Anyone who starts a resume on banaocv.in and doesn't finish (having left an email to save progress) can get a reminder — first-party engagement, not cold outreach to a stranger.
4. **LinkedIn Sales Navigator + InMail.** If LinkedIn specifically matters, Sales Navigator's own search/filter tools plus InMail credits let Aditya reach freshers by criteria (college, batch, skills) fully within LinkedIn's ToS.
5. **Community engagement.** Already planned via the Growth Hacker's Reddit strategy — value-first participation, not disguised spam.

Status: **Decided** — see §6 and `leadforge-overview.md`.

## 8. Cost Breakdown (checked July 2026)

| Item | Cost |
|---|---|
| Render hosting (backend) | ₹0 — free tier, no card |
| Gemini API via AI Studio key | ₹0 — free tier: ~1,500 requests/day, Flash models only. Limits are set by Google and have shifted a few times over the past year; check the live limit in AI Studio rather than assuming these hold forever. Paid Flash pricing (if ever needed) is very cheap. |
| Dashboard hosting | ₹0 — static, can sit on Render or GitHub Pages |
| Domain | ₹0 — banaocv.in already owned |
| Compliant lead channels (§7: placement cells, opt-in forms, abandoned-session recovery, community posts) | ₹0 |
| *Optional:* LinkedIn Sales Navigator Core (only if that channel is chosen later) | ~$99–120/mo (~₹8,000–10,000/mo) |

**Bottom line: the core system runs at ₹0/month.** The only real cost on the table is Sales Navigator, and it's optional — the free compliant channels look more promising for banaocv.in's audience anyway.

## 9. Build Log

- **v0.1 — Dashboard shell built** (`leadforge-dashboard.html`): dark command-center UI, all 8 agents represented (Project Shepherd shown as orchestrator above the other 7), Settings panel with a working Gemini key connection (tests the key live via `gemini-flash-latest`, has Shepherd greet Aditya on success), Approval Queue + Activity Feed with compliant-flavored example content, honest "Preview mode" labeling since no backend exists yet, and a Build Roadmap card showing real progress instead of fake data. Key is kept in browser memory only for this session — never saved, never sent anywhere but Google.
- Not yet built: the 8 Python/CrewAI agent backends, the Render deployment, real data flowing into the dashboard.

## 10. Process Rules (explicit from Aditya)

- No code until Aditya explicitly says go.
- Claude keeps this document updated as new requirements/decisions come up.
- Full spec shared any time Aditya asks for it.
