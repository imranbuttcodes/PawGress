from config import (
    HUNGER_DECAY_PER_DAY, HAPPINESS_DECAY_PER_DAY,
    TASK_HUNGER_BOOST, TASK_HAPPINESS_BOOST,
    HAPPY_THRESHOLD, NEUTRAL_THRESHOLD,
    EGG_THRESHOLD, BABY_THRESHOLD, CHILD_THRESHOLD,
    TEEN_THRESHOLD, ADULT_THRESHOLD, HUNGER_CRITICAL, HUNGER_WARNING
)

# -----------------------------------------
# PET STAGES DICTIONARIES 
# -----------------------------------------
PET_STAGES = [
    {"name": "Egg",   "min_points": EGG_THRESHOLD,   "emoji": "🥚"},
    {"name": "Baby",  "min_points": BABY_THRESHOLD,  "emoji": "🐣"},
    {"name": "Child", "min_points": CHILD_THRESHOLD, "emoji": "🐥"},
    {"name": "Teen",  "min_points": TEEN_THRESHOLD,  "emoji": "🐦"},
    {"name": "Adult", "min_points": ADULT_THRESHOLD, "emoji": "🦅"},
]


class Pet:
    """
    Object handling all the logic, stats, and evolution metrics
    for the user's pet. 
    """
    def __init__(self, profile_dict):
        """
        Initializes the Pet object directly from the database profile dictionary.
        """
        self.profile = profile_dict
        self.name = profile_dict.get("pet_name", "My Pet")

    # -----------------------------------------
    # PROPERTIES (Accessed like variables, but run as functions)
    # -----------------------------------------
    @property
    def hunger(self) -> int:
        return self.profile.get("hunger_level", 100)
    
    @hunger.setter
    def hunger(self, value: int):
        self.profile["hunger_level"] = max(0, min(100, value))

    @property
    def happiness(self) -> int:
        return self.profile.get("happiness_level", 100)
        
    @happiness.setter
    def happiness(self, value: int):
        self.profile["happiness_level"] = max(0, min(100, value))

    @property
    def total_points(self) -> int:
        return self.profile.get("total_points", 0)

    @total_points.setter
    def total_points(self, value: int):
        self.profile["total_points"] = value


    @property
    def current_stage(self) -> dict:
        """Returns the pet's current evolution stage based on total points."""
        current = PET_STAGES[0]
        for stage in PET_STAGES:
            if self.total_points >= stage["min_points"]:
                current = stage
        return current

    @property
    def next_stage(self) -> dict:
        """Returns the next evolution stage target."""
        for stage in PET_STAGES:
            if self.total_points < stage["min_points"]:
                return stage
        return None  # Max stage

    @property
    def points_to_next(self) -> int:
        """Calculates points needed to reach the next stage."""
        nxt = self.next_stage
        if nxt is None:
            return 0
        return nxt["min_points"] - self.total_points

    @property
    def mood(self) -> dict:
        """Determines pet's emotional state based on happiness and hunger."""
        if self.hunger <= HUNGER_CRITICAL:
            return {"mood": "Sad", "emoji": "😢", "color": "red"}
        
        if self.hunger <= HUNGER_WARNING and self.happiness >= HAPPY_THRESHOLD:
            return {"mood": "Neutral", "emoji": "😐", "color": "orange"}

        if self.happiness >= HAPPY_THRESHOLD:
            return {"mood": "Happy", "emoji": "😊", "color": "green"}
        elif self.happiness >= NEUTRAL_THRESHOLD:
            return {"mood": "Neutral", "emoji": "😐", "color": "orange"}
        else:
            return {"mood": "Sad", "emoji": "😢", "color": "red"}

    # -----------------------------------------
    # METHODS
    # -----------------------------------------
    def feed(self, restore_amount: int):
        """Restores hunger by the given amount."""
        self.hunger += restore_amount

    def apply_decay(self, days_inactive: int):
        """Reduces happiness and hunger based on days inactive."""
        if days_inactive > 0:
            self.hunger -= (days_inactive * HUNGER_DECAY_PER_DAY)
            self.happiness -= (days_inactive * HAPPINESS_DECAY_PER_DAY)

    def apply_task_boost(self):
        """Boosts pet stats when a task is completed."""
        self.hunger += TASK_HUNGER_BOOST
        self.happiness += TASK_HAPPINESS_BOOST

    def check_evolution(self, new_total_points: int) -> dict:
        """
        Checks if adding points will cause an evolution.
        Returns the new stage dict if evolved, or None.
        """
        old_stage = self.current_stage
        
        # Temporarily fake the points calculation to see if it evolves
        temp_pet = Pet({"total_points": new_total_points})
        new_stage = temp_pet.current_stage
        
        if old_stage["name"] != new_stage["name"]:
            return new_stage
        return None
