# ◈ Catalyst — Architecture & Technical Documentation

## What is Catalyst?

Catalyst is an Agentic AI system that solves a real problem:
**Resumes lie. Candidates claim skills they don't have.**

Catalyst takes a Job Description and a Resume, runs the candidate
through a multi-mode assessment, identifies real skill gaps,
and produces a personalised learning plan with live YouTube resources.

---

## System Architecture
┌─────────────────────────────────────────────────────────────┐
│                    CANDIDATE INPUT                           │
│              Job Description + Resume                        │
└──────────────────────┬──────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│                 SKILL EXTRACTOR                              │
│   Groq LLM reads JD + Resume                                 │
│   → Required skills list                                     │
│   → Candidate skills list                                    │
│   → Match status: YES / PARTIAL / NO                        │
└──────────────────────┬──────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│              AGENT ORCHESTRATOR                              │
│   Decides assessment mode per skill:                        │
│   LOW level → MCQ basic + Debugging challenge               │
│   MEDIUM level → Whiteboard scenario + Trade-off slider     │
│   HIGH level → Scenario branch + GitHub code question       │
└──────┬────────────────┬───────────────────┬─────────────────┘
│                │                   │
▼                ▼                   ▼
┌──────────┐   ┌──────────────┐   ┌──────────────────┐
│   MCQ    │   │ Conversational│   │  Gamified Modes  │
│  Engine  │   │  Assessor     │   │  - Debug Code    │
│ Timed    │   │ Adaptive      │   │  - Whiteboard    │
│ Anti-    │   │ Follow-ups    │   │  - Trade-off     │
│ cheat    │   │ Scoring 1-10  │   │  - Scenario RPG  │
└────┬─────┘   └──────┬───────┘   └────────┬─────────┘
│                │                    │
└────────────────┴────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│                  GAP ANALYZER                                │
│   Groq LLM analyzes all scores                              │
│   → Strong skills (score >= 7)                              │
│   → Gap skills (score < 7)                                  │
│   → Adjacent skills to realistically acquire               │
└──────────────────────┬──────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│             LEARNING PLAN GENERATOR                          │
│   Groq LLM creates personalised roadmap                     │
│   + YouTube Data API v3 fetches live best videos            │
│   + Sorted by view count + like count                       │
│   + Flashcards generated per skill                          │
└──────────────────────┬──────────────────────────────────────┘
│
▼
┌─────────────────────────────────────────────────────────────┐
│                    OUTPUT                                    │
│   Radar chart + Bar chart + Gauge charts                    │
│   Skill Sprint Game (60s rapid fire)                        │
│   XP + Level + Badges (gamification)                        │
│   PDF Report (ReportLab)                                    │
│   HR Dashboard with leaderboard + analytics                 │
└─────────────────────────────────────────────────────────────┘

---

## Tech Stack

| Layer | Technology | Purpose | Cost |
|---|---|---|---|
| Language | Python 3.13 | Core backend | Free |
| UI Framework | Streamlit | Web interface | Free |
| Primary LLM | Groq (Llama 3.3 70B) | All AI reasoning | Free tier |
| Backup LLM | Google Gemini 2.0 Flash | Fallback AI | Free tier |
| Video API | YouTube Data API v3 | Live resource search | Free (10k/day) |
| Charts | Plotly | Radar, bar, gauge charts | Free |
| PDF | ReportLab | PDF report generation | Free |
| PDF parsing | PyPDF2 | Resume PDF reading | Free |
| Gamification | Custom (utils/gamification.py) | XP, levels, badges | Built in-house |
| Anti-cheat | JavaScript visibilitychange API | Tab switch detection | Built in-house |
| Storage | JSON file (data/candidates.json) | Candidate data | Built in-house |
| Deployment | Streamlit Cloud | Live URL | Free |

---

## Key Technical Decisions

### Why Groq over OpenAI?
Groq runs Llama 3.3 70B at ~300 tokens/second — 10x faster than GPT-4.
For a real-time conversational assessment, speed matters.
The free tier gives 14,400 requests/day — more than enough.

### Why Streamlit over React?
The entire frontend needed to be built in under 48 hours.
Streamlit lets Python developers build production UIs without JavaScript.
Everything from chat interfaces to charts to file uploads is built-in.

### Why YouTube API instead of hardcoded links?
Hardcoded links go stale. YouTube API fetches the most viewed,
most liked beginner videos in real time — so resources are always current.

### Why JSON storage instead of a database?
For a hackathon prototype, a database adds deployment complexity.
JSON file works perfectly for the scale being demonstrated.
In production, this would be replaced with PostgreSQL.

---

## Agentic AI Flow

What makes this Agentic (not just a chatbot):

1. **Plans** — Reads JD and resume, decides which skills to test
2. **Decides** — Chooses assessment mode per skill based on level
3. **Adapts** — Asks follow-up questions if answers are weak
4. **Loops** — Moves through all skills automatically without human input
5. **Synthesizes** — Combines all scores to generate gap analysis
6. **Acts** — Searches YouTube live, generates learning plan, produces PDF

The human only inputs at the start (JD + Resume) and answers questions.
Everything else is driven by the agent.

---

## File Structure

## File Structure
catalyst-agent/
├── app.py                        
├── pages/
│   ├── Candidate_Portal.py      
│   └── HR_Portal.py             
├── agent/
│   ├── extractor.py              
│   ├── assessor.py               
│   ├── gap_analyzer.py           
│   ├── youtube_search.py         
│   └── mcq_generator.py          
├── utils/
│   ├── pdf_generator.py          
│   ├── storage.py               
│   └── anti_cheat.py             
├── prompts/
│   └── __init__.py               
├── data/                        
│   └── candidates.json       
├── .env
└── requirements.txt
