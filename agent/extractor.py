import json
import os
from groq import Groq
from dotenv import load_dotenv
from prompts import SKILL_EXTRACTOR_PROMPT

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def extract_skills(jd: str, resume: str) -> dict:
    try:
        prompt = SKILL_EXTRACTOR_PROMPT.format(
            jd=jd,
            resume=resume
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

    except json.JSONDecodeError as e:
        return {
            "error": f"Failed to parse AI response: {str(e)}",
            "job_role": "Unknown",
            "required_skills": [],
            "candidate_skills": [],
            "skill_match": {}
        }
    except Exception as e:
        return {
            "error": f"API error: {str(e)}",
            "job_role": "Unknown",
            "required_skills": [],
            "candidate_skills": [],
            "skill_match": {}
        }


def get_skills_to_assess(skill_match: dict) -> list:
    skills_to_assess = []
    for skill, status in skill_match.items():
        if status in ["NO", "PARTIAL"]:
            skills_to_assess.append({
                "skill": skill,
                "status": status
            })
    return skills_to_assess


def get_resume_text_from_pdf(uploaded_file) -> str:
    try:
        import PyPDF2
        pdf_reader = PyPDF2.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        return f"Error reading PDF: {str(e)}"