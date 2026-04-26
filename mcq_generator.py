import json
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_mcq(skill, level, focus_area="", count=5):
    level_desc = {
        "LOW": "basic definitions and concepts for beginners.",
        "MEDIUM": "practical application and real scenarios. Intermediate.",
        "HIGH": "advanced edge cases and architecture. Expert level."
    }
    focus_text = f"Focus on: {focus_area}" if focus_area else ""
    prompt = f"""Generate exactly {count} MCQ questions for the skill: {skill}
Difficulty: {level} — {level_desc.get(level, '')}
{focus_text}

Return ONLY valid JSON, no extra text:
{{
    "questions": [
        {{
            "question": "question text",
            "options": ["A. opt1", "B. opt2", "C. opt3", "D. opt4"],
            "correct": "A",
            "explanation": "why this is correct"
        }}
    ]
}}"""
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        raw = response.choices[0].message.content.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()
        result = json.loads(raw)
        return result.get("questions", [])
    except Exception:
        return [{
            "question": f"What is {skill} primarily used for?",
            "options": [
                "A. Data processing",
                "B. Web development",
                "C. Automation",
                "D. All of the above"
            ],
            "correct": "D",
            "explanation": f"{skill} has multiple use cases."
        }]


def determine_skill_level(score):
    if score >= 7:
        return "HIGH"
    elif score >= 4:
        return "MEDIUM"
    else:
        return "LOW"


def extract_focus_area(skill, jd):
    skill_lower = skill.lower()
    for line in jd.lower().split('\n'):
        if skill_lower in line:
            return line.strip()
    return ""


def calculate_mcq_score(answers, questions):
    correct = 0
    total = len(questions)
    results = []
    for i, q in enumerate(questions):
        user_answer = answers[i] if i < len(answers) else ""
        is_correct = (
            user_answer.strip().upper().startswith(
                q.get("correct", "A").upper()
            )
        ) if user_answer else False
        if is_correct:
            correct += 1
        results.append({
            "question": q["question"],
            "user_answer": user_answer,
            "correct_answer": q["correct"],
            "is_correct": is_correct,
            "explanation": q.get("explanation", "")
        })
    return {
        "score": round((correct / total) * 10) if total > 0 else 0,
        "correct": correct,
        "total": total,
        "percentage": round((correct / total) * 100) if total > 0 else 0,
        "results": results
    }


def get_timer_seconds(question_count):
    return question_count * 30


def get_question_level(resume_status, skill_score=0):
    if skill_score >= 7:
        return "HIGH"
    elif resume_status == "YES":
        return "MEDIUM"
    elif resume_status == "PARTIAL":
        return "MEDIUM"
    else:
        return "LOW"