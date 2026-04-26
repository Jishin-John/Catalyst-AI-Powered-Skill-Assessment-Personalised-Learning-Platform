import json
import os
from datetime import datetime

STORAGE_FILE = "data/candidates.json"

# ─────────────────────────────────────────
# XP VALUES — how much each action earns
# ─────────────────────────────────────────
XP_VALUES = {
    "correct_mcq":        10,   # each correct MCQ answer
    "perfect_mcq":        30,   # all correct in one skill MCQ
    "good_interview":     20,   # interview score >= 7
    "great_interview":    35,   # interview score >= 9
    "full_assessment":    50,   # completed all skills
    "flashcard_done":     15,   # opened and flipped all flashcards
    "learning_plan":      25,   # generated learning plan
    "zero_violations":    40,   # no tab switches during test
    "skill_sprint_play":  10,   # played skill sprint game
    "skill_sprint_win":   50,   # scored 80%+ in skill sprint
    "pdf_downloaded":     10,   # downloaded report
    "return_attempt":     20,   # came back and did another attempt
}

# ─────────────────────────────────────────
# LEVELS — XP thresholds
# ─────────────────────────────────────────
LEVELS = [
    {"name": "Rookie",      "min": 0,    "max": 199,  "icon": "🌱", "color": "#a0aec0"},
    {"name": "Learner",     "min": 200,  "max": 499,  "icon": "📚", "color": "#63b3ed"},
    {"name": "Skilled",     "min": 500,  "max": 999,  "icon": "⚡", "color": "#68d391"},
    {"name": "Advanced",    "min": 1000, "max": 1999, "icon": "🔥", "color": "#f6ad55"},
    {"name": "Expert",      "min": 2000, "max": 3999, "icon": "💎", "color": "#b794f4"},
    {"name": "Master",      "min": 4000, "max": 99999,"icon": "👑", "color": "#fc8181"},
]

# ─────────────────────────────────────────
# BADGES — conditions to unlock them
# ─────────────────────────────────────────
ALL_BADGES = [
    {
        "id": "first_assessment",
        "name": "First Step",
        "desc": "Completed your first assessment",
        "icon": "🎯",
        "color": "#63b3ed"
    },
    {
        "id": "perfect_mcq",
        "name": "Perfect Score",
        "desc": "Got 100% on an MCQ test",
        "icon": "⭐",
        "color": "#f6ad55"
    },
    {
        "id": "zero_violations",
        "name": "Honest Coder",
        "desc": "Completed test with zero tab switches",
        "icon": "🛡️",
        "color": "#68d391"
    },
    {
        "id": "skill_sprint_master",
        "name": "Sprint Master",
        "desc": "Scored 80%+ in Skill Sprint game",
        "icon": "⚡",
        "color": "#f6ad55"
    },
    {
        "id": "learning_started",
        "name": "Growth Mindset",
        "desc": "Generated your first learning plan",
        "icon": "🌱",
        "color": "#68d391"
    },
    {
        "id": "flashcard_master",
        "name": "Flashcard Fan",
        "desc": "Completed flashcards for a skill",
        "icon": "🃏",
        "color": "#b794f4"
    },
    {
        "id": "high_readiness",
        "name": "Job Ready",
        "desc": "Reached 70%+ readiness score",
        "icon": "🚀",
        "color": "#fc8181"
    },
    {
        "id": "comeback_kid",
        "name": "Comeback Kid",
        "desc": "Improved score on second attempt",
        "icon": "💪",
        "color": "#f6ad55"
    },
    {
        "id": "expert_skill",
        "name": "Skill Expert",
        "desc": "Scored 9+ on any single skill",
        "icon": "💎",
        "color": "#b794f4"
    },
    {
        "id": "speed_demon",
        "name": "Speed Demon",
        "desc": "Finished assessment in under 10 minutes",
        "icon": "🏎️",
        "color": "#fc8181"
    },
]


# ─────────────────────────────────────────
# LOAD / SAVE HELPERS
# ─────────────────────────────────────────

def _load() -> dict:
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, "r") as f:
            try:
                return json.load(f)
            except Exception:
                return {}
    return {}


def _save(data: dict):
    os.makedirs("data", exist_ok=True)
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _get_or_create_profile(email: str, name: str = "") -> dict:
    data = _load()
    key = email.lower().strip()
    if key not in data:
        data[key] = {
            "name": name,
            "email": key,
            "created_at": datetime.now().isoformat(),
            "attempts": [],
            "latest": {}
        }
    if "xp" not in data[key]:
        data[key]["xp"] = 0
    if "badges" not in data[key]:
        data[key]["badges"] = []
    if "streak" not in data[key]:
        data[key]["streak"] = 0
    if "skill_sprint_best" not in data[key]:
        data[key]["skill_sprint_best"] = 0
    if "game_history" not in data[key]:
        data[key]["game_history"] = []
    return data, key


# ─────────────────────────────────────────
# XP ENGINE
# ─────────────────────────────────────────

def award_xp(email: str, action: str, amount: int = None) -> dict:
    """
    Awards XP for an action.
    Returns dict with xp_gained, total_xp, leveled_up, new_level info.
    """
    data, key = _get_or_create_profile(email)
    profile = data[key]

    xp_gained = amount if amount else XP_VALUES.get(action, 0)
    old_xp = profile["xp"]
    new_xp = old_xp + xp_gained

    old_level = get_level(old_xp)
    new_level = get_level(new_xp)
    leveled_up = new_level["name"] != old_level["name"]

    profile["xp"] = new_xp
    profile["game_history"].append({
        "action": action,
        "xp": xp_gained,
        "timestamp": datetime.now().isoformat()
    })

    data[key] = profile
    _save(data)

    return {
        "xp_gained": xp_gained,
        "total_xp": new_xp,
        "old_xp": old_xp,
        "leveled_up": leveled_up,
        "old_level": old_level,
        "new_level": new_level,
        "progress_pct": get_level_progress_pct(new_xp)
    }


def get_xp(email: str) -> int:
    data = _load()
    key = email.lower().strip()
    return data.get(key, {}).get("xp", 0)


# ─────────────────────────────────────────
# LEVEL ENGINE
# ─────────────────────────────────────────

def get_level(xp: int) -> dict:
    for level in reversed(LEVELS):
        if xp >= level["min"]:
            return level
    return LEVELS[0]


def get_level_progress_pct(xp: int) -> int:
    """
    Returns 0-100 progress within current level.
    """
    level = get_level(xp)
    if level["max"] == 99999:
        return 100
    level_xp = xp - level["min"]
    level_range = level["max"] - level["min"]
    return min(100, int((level_xp / level_range) * 100))


def get_xp_to_next(xp: int) -> int:
    level = get_level(xp)
    if level["max"] == 99999:
        return 0
    return level["max"] - xp + 1


# ─────────────────────────────────────────
# BADGE ENGINE
# ─────────────────────────────────────────

def unlock_badge(email: str, badge_id: str) -> dict:
    """
    Unlocks a badge for a candidate.
    Returns the badge dict if newly unlocked, None if already had it.
    """
    data, key = _get_or_create_profile(email)
    profile = data[key]

    if badge_id in profile["badges"]:
        return None

    badge = next((b for b in ALL_BADGES if b["id"] == badge_id), None)
    if not badge:
        return None

    profile["badges"].append(badge_id)
    data[key] = profile
    _save(data)
    return badge


def get_badges(email: str) -> list:
    """
    Returns list of unlocked badge objects for a candidate.
    """
    data = _load()
    key = email.lower().strip()
    unlocked_ids = data.get(key, {}).get("badges", [])
    return [b for b in ALL_BADGES if b["id"] in unlocked_ids]


def get_all_badges_status(email: str) -> list:
    """
    Returns ALL badges with locked/unlocked status.
    """
    data = _load()
    key = email.lower().strip()
    unlocked_ids = data.get(key, {}).get("badges", [])
    result = []
    for b in ALL_BADGES:
        b_copy = dict(b)
        b_copy["unlocked"] = b["id"] in unlocked_ids
        result.append(b_copy)
    return result


def check_and_award_badges(
    email: str,
    readiness_score: int = 0,
    tab_violations: int = 0,
    skill_scores: dict = None,
    is_first_attempt: bool = False,
    improved: bool = False,
    sprint_pct: int = 0,
    flashcard_done: bool = False,
    time_taken_mins: float = 999
) -> list:
    """
    Checks all badge conditions and unlocks eligible ones.
    Returns list of newly unlocked badges.
    """
    newly_unlocked = []
    skill_scores = skill_scores or {}

    checks = [
        ("first_assessment",    is_first_attempt),
        ("perfect_mcq",         any(s == 10 for s in skill_scores.values())),
        ("zero_violations",     tab_violations == 0),
        ("skill_sprint_master", sprint_pct >= 80),
        ("learning_started",    True),
        ("flashcard_master",    flashcard_done),
        ("high_readiness",      readiness_score >= 70),
        ("comeback_kid",        improved),
        ("expert_skill",        any(s >= 9 for s in skill_scores.values())),
        ("speed_demon",         time_taken_mins < 10),
    ]

    for badge_id, condition in checks:
        if condition:
            result = unlock_badge(email, badge_id)
            if result:
                newly_unlocked.append(result)

    return newly_unlocked


# ─────────────────────────────────────────
# STREAK ENGINE
# ─────────────────────────────────────────

def update_streak(email: str) -> int:
    data, key = _get_or_create_profile(email)
    profile = data[key]
    history = profile.get("game_history", [])

    if not history:
        profile["streak"] = 1
    else:
        last = history[-1].get("timestamp", "")
        try:
            last_date = datetime.fromisoformat(last).date()
            today = datetime.now().date()
            diff = (today - last_date).days
            if diff == 1:
                profile["streak"] = profile.get("streak", 0) + 1
            elif diff == 0:
                pass
            else:
                profile["streak"] = 1
        except Exception:
            profile["streak"] = 1

    data[key] = profile
    _save(data)
    return profile["streak"]


# ─────────────────────────────────────────
# SKILL SPRINT SCORE
# ─────────────────────────────────────────

def save_sprint_score(email: str, score: int):
    data, key = _get_or_create_profile(email)
    profile = data[key]
    current_best = profile.get("skill_sprint_best", 0)
    if score > current_best:
        profile["skill_sprint_best"] = score
    data[key] = profile
    _save(data)


def get_sprint_best(email: str) -> int:
    data = _load()
    return data.get(email.lower().strip(), {}).get("skill_sprint_best", 0)


# ─────────────────────────────────────────
# LEADERBOARD
# ─────────────────────────────────────────

def get_leaderboard(top_n: int = 10) -> list:
    data = _load()
    board = []
    for email, profile in data.items():
        xp = profile.get("xp", 0)
        level = get_level(xp)
        board.append({
            "name": profile.get("name", "Unknown"),
            "email": email,
            "xp": xp,
            "level": level["name"],
            "level_icon": level["icon"],
            "level_color": level["color"],
            "badges_count": len(profile.get("badges", [])),
            "sprint_best": profile.get("skill_sprint_best", 0),
            "streak": profile.get("streak", 0),
            "readiness": profile.get("latest", {}).get("readiness_score", 0)
        })

    board.sort(key=lambda x: x["xp"], reverse=True)
    for i, entry in enumerate(board):
        entry["rank"] = i + 1
    return board[:top_n]


# ─────────────────────────────────────────
# FULL PROFILE SUMMARY
# ─────────────────────────────────────────

def get_profile_summary(email: str) -> dict:
    data = _load()
    key = email.lower().strip()
    profile = data.get(key, {})
    xp = profile.get("xp", 0)
    level = get_level(xp)
    return {
        "name": profile.get("name", ""),
        "xp": xp,
        "level": level,
        "level_progress_pct": get_level_progress_pct(xp),
        "xp_to_next": get_xp_to_next(xp),
        "badges": get_badges(email),
        "badges_count": len(profile.get("badges", [])),
        "streak": profile.get("streak", 0),
        "sprint_best": profile.get("skill_sprint_best", 0),
        "readiness": profile.get("latest", {}).get("readiness_score", 0)
    }