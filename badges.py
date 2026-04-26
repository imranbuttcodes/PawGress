# ─────────────────────────────────────────
# PAWGRESS — BADGE DEFINITIONS
# ─────────────────────────────────────────
# All badge definitions and check logic
# No DB calls here — only logic
# ─────────────────────────────────────────


from collections import Counter
from models.analytics import Analytics
from config import (
    BADGE_STREAK_BRONZE, BADGE_STREAK_SILVER_1,
    BADGE_STREAK_SILVER_2, BADGE_STREAK_GOLD,
    BADGE_TASKS_BRONZE_1, BADGE_TASKS_BRONZE_2,
    BADGE_TASKS_SILVER, BADGE_TASKS_GOLD,
    BADGE_XP_SILVER, BADGE_XP_GOLD,
    BADGE_DAY_BRONZE, BADGE_DAY_GOLD,
    BADGE_EARLY_BIRD_HOUR, BADGE_NIGHT_OWL_HOUR,
    BADGE_PET_STAGES
)


# ─────────────────────────────────────────
# BADGE CATALOG
# ─────────────────────────────────────────

BADGES = {
    # ── Streak Badges ─────────────────────
    "on_a_roll": {
        "key":  "on_a_roll",
        "name": "On a Roll",
        "icon": "🔥",
        "tier": "B",
        "desc": f"{BADGE_STREAK_BRONZE} day streak",
        "category": "streak"
    },
    "week_warrior": {
        "key":  "week_warrior",
        "name": "Week Warrior",
        "icon": "📅",
        "tier": "S",
        "desc": f"{BADGE_STREAK_SILVER_1} day streak",
        "category": "streak"
    },
    "unstoppable": {
        "key":  "unstoppable",
        "name": "Unstoppable",
        "icon": "⚡",
        "tier": "S",
        "desc": f"{BADGE_STREAK_SILVER_2} day streak",
        "category": "streak"
    },
    "legend": {
        "key":  "legend",
        "name": "Legend",
        "icon": "👑",
        "tier": "G",
        "desc": f"{BADGE_STREAK_GOLD} day streak",
        "category": "streak"
    },

    # ── Task Badges ───────────────────────
    "first_step": {
        "key":  "first_step",
        "name": "First Step",
        "icon": "🐾",
        "tier": "B",
        "desc": "First task ever",
        "category": "tasks"
    },
    "getting_started": {
        "key":  "getting_started",
        "name": "Getting Started",
        "icon": "🌱",
        "tier": "B",
        "desc": f"{BADGE_TASKS_BRONZE_2} tasks done",
        "category": "tasks"
    },
    "consistent": {
        "key":  "consistent",
        "name": "Consistent",
        "icon": "⭐",
        "tier": "S",
        "desc": f"{BADGE_TASKS_SILVER} tasks done",
        "category": "tasks"
    },
    "centurion": {
        "key":  "centurion",
        "name": "Centurion",
        "icon": "💯",
        "tier": "G",
        "desc": f"{BADGE_TASKS_GOLD} tasks done",
        "category": "tasks"
    },

    # ── XP Badges ─────────────────────────
    "xp_hunter": {
        "key":  "xp_hunter",
        "name": "XP Hunter",
        "icon": "💰",
        "tier": "S",
        "desc": f"{BADGE_XP_SILVER} total XP",
        "category": "xp"
    },
    "rich": {
        "key":  "rich",
        "name": "Rich",
        "icon": "🤑",
        "tier": "G",
        "desc": f"{BADGE_XP_GOLD} total XP",
        "category": "xp"
    },
    "grinder": {
        "key":  "grinder",
        "name": "Grinder",
        "icon": "💪",
        "tier": "B",
        "desc": f"{BADGE_DAY_BRONZE} tasks in a day",
        "category": "xp"
    },
    "overachiever": {
        "key":  "overachiever",
        "name": "Overachiever",
        "icon": "⚡",
        "tier": "G",
        "desc": f"{BADGE_DAY_GOLD} tasks in a day",
        "category": "xp"
    },

    # ── Time Badges ───────────────────────
    "early_bird": {
        "key":  "early_bird",
        "name": "Early Bird",
        "icon": "🌅",
        "tier": "B",
        "desc": f"Task before {BADGE_EARLY_BIRD_HOUR} AM",
        "category": "time"
    },
    "night_owl": {
        "key":  "night_owl",
        "name": "Night Owl",
        "icon": "🦉",
        "tier": "B",
        "desc": f"Task after {BADGE_NIGHT_OWL_HOUR - 12} PM",
        "category": "time"
    },

    # ── Pet Badges ────────────────────────
    "hatchling": {
        "key":  "hatchling",
        "name": "Hatchling",
        "icon": "🥚",
        "tier": "B",
        "desc": "Reached Baby stage",
        "category": "pet"
    },
    "growing_up": {
        "key":  "growing_up",
        "name": "Growing Up",
        "icon": "🐣",
        "tier": "S",
        "desc": "Reached Child stage",
        "category": "pet"
    },
    "teen_spirit": {
        "key":  "teen_spirit",
        "name": "Teen Spirit",
        "icon": "😽",
        "tier": "S",
        "desc": "Reached Teen stage",
        "category": "pet"
    },
    "full_grown": {
        "key":  "full_grown",
        "name": "Full Grown",
        "icon": "🐉",
        "tier": "G",
        "desc": "Reached Adult stage",
        "category": "pet"
    },
}


# ─────────────────────────────────────────
# BADGE CHECK FUNCTIONS
# ─────────────────────────────────────────

def check_badges(profile, task_logs):
    """
    Checks which badges user should earn based on
    current profile and task logs.
    Returns list of badge keys that should be awarded.

    Args:
        profile (dict): User's full profile
        task_logs (list): All user's task logs

    Returns:
        list: Badge keys that should be awarded
    """
    to_award = []
    total_tasks  = len(task_logs)
    total_points = profile.get("total_points", 0)
    streak       = profile.get("current_streak", 0)
    pet_stage    = profile.get("pet_stage", "Egg")

    # ── Streak checks ─────────────────────
    if streak >= BADGE_STREAK_BRONZE:
        to_award.append("on_a_roll")
    if streak >= BADGE_STREAK_SILVER_1:
        to_award.append("week_warrior")
    if streak >= BADGE_STREAK_SILVER_2:
        to_award.append("unstoppable")
    if streak >= BADGE_STREAK_GOLD:
        to_award.append("legend")

    # ── Task count checks ─────────────────
    if total_tasks >= BADGE_TASKS_BRONZE_1:
        to_award.append("first_step")
    if total_tasks >= BADGE_TASKS_BRONZE_2:
        to_award.append("getting_started")
    if total_tasks >= BADGE_TASKS_SILVER:
        to_award.append("consistent")
    if total_tasks >= BADGE_TASKS_GOLD:
        to_award.append("centurion")

    # ── XP checks ────────────────────────
    if total_points >= BADGE_XP_SILVER:
        to_award.append("xp_hunter")
    if total_points >= BADGE_XP_GOLD:
        to_award.append("rich")

    # ── Tasks per day checks ──────────────
    date_counts = Counter(
        Analytics.convert_to_local(log["completed_at"])[0]
        for log in task_logs
    )
    max_tasks_day = max(date_counts.values()) if date_counts else 0

    if max_tasks_day >= BADGE_DAY_BRONZE:
        to_award.append("grinder")
    if max_tasks_day >= BADGE_DAY_GOLD:
        to_award.append("overachiever")

    # ── Time checks ───────────────────────
    for log in task_logs:
        try:
            hour = Analytics.get_local_hour(log["completed_at"])  
            if hour < BADGE_EARLY_BIRD_HOUR:
                to_award.append("early_bird")
                break
        except:
            pass

    for log in task_logs:
        try:
            hour = Analytics.get_local_hour(log["completed_at"])  
            if hour >= BADGE_NIGHT_OWL_HOUR:
                to_award.append("night_owl")  
                break
        except:
            pass

    # ── Pet stage checks ──────────────────
    current_idx  =  BADGE_PET_STAGES.index(pet_stage) if pet_stage in BADGE_PET_STAGES else 0

    if current_idx >= 1:
        to_award.append("hatchling")
    if current_idx >= 2:
        to_award.append("growing_up")
    if current_idx >= 3:
        to_award.append("teen_spirit")
    if current_idx >= 4:
        to_award.append("full_grown")

    return to_award


def get_new_badges(profile, task_logs, earned_keys):
    """
    Returns only badges that should be awarded
    but haven't been earned yet.

    Args:
        profile (dict): User's profile
        task_logs (list): All task logs
        earned_keys (list): Already earned badge keys

    Returns:
        list: Badge dicts to award
    """
    should_have = check_badges(profile, task_logs)
    new_ones    = [
        BADGES[key] for key in should_have
        if key not in earned_keys and key in BADGES
    ]
    return new_ones