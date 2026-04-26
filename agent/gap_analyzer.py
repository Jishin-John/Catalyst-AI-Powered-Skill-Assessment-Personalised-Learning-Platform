import json
import os
from groq import Groq
from dotenv import load_dotenv
from prompts import GAP_ANALYZER_PROMPT, LEARNING_PLAN_PROMPT

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def analyze_gaps(skill_scores: dict, job_role: str) -> dict:
    """
    Analyzes skill scores and identifies strong skills,
    gap skills and adjacent skills to learn.
    """
    try:
        scores_text = "\n".join([
            f"- {skill}: {score}/10"
            for skill, score in skill_scores.items()
        ])

        prompt = GAP_ANALYZER_PROMPT.format(
            job_role=job_role,
            skill_scores=scores_text
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )

        raw_text = response.choices[0].message.content.strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        raw_text = raw_text.strip()

        return json.loads(raw_text)

    except Exception as e:
        return {
            "strong_skills": [],
            "gap_skills": list(skill_scores.keys()),
            "adjacent_skills": []
        }


def generate_learning_plan(gap_skills: list, job_role: str) -> dict:
    """
    Generates a personalised week by week learning plan
    for the identified skill gaps.
    """
    try:
        prompt = LEARNING_PLAN_PROMPT.format(
            gap_skills=", ".join(gap_skills),
            job_role=job_role
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.5
        )

        raw_text = response.choices[0].message.content.strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        raw_text = raw_text.strip()

        return json.loads(raw_text)

    except Exception as e:
        return {
            "learning_plan": [],
            "total_time_estimate": "Unknown",
            "recommended_order": gap_skills
        }