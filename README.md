<div align="center">

<img src="https://img.shields.io/badge/◈-Catalyst-667eea?style=for-the-badge&labelColor=1a1a2e&color=667eea" alt="Catalyst" />

# ◈ Catalyst
### AI-Powered Skill Assessment & Personalised Learning Platform

> *A resume tells you what someone claims to know — not how well they actually know it.*

[![Python](https://img.shields.io/badge/Python-3.13-blue?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.32-FF4B4B?style=flat-square&logo=streamlit&logoColor=white)](https://streamlit.io)
[![Groq](https://img.shields.io/badge/Groq-Llama_3.3_70B-orange?style=flat-square)](https://groq.com)
[![YouTube API](https://img.shields.io/badge/YouTube-Data_API_v3-red?style=flat-square&logo=youtube&logoColor=white)](https://developers.google.com/youtube)
[![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)

**[Live Demo →](https://your-app.streamlit.app)** • **[Video Walkthrough →](https://your-video-link)** • **[Report Bug →](mailto:support@catalyst.ai)**

---

</div>

## 🎯 What is Catalyst?

Catalyst is an **Agentic AI system** that solves the most expensive problem in hiring:

**Candidates lie on resumes. Hiring managers can't verify in real time.**

Catalyst takes a Job Description and a Resume, autonomously runs the candidate through a multi-mode assessment, identifies real skill gaps, and produces a personalised learning plan with live YouTube resources — all without human intervention between steps.

---

## ✨ Features

### 🎯 Candidate Portal
| Feature | Description |
|---|---|
| **Smart Skill Extraction** | AI reads JD + Resume and maps required vs claimed skills |
| **MCQ Assessment** | Timed tests with adaptive difficulty — LOW / MEDIUM / HIGH |
| **Conversational Interview** | AI asks questions, evaluates answers, asks follow-ups if weak |
| **🐛 Debug Challenges** | Fix broken code snippets — tests real engineering instinct |
| **🤝 Whiteboard Collaboration** | AI admits a design flaw and asks candidate for advice |
| **⚖️ Trade-off Sliders** | Pick 2 of 3 — reveals engineering philosophy |
| **🎮 Scenario RPG** | Own a system, face a crisis, make decisions under pressure |
| **Anti-Cheat Timer** | Tab switch detection, integrity score, violation tracking |
| **Adaptive Follow-ups** | If answer is weak, AI digs deeper automatically |
| **YouTube Live Search** | Fetches most viewed + liked beginner videos per skill gap |
| **Flashcards** | AI-generated flip cards per skill — reinforces learning |
| **Skill Sprint Game** | 60 second rapid fire quiz with streak multiplier |
| **XP + Levels + Badges** | Gamified progression — Rookie → Learner → Expert → Master |
| **Readiness Score** | Overall % readiness for the role |
| **Selection Chance %** | Probability of getting hired based on scores + integrity |
| **PDF Report** | Full assessment report with charts, gaps, learning plan |

### 👔 HR Portal
| Feature | Description |
|---|---|
| **Leaderboard** | All candidates ranked by XP with level badges |
| **Candidate Comparison** | Side by side comparison with radar chart overlay |
| **Willingness Score** | Tracks improvement over multiple attempts |
| **Integrity Score** | Tab violations → integrity penalty visible to HR |
| **Analytics Dashboard** | Readiness distribution, level pie chart, avg skill scores |
| **Hiring Recommendation** | AI recommendation on who to hire based on all signals |

---

## 🏗️ Architecture
JD + Resume Input
↓
Skill Extractor (Groq LLM)
↓
Agent Orchestrator — plans assessment per skill
↓
┌──────────────────────────────────────────┐
│  MCQ Engine  │  Gamified Modes  │  Chat  │
│  Timed test  │  Debug/Board/RPG │  Q&A   │
└──────────────────────────────────────────┘
↓
Gap Analyzer (Groq LLM)
↓
Learning Plan + YouTube API (live search)
↓
PDF Report + Radar Chart + Gamification

**What makes it Agentic:**
1. **Plans** — reads JD+resume, decides which skills to test and at what level
2. **Decides** — picks assessment mode per skill based on difficulty
3. **Adapts** — asks follow-up questions when answers are weak
4. **Loops** — moves through all skills automatically
5. **Synthesizes** — combines all scores into gap analysis
6. **Acts** — searches YouTube live, generates plan, produces PDF

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Language | Python 3.13 | Core backend |
| UI | Streamlit | Web interface |
| Primary LLM | Groq (Llama 3.3 70B) | All AI reasoning — free tier |
| Backup LLM | Google Gemini 2.0 Flash | Fallback |
| Video API | YouTube Data API v3 | Live resource search |
| Charts | Plotly | Radar, bar, gauge charts |
| PDF | ReportLab | Assessment report generation |
| Anti-cheat | JS visibilitychange API | Tab switch detection |
| Storage | JSON | Candidate data persistence |
| Deployment | Streamlit Cloud | Free live URL |

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Free API keys (all free tier, no credit card needed)

### Installation

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/catalyst-agent
cd catalyst-agent

# Install dependencies
pip install -r requirements.txt
```

### API Keys

Create a `.env` file in the root directory:

```env
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
YOUTUBE_API_KEY=your_youtube_key
```

Get your free keys:
- **Groq** (free, no card): https://console.groq.com/keys
- **Gemini** (free, no card): https://aistudio.google.com/app/apikey
- **YouTube** (free, 10k/day): https://console.cloud.google.com → YouTube Data API v3

### Run

```bash
streamlit run app.py
```

Open http://localhost:8501

---

## 📁 Project Structure
catalyst-agent/
├── app.py                      ← Landing page with portal selection
├── pages/
│   ├── Candidate_Portal.py     ← Full candidate assessment flow
│   └── HR_Portal.py            ← HR dashboard and analytics
├── agent/
│   ├── extractor.py            ← Skill extraction from JD + resume
│   ├── assessor.py             ← Conversational interview engine
│   ├── gap_analyzer.py         ← Gap analysis + learning plan
│   ├── mcq_generator.py        ← MCQ generation with smart timer
│   ├── youtube_search.py       ← YouTube API live search
│   └── gamified_assessment.py  ← Debug/whiteboard/tradeoff/RPG modes
├── utils/
│   ├── gamification.py         ← XP, levels, badges engine
│   ├── storage.py              ← JSON data persistence
│   ├── anti_cheat.py           ← Timer + tab switch detection
│   └── pdf_generator.py        ← PDF report generation
├── prompts/
│   └── init.py             ← All LLM prompt templates
├── data/
│   └── candidates.json         ← Auto-created candidate storage
├── .env                        ← API keys (never commit)
├── .gitignore
├── requirements.txt
└── README.md

---

## 🎮 Gamification System
XP Actions                    Levels
─────────────────────         ──────────────────────
✓ Correct MCQ    +10 XP       🌱 Rookie      0–199 XP
✓ Good interview +20 XP       📚 Learner    200–499 XP
✓ Full assessment +50 XP      ⚡ Skilled    500–999 XP
✓ Flashcards     +15 XP       🔥 Advanced  1000–1999 XP
✓ Learning plan  +25 XP       💎 Expert    2000–3999 XP
✓ Zero violations +40 XP      👑 Master      4000+ XP
✓ Sprint win      +50 XP

---

## 🧠 Psychology-Backed Assessment Modes

| Mode | Trigger | Psychology |
|---|---|---|
| **MCQ Test** | All skills | Timed pressure → System 1 thinking |
| **Debug Challenge** | Low scorers | Cognitive dissonance → urge to fix broken things |
| **Whiteboard** | High scorers | Pratfall Effect → AI admits weakness, reduces anxiety |
| **Trade-off** | Mid scorers | Forced choice → reveals engineering philosophy |
| **Scenario RPG** | All | Endowment Effect → ownership increases engagement |
| **Micro-feedback** | After answers | Variable Reward → dopamine hit from unexpected praise |

---

## 📊 Judging Criteria Coverage

| Criteria | Weight | How We Address It |
|---|---|---|
| Works end-to-end | 20% | Full flow from input to PDF output, demo mode included |
| Agent quality | 25% | 5-step agentic loop with memory, adaptation, synthesis |
| Output quality | 20% | Scores, radar, gap analysis, learning plan, YouTube, PDF |
| Technical implementation | 15% | 4 APIs, gamification engine, anti-cheat, modular codebase |
| Innovation | 10% | Live YouTube search, psychology-backed modes, gamification |
| UX | 5% | Animations, XP bar, badges, dark theme, mobile-friendly |
| Code quality | 5% | Modular files, clear functions, error handling throughout |

---

## 🎬 Demo

**Try the demo in 10 seconds:**
1. Open the app
2. Click **"Try Demo"** on the Candidate Portal
3. Click **"Analyze My Skills"**
4. Click **"Begin Assessment"**
5. Answer a few questions
6. See your results, learning plan, and download PDF

---

## 🔮 Roadmap (Post-Hackathon)

- [ ] PostgreSQL database for production scale
- [ ] Multi-tenant HR accounts
- [ ] Video interview recording and analysis
- [ ] Integration with LinkedIn and GitHub profiles
- [ ] Mobile app (React Native)
- [ ] Calendar integration for scheduled assessments
- [ ] Team assessments for project-based hiring

---

## 👤 Author

**Jishin John**
Built for **Deccan AI Catalyst Hackathon 2026**

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

<div align="center">

**◈ Catalyst — Stop hiring resumes. Start hiring skills.**

*Built with ❤️ using Agentic AI + Groq + YouTube API*

</div>