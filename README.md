# Agentic Internship Auto‑Applier — 12‑Hour MVP

A small, focused system that discovers relevant early‑career roles, tailors applications to the candidate’s CV and the company’s values, and autofills forms on Greenhouse and Lever with a human‑approval gate.

> **Why this scope**: Greenhouse and Lever share predictable HTML patterns and have fewer blockers than Workday/Taleo. We get a real end‑to‑end demo without fighting captchas or MFA. Other ATS are supported via a “handoff” flow (open link, clipboard package, drafts).

---

## 1) Goals 

**Goals**

* Discover new roles at a curated list of target companies (Greenhouse/Lever focus).
* Parse an extended CV into structured JSON for retrieval.
* Profile company values from About/Careers pages.
* Generate a tailored cover letter and short answers grounded in the CV and company values.
* Autofill and submit where possible; fall back to a handoff flow when blocked.
* Maintain an approval gate with a transparent checklist of submitted fields and stored screenshots.

## 2) System Overview

**Orchestrator**: FastAPI service that routes tasks, persists state in SQLite, and exposes a simple dashboard.

**Agents** (plain Python modules, called via the orchestrator):

1. **CV Parser** → CV JSON
2. **Job Scout** → Jobs JSON (Greenhouse/Lever)
3. **Match & Gate** → accept | manual_review | reject
4. **Company Profiler** → values/hooks JSON with sources
5. **Tailor** → cover letter + short answers + evidence map
6. **Form Filler** → autofill on Greenhouse/Lever + screenshots
7. **Follow‑Up** → email drafts and reminders
8. **Compliance Gatekeeper** → approval checklist JSON

**UI**: single‑page dashboard (FastAPI + Jinja or Vite React) with three columns: New Roles, Tailored Draft, Ready to Submit. Submissions table with screenshots.

**Notifications**: Slack/Discord webhooks for events.

---

## 3) Data Contracts

### Candidate JSON

```json
{
  "id": "cand_001",
  "name": "Example Candidate",
  "contact": {"email": "", "phone": ""},
  "constraints": {
    "location": ["London", "UK"],
    "seniority": ["Intern", "Spring Week"],
    "keywords_include": ["software", "ml", "platform"],
    "keywords_exclude": ["senior", "5+ years"]
  },
  "cv_bullets": ["..."],
  "skills": ["Python", "React", "Flask", "Playwright"],
  "education": ["..."],
  "projects": [{"name": "Project A", "bullets": ["..."]}]
}
```

### Job JSON

```json
{
  "id": "job_gh_123",
  "company": "Company A",
  "platform": "greenhouse",
  "title": "Software Engineering Intern",
  "location": "London, UK",
  "url": "https://boards.greenhouse.io/.../jobs/...",
  "description": "raw text...",
  "requirements": {
    "years_experience_min": 0,
    "must_have_keywords": ["python"],
    "nice_to_have_keywords": ["react"]
  },
  "first_seen_at": "2025-11-01T13:00:00Z",
  "status": "new"
}
```

### CompanyProfile JSON

```json
{
  "company": "Company A",
  "values": ["Customer focus", "Sustainability", "Operational excellence"],
  "hooks": ["Series D 2024", "Open source program", "UK HQ London"],
  "sources": [{"url": "https://...", "snippet": "one sentence from the page"}]
}
```

### TailoredDraft JSON

```json
{
  "job_id": "job_gh_123",
  "candidate_id": "cand_001",
  "cover_letter_md": "markdown text...",
  "short_answers": [
    {"question": "Why us?", "answer": "..."},
    {"question": "Why you?", "answer": "..."}
  ],
  "evidence_map": [
    {"cl_sentence": "Improved X by Y%", "source": "CV: Project A bullet 2"}
  ]
}
```

### Submission JSON

```json
{
  "job_id": "job_gh_123",
  "method": "auto",
  "result": "submitted",
  "confirmation_screenshot": "/runs/gh_123.png",
  "submitted_at": "2025-11-01T14:05:00Z"
}
```

---

## 4) Tech Stack

* **Backend**: Python 3.11, FastAPI, uvicorn
* **Headless browser**: Playwright (Chromium)
* **Storage**: SQLite (core tables) + Chroma or FAISS for embeddings
* **LLM**: one general model for parsing/writing; optional lighter model for extraction
* **UI**: FastAPI Jinja page or Vite React (single page)
* **Docs & Exports**: Markdown, optional WeasyPrint for PDF
* **Notifications**: Slack/Discord webhooks

---

## 5) Endpoints (FastAPI)

```http
POST /candidate/load      # upload extended CV, returns candidate_id
POST /crawl/run           # scan boards, save jobs, return count
GET  /jobs/new            # list new jobs (paginated)
POST /tailor/{job_id}     # generate TailoredDraft
POST /approve/{job_id}    # run Gatekeeper, return checklist JSON
POST /submit/{job_id}     # run Form Filler, return Submission JSON
GET  /submissions         # list submissions with statuses
```

---

## 6) Database Schema (SQLite)

```
companies(id, name, domain, board_type, careers_url, last_scraped_at)
jobs(id, company_id, title, location, url, description, req_json, first_seen_at, status)
candidates(id, json)
drafts(id, job_id, candidate_id, cover_letter_md, short_answers_json, created_at)
submissions(id, job_id, method, result, screenshot_path, submitted_at)
events(id, ts, kind, payload_json)  -- logging/events
```

---

## 7) Agents and Prompts

### 7.1 CV Parser Agent

* **Tools**: pypdf or pdfminer for text, regex for sections
* **Input**: extended CV file
* **Output**: Candidate JSON
* **Prompt**

```
System: Convert raw CV text into structured JSON with sections: education, skills,
experience, projects, awards, and the 12 strongest metric‑driven bullets. Keep text factual.
No hallucinations.
User: <raw_cv_text>
```

### 7.2 Job Scout Agent

* **Tools**: Playwright, selectors for Greenhouse/Lever
* **Selectors**

  * Greenhouse list: `.opening a[href*="/jobs/"]`
  * Greenhouse detail: `#content`
  * Lever list: `a.posting-title`
  * Lever detail: `.content`
* **Search recipes**

  * `site:boards.greenhouse.io (intern OR "spring week") (software OR data) (London OR UK)`
  * `site:jobs.lever.co (intern OR placement) software London`
* **Optional extractor prompt**

```
System: From this job description, return JSON:
{ "years_experience_min": <int or 0>,
  "must_have_keywords": [...],
  "nice_to_have_keywords": [...],
  "visa_note_if_any": "..." }
Only include facts explicitly present.
User: <job_description>
```

### 7.3 Match & Gate Agent

* **Logic**

  * Title includes required keywords and not excluded ones
  * years_experience_min <= 1 unless title includes intern or spring
  * Location in constraints
  * Embedding similarity between job text and candidate bullets ≥ 0.35
* **Prompt**

```
System: Given candidate and job requirement JSON, return
{"decision":"accept|manual_review|reject","reasons":["...","...","..."]}.
Be conservative on visas and unrelated stacks.
User: <candidate_json> + <job_requirements_json>
```

### 7.4 Company Profiler Agent

* **Tools**: Playwright scrape `/about`, `/careers`, newsroom, ESG page
* **Prompt**

```
System: Summarise 3–5 core values and 2–3 recent initiatives. Output JSON with
values, hooks, and sources (url + one sentence snippet). Do not invent content.
User: <about_page_text + careers_page_text>
```

### 7.5 Tailor Agent (RAG)

* **Retrieval**: top 8 CV bullets + 4 project bullets via embeddings
* **Prompt**

```
System: Write a concise UK‑style cover letter (300–350 words, British English, no em dashes).
Opening: tie one company value or initiative to the role.
Middle: two short paragraphs mapping responsibilities to candidate achievements with metrics.
Ending: three "Why me" bullets with outcomes.
Inputs:
Job: <job_excerpt>
Company: <company_profile_json>
Candidate: <retrieved_bullets_json>
```

### 7.6 Form Filler Agent

* **Tools**: Playwright
* **Behaviour**: Fill basics, upload CV, paste cover letter or upload file, answer common fields. If captcha or MFA, stop and return handoff package (deep link + clipboard text). Always save before/after screenshots.

### 7.7 Follow‑Up Agent

* **Output**: follow‑up drafts for T+7 and T+14 days
* **Prompt**

```
System: Draft a 90–120 word polite follow‑up for the application to "<ROLE_TITLE>"
submitted on <DATE>. Reference one company value and one quantified achievement.
British English. Friendly and concise.
```

### 7.8 Compliance Gatekeeper

* **Output**: checklist JSON of fields to submit, risks, requires_manual_review flag
* **Prompt**

```
System: Produce a checklist of fields that will be submitted with one‑line risks.
Set requires_manual_review true if anything is uncertain.
User: <job_json + candidate_json + draft_json>
```

---

## 8) Playwright Notes (Greenhouse/Lever)

* Click apply: button text often "Apply for this job" or similar
* Files: `input[type=file]` near label text like Resume or CV
* Submit: `[type=submit]` or button with text "Submit application"
* Screenshots: always capture before and after submit
* Resilient waits: use `locator.wait_for()` on key form elements

---

## 9) Setup and Run

### Prereqs

* Python 3.11
* Node (only if using React UI)
* Playwright browsers: `playwright install`

### Environment

```
cp .env.example .env
# set LLM API keys, webhook urls, run mode
```

### Install

```
pip install -r requirements.txt
# optionally: npm i && npm run build
```

### Seed

```
# CSV of target boards with columns: company,name,board_type,careers_url
python tools/seed_companies.py seeds/targets.csv
```

### Run

```
uvicorn app.main:app --reload
# open http://localhost:8000
```

---

## 10) Directory Structure

```
app/
  main.py                # FastAPI app and routes
  agents/
    cv_parser.py
    job_scout.py
    matcher.py
    company_profiler.py
    tailor.py
    form_filler.py
    follow_up.py
    gatekeeper.py
  services/
    embeddings.py
    storage.py
    notifier.py
    browser.py
  ui/
    templates/
    static/
  models/
    schema.py            # pydantic models
    db.py                # sqlite setup
  prompts/
    *.md
seeds/
  targets.csv
runs/
  screenshots/
requirements.txt
README.md
```

---

## 11) Work Plan (12 Hours)

1. Scaffold repo, DB models, env, seed CSV.
2. Greenhouse crawler → jobs table; basic requirement extractor.
3. Lever crawler, dedupe on URL.
4. CV ingestion: PDF to text → CV JSON. Store candidate.
5. Embeddings for CV bullets and projects. Retrieval API.
6. Company profiler for About/Careers → values/hooks.
7. Tailor agent prompt → cover letter + short answers + evidence map.
8. Gatekeeper checklist + simple dashboard cards.
9. Playwright autofill for Greenhouse (screenshots, waits).
10. Lever autofill; Slack webhook on submission.
11. Polish errors and logs; export submissions CSV.
12. Record one golden demo run.

---

## 12) Demo Script

1. Run crawl: new roles appear in "New Roles".
2. Pick one role → Profile Company → values + hooks with sources.
3. Tailor → cover letter appears with highlighted evidence map.
4. Approve → checklist shows fields and risks.
5. Submit → live browser run; show confirmation screenshot.
6. Show follow‑up drafts created for T+7 and T+14.

---

## 13) Guardrails

* Respectful scraping with delays; avoid non‑ATS heavy sites.
* Stop on captcha/MFA; return handoff package.
* Approval gate before any submission.
* Evidence map links cover letter sentences to CV bullets.
* Keep logs and screenshots for every run.

---

## 14) Success Criteria

* Discovers and lists new relevant roles from target boards.
* Produces a tailored cover letter grounded in real values and CV bullets.
* Autofills at least one role end‑to‑end on Greenhouse or Lever in the demo.
* Transparent audit trail with screenshots and stored JSON.

---

## 15) Future Work (post‑MVP)

* Add selected Workday/Taleo flows.
* Gmail API for sending follow‑ups and inbox tracking.
* Multi‑user profiles and authentication.
* Better PDF export and styling.
* More robust semantic matching and salary/visa metadata.

---

## 16) Contribution Guidelines

* Small PRs. Include before/after screenshots where relevant.
* Update schema docs when fields change.
* Add minimal unit tests for agents that transform data (parser, matcher, tailor).
* Log every external action (navigate, submit, upload) to `events`.

---

## 17) Licence

MIT for the hackathon prototype. Review third‑party TOS for any production use.
