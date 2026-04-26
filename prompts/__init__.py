SKILL_EXTRACTOR_PROMPT = """
You are an expert HR analyst. Given a Job Description and a Resume, extract skills.

Job Description:
{jd}

Resume:
{resume}

Return ONLY valid JSON, no extra text, no markdown:
{{
  "job_role": "title of the job",
  "required_skills": ["skill1", "skill2"],
  "candidate_skills": ["skill1", "skill2"],
  "skill_match": {{
    "skill_name": "YES/PARTIAL/NO"
  }}
}}
"""

QUESTION_GENERATOR_PROMPT = """
You are a senior technical interviewer. Generate 2 short conversational assessment questions for: {skill}

Candidate background: {candidate_context}

Return ONLY valid JSON:
{{
  "questions": ["question1", "question2"]
}}
"""

ANSWER_EVALUATOR_PROMPT = """
You are an expert evaluator. Score this answer for the skill: {skill}

Question: {question}
Answer: {answer}

Score 1-10 where:
1-3 = No understanding
4-5 = Surface knowledge
6-7 = Solid knowledge
8-10 = Expert level

Return ONLY valid JSON:
{{
  "score": 7,
  "reasoning": "one sentence explanation",
  "follow_up": "optional follow-up question or null"
}}
"""

GAP_ANALYZER_PROMPT = """
You are a career coach. Analyze these skill scores for a {job_role} role:

{skill_scores}

Return ONLY valid JSON:
{{
  "strong_skills": ["skill (score/10)"],
  "gap_skills": ["skill (score/10)"],
  "adjacent_skills": ["skill that bridges a gap"]
}}
"""

LEARNING_PLAN_PROMPT = """
You are a learning coach. Create a personalised plan for these skill gaps: {gap_skills}
Target role: {job_role}

Return ONLY valid JSON:
{{
  "learning_plan": [
    {{
      "skill": "skill name",
      "priority": "HIGH",
      "time_estimate": "2 weeks",
      "mini_project": "build X to prove this skill"
    }}
  ],
  "total_time_estimate": "6-8 weeks",
  "recommended_order": ["skill1", "skill2"]
}}
"""

FLASHCARD_PROMPT = """
Generate 5 flashcards for the skill: {skill}
Level: {level}

Return ONLY valid JSON, no extra text:
{{
  "flashcards": [
    {{
      "front": "concept or question on the front of the card",
      "back": "clear explanation or answer on the back"
    }}
  ]
}}
"""