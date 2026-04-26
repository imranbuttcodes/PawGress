# ─────────────────────────────────────────
# PAWGRESS — APP CONFIGURATION
# ─────────────────────────────────────────
# All configurable values in one place.
# Change anything here without touching
# any other file in the project.
# ─────────────────────────────────────────


# ─────────────────────────────────────────
# APP INFO
# ─────────────────────────────────────────

APP_NAME    = "PawGress"
APP_VERSION = "1.0.0"
APP_ICON    = "🐾"
APP_LOGO    = "assets/logo.png" # just the path string
APP_TAGLINE = "Stay productive. Keep your pet happy."


# ─────────────────────────────────────────
# FEED PET CONFIGURATION
# ─────────────────────────────────────────

FEED_COST    = 10   # points spent per feed
FEED_RESTORE = 5   # hunger restored per feed


# ─────────────────────────────────────────
# DECAY CONFIGURATION
# ─────────────────────────────────────────
# How much hunger/happiness drops per inactive day

HUNGER_DECAY_PER_DAY    = 10   # hunger drops 10 per inactive day
HAPPINESS_DECAY_PER_DAY = 15   # happiness drops 15 per inactive day


# ─────────────────────────────────────────
# TASK BOOST CONFIGURATION
# ─────────────────────────────────────────
# How much hunger/happiness increases per task logged

TASK_HUNGER_BOOST    = 5    # hunger +5 per task
TASK_HAPPINESS_BOOST = 8    # happiness +8 per task


# ─────────────────────────────────────────
# PET MOOD THRESHOLDS
# ─────────────────────────────────────────

HAPPY_THRESHOLD   = 70   # happiness >= 70 → Happy
NEUTRAL_THRESHOLD = 40   # happiness >= 40 → Neutral
                          # happiness <  40 → Sad


# ─────────────────────────────────────────
# PET WARNING THRESHOLDS
# ─────────────────────────────────────────
# When to show warning messages on home screen

HUNGER_CRITICAL  = 20   # show red error
HUNGER_WARNING   = 40   # show yellow warning
HAPPY_CRITICAL   = 20   # show red error
HAPPY_WARNING    = 40   # show yellow warning


# ─────────────────────────────────────────
# EVOLUTION THRESHOLDS
# ─────────────────────────────────────────

EGG_THRESHOLD   = 0
BABY_THRESHOLD  = 50
CHILD_THRESHOLD = 150
TEEN_THRESHOLD  = 350
ADULT_THRESHOLD = 600


# ─────────────────────────────────────────
# STREAK CONFIGURATION
# ─────────────────────────────────────────

STREAK_CONTINUE_DAYS = 1   # consecutive days needed to continue streak
STREAK_RESET_DAYS    = 2   # days missed before streak resets


# ─────────────────────────────────────────
# STATS CONFIGURATION
# ─────────────────────────────────────────

ACTIVITY_GRAPH_WEEKS = 5   # how many weeks to show in activity graph
MAX_RECENT_LOGS      = 10  # max task logs shown in recent activity


# ─────────────────────────────────────────
# PET ANIMATION CONFIGURATION
# ─────────────────────────────────────────

PET_LOTTIES = {
    "Egg": {
        "Happy":   "assets/pets/egg_happy.json",
        "Neutral": "assets/pets/egg_neutral.json",
        "Sad":     "assets/pets/egg_sad.json"
    },
    "Baby": {
        "Happy":   "assets/pets/baby_happy.json",
        "Neutral": "assets/pets/baby_neutral.json",
        "Sad":     "assets/pets/baby_sad.json"
    },
    "Child": {
        "Happy":   "assets/pets/child_happy.json",
        "Neutral": "assets/pets/child_neutral.json",
        "Sad":     "assets/pets/child_sad.json"
    },
    "Teen": {
        "Happy":   "assets/pets/teen_happy.json",
        "Neutral": "assets/pets/teen_neutral.json",
        "Sad":     "assets/pets/teen_sad.json"
    },
    "Adult": {
        "Happy":   "assets/pets/adult_happy.json",
        "Neutral": "assets/pets/adult_neutral.json",
        "Sad":     "assets/pets/adult_sad.json"
    }
}


# ─────────────────────────────────────────
# OTP EXPIRY SECOND CONSTANT
# ─────────────────────────────────────────

OTP_EXPIRY_SECONDS = 600 


# ─────────────────────────────────────────
# BADGE THRESHOLDS
# ─────────────────────────────────────────

# Streak badges
BADGE_STREAK_BRONZE   = 3    # On a Roll
BADGE_STREAK_SILVER_1 = 7    # Week Warrior
BADGE_STREAK_SILVER_2 = 14   # Unstoppable
BADGE_STREAK_GOLD     = 30   # Legend

# Task count badges
BADGE_TASKS_BRONZE_1  = 1    # First Step
BADGE_TASKS_BRONZE_2  = 10   # Getting Started
BADGE_TASKS_SILVER    = 50   # Consistent
BADGE_TASKS_GOLD      = 100  # Centurion

# XP badges
BADGE_XP_SILVER       = 500   # XP Hunter
BADGE_XP_GOLD         = 1000  # Rich

# Tasks per day badges
BADGE_DAY_BRONZE      = 3    # Grinder
BADGE_DAY_GOLD        = 5    # Overachiever

# Time badges
BADGE_EARLY_BIRD_HOUR = 8    # Before 8 AM
BADGE_NIGHT_OWL_HOUR  = 22   # After 10 PM

# Pet stage order
BADGE_PET_STAGES = ["Egg", "Baby", "Child", "Teen", "Adult"]

# ─────────────────────────────────────────
# TIMEZONE CONFIGURATION
# ─────────────────────────────────────────
# Fallback timezone if browser detection fails
DEFAULT_TIMEZONE = "Asia/Karachi" # GMT+5

