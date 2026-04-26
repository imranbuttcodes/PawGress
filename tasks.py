# -----------------------------------------
# TASK DEFINITIONS
# -----------------------------------------
# Each task is a dictionary with:
#   name       → display name shown in UI
#   icon       → emoji shown next to task
#   points     → points earned on completion
#   ask_detail → whether to ask for extra context

TASKS = [
    {"name": "Deep Work / Study",    "icon": "psychology", "points": 10, "ask_detail": True,  "detail_prompt": "What did you focus on?"},
    {"name": "Important Task Done",  "icon": "done_all", "points": 15, "ask_detail": True,  "detail_prompt": "What did you complete?"},
    {"name": "Exercise / Movement",  "icon": "fitness_center", "points": 10, "ask_detail": False, "detail_prompt": None},
    {"name": "Reading / Learning",   "icon": "menu_book", "points": 8,  "ask_detail": True,  "detail_prompt": "What did you read or learn?"},
    {"name": "Healthy Habit",        "icon": "auto_awesome", "points": 3,  "ask_detail": True,  "detail_prompt": "Which habit? (e.g. water, stretch)"},
    {"name": "Sleep on Time",        "icon": "bedtime", "points": 5,  "ask_detail": False, "detail_prompt": None},
    {"name": "Custom Task",          "icon": "settings_suggest", "points": 5,  "ask_detail": True,  "detail_prompt": "Describe your task"}

]



# -----------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------

def get_task_by_name(name):
    """
    Fetches a task dictionary by its name.

    Args:
        name (str): Task name to search for

    Returns:
        dict: Task dictionary or None if not found
    """
    for task in TASKS:
        if task["name"] == name:
            return task
    return None


def get_all_task_names():
    """
    Returns a list of all task names.
    Useful for dropdowns and filters in stats screen.

    Returns:
        list: List of task name strings
    """
    return [task["name"] for task in TASKS]