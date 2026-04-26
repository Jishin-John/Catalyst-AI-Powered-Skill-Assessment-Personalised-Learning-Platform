import json
import os
from datetime import datetime

STORAGE_FILE = "data/candidates.json"


def load_all_candidates() -> dict:
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}


def save_candidate_result(name: str, email: str, data: dict):
    all_data = load_all_candidates()
    candidate_id = email.lower().strip()

    if candidate_id not in all_data:
        all_data[candidate_id] = {
            'name': name,
            'email': email,
            'created_at': datetime.now().isoformat(),
            'attempts': []
        }

    attempt = {
        'timestamp': datetime.now().isoformat(),
        'job_role': data.get('job_role', ''),
        'readiness_score': data.get('readiness_score', 0),
        'skill_scores': data.get('skill_scores', {}),
        'gap_analysis': data.get('gap_analysis', {}),
        'selection_chance': data.get('selection_chance', 0),
        'tab_violations': data.get('tab_violations', 0),
        'time_taken': data.get('time_taken', 0),
        'willingness_score': data.get('willingness_score', 0)
    }

    all_data[candidate_id]['attempts'].append(attempt)
    all_data[candidate_id]['latest'] = attempt
    all_data[candidate_id]['name'] = name

    if 'xp' not in all_data[candidate_id]:
        all_data[candidate_id]['xp'] = 0
    if 'badges' not in all_data[candidate_id]:
        all_data[candidate_id]['badges'] = []
    if 'skill_sprint_best' not in all_data[candidate_id]:
        all_data[candidate_id]['skill_sprint_best'] = 0
    if 'streak' not in all_data[candidate_id]:
        all_data[candidate_id]['streak'] = 0

    os.makedirs('data', exist_ok=True)
    with open(STORAGE_FILE, 'w') as f:
        json.dump(all_data, f, indent=2)

    return candidate_id


def get_candidate(email: str) -> dict:
    all_data = load_all_candidates()
    return all_data.get(email.lower().strip(), None)


def calculate_willingness_score(attempts: list) -> int:
    if len(attempts) < 2:
        return 50
    scores = [a.get('readiness_score', 0) for a in attempts]
    if scores[-1] > scores[0]:
        return min(100, 50 + (scores[-1] - scores[0]))
    return max(20, 50 - (scores[0] - scores[-1]))


def calculate_selection_chance(
    readiness_score: int,
    tab_violations: int,
    willingness: int
) -> int:
    base = readiness_score
    penalty = tab_violations * 5
    bonus = (willingness - 50) * 0.3
    return max(0, min(100, int(base - penalty + bonus)))