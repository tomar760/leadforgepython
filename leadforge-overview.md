# LeadForge — What It Is & How It Works

**For:** banaocv.in — an affordable, ATS-friendly resume builder for freshers and students
**In one line:** An 8-agent AI team that handles marketing, sales, and support for banaocv.in — always running in the cloud, never dependent on anyone's laptop being on. Every agent drafts; nothing goes out until Aditya approves it.

---

## The big picture

All 8 agents run on a small always-on server (Render), not on anyone's computer — so they keep working overnight, on weekends, whenever. They all "think" using Google's Gemini AI. One agent (Project Shepherd) manages the other 7 and checks their work. Whatever any agent produces that's customer-facing — a message, a post, a reply — lands in an Approval Queue on the dashboard. Aditya can open that dashboard from any device and Approve, Edit, or Reject. Nothing is ever sent automatically without that click.

**Status right now:** the dashboard (what Aditya sees and clicks) is built. The backend that actually runs the 8 agents is the next thing to build.

---

## The 8 agents

### 1. Project Shepherd — the manager
Assigns work to the other 7 agents, reviews what they produce, and routes anything ready for the outside world into the Approval Queue. The one agent that talks to all the others.

### 2. Data Extraction Agent — finds people who might need a resume
Does **not** pull data from LinkedIn, Instagram, or anyone's private profile. Instead it tracks:
- Anyone who uses the free "ATS Score Checker" or "Resume Review" tool on banaocv.in and opts in
- Anyone who starts building a resume and doesn't finish — so they can be reminded about their own saved draft
- A directory of college placement-cell contacts — public information colleges publish specifically so companies and services can reach out

### 3. Sales Outreach Specialist — writes the outreach
Only ever writes to the people the Data Extraction Agent above found — never a cold stranger pulled from a scraped profile. Examples of what it drafts:
- "You left your resume 80% done — want to pick it back up?" → to someone's own abandoned session
- "Free resume builder for your graduating batch" → to a college placement cell
Every message waits in the Approval Queue for a human click before it's sent.

### 4. Growth Hacker
Comes up with zero-budget growth ideas: referral mechanics (e.g. "3 referrals unlocks a premium template"), and value-first posts for communities like r/developersIndia. Drafts go through approval before anything is posted.

### 5. SEO Specialist
Figures out what freshers actually search for ("free resume builder for freshers", "ATS resume checker") and writes/optimizes blog content and page metadata so banaocv.in ranks for those searches.

### 6. Content Creator & Social Media Strategist
Writes scripts for Instagram/YouTube Reels aimed at freshers and students — relatable, trend-aware, a little funny — to build an audience organically.

### 7. Frontend Developer
Writes the actual code whenever a new feature or fix is needed on the website or the dashboard.

### 8. Customer Support Responder
Drafts replies when a user has trouble downloading their resume or has a question. Same rule as everyone else — Aditya approves before it goes out.

---

## Why compliant channels instead of scraping

The original idea included pulling data directly from LinkedIn and Instagram. Two reasons that changed:
1. **Platform risk** — both platforms' user agreements explicitly prohibit automated scraping and automated messaging, and can lead to account bans.
2. **It has to run unattended** — LinkedIn-based tools generally need a real, logged-in human session to work safely, which conflicts with the goal of the system running 24/7 without anyone watching it. The channels above (own website data, placement cells) don't have that problem — they're fully automatable and carry no ban risk.

## How it's hosted

- **Backend:** Python (CrewAI framework) on Render — free tier, always on
- **AI:** Google Gemini, via a free Google AI Studio key
- **Dashboard:** works from any browser, on any device — not tied to a specific laptop
- **Cost:** ₹0/month to run at this stage
