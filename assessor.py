import json
import os
from groq import Groq
from dotenv import load_dotenv
from prompts import QUESTION_GENERATOR_PROMPT, ANSWER_EVALUATOR_PROMPT

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def generate_questions(skill: str, candidate_context: str) -> list:
    """
    Generates 2 assessment questions for a given skill.
    """
    try:
        prompt = QUESTION_GENERATOR_PROMPT.format(
            skill=skill,
            candidate_context=candidate_context
        )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )

        raw_text = response.choices[0].message.content.strip()

        if raw_text.startswith("```"):
            raw_text = raw_text.split("```")[1]
            if raw_text.startswith("json"):
                raw_text = raw_text[4:]
        raw_text = raw_text.strip()

        result = json.loads(raw_text)
        return result.get("questions", [])

    except Exception as e:
        return [
            f"Can you explain your experience with {skill}?",
            f"Give an example of how you have used {skill} in a real project."
        ]


def evaluate_answer(skill: str, question: str, answer: str) -> dict:
    """
    Evaluates a candidate's answer and returns score + reasoning.
    """
    try:
        prompt = ANSWER_EVALUATOR_PROMPT.format(
            skill=skill,
            question=question,
            answer=answer
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

        result = json.loads(raw_text)
        return result

    except Exception as e:
        return {
            "score": 5,
            "reasoning": "Could not evaluate answer properly.",
            "follow_up": None
        }


def get_score_label(score: int) -> str:
    """
    Converts a numeric score to a human readable label.
    """
    if score >= 8:
        return "Expert"
    elif score >= 6:
        return "Proficient"
    elif score >= 4:
        return "Basic"
    else:
        return "Beginner"


def calculate_readiness_score(skill_scores: dict) -> int:
    """
    Calculates overall candidate readiness as percentage out of 100.
    """
    if not skill_scores:
        return 0
    total = sum(skill_scores.values())
    average = total / len(skill_scores)
    return round((average / 10) * 100)