from datetime import date, datetime
from models.pet import Pet
from config import STREAK_CONTINUE_DAYS, STREAK_RESET_DAYS
from models.analytics import Analytics

class User:
    """
    Object handling the player's profile data (coins, streak, dates),
    and acting as the 'owner' wrapper for their Pet object.
    """
    def __init__(self, profile_dict: dict):
        """
        Initializes the User object directly from the database profile dictionary.
        """
        self.profile = profile_dict
        
        # The User "Owns" a Pet (Composition)
        # We pass the same profile dictionary into the Pet so they stay synchronized!
        self.pet = Pet(self.profile)

    # -----------------------------------------
    # READ-ONLY PROPERTIES 
    # -----------------------------------------
    @property
    def user_id(self) -> str:
        return self.profile.get("user_id", "")
        
    @property
    def username(self) -> str:
        return self.profile.get("username", "Player")

    @property
    def display_name(self) -> str:
        return self.profile.get("full_name") or self.username

    # -----------------------------------------
    # EDITABLE PROPERTIES (Auto-updating the dict)
    # -----------------------------------------
    @property
    def coins(self) -> int:
        return self.profile.get("available_points", 0)
        
    @coins.setter
    def coins(self, value: int):
        self.profile["available_points"] = max(0, value)

    @property
    def current_streak(self) -> int:
        return self.profile.get("current_streak", 0)
        
    @current_streak.setter
    def current_streak(self, value: int):
        self.profile["current_streak"] = max(0, value)

    @property
    def last_active_date(self) -> str:
        return self.profile.get("last_active_date")

    @last_active_date.setter
    def last_active_date(self, value: str):
        self.profile["last_active_date"] = value

    # -----------------------------------------
    # DATE/STREAK LOGIC (Replacing utils.py)
    # -----------------------------------------
    def get_days_inactive(self) -> int:
        """Calculates days passed since the user last completed a task."""
        if not self.last_active_date:
            return 0
            
        last_date = datetime.strptime(self.last_active_date, "%Y-%m-%d").date()
        today = Analytics.get_local_today_date()
        return max(0, (today - last_date).days)

    def _update_streak(self):
        """Internal helper to calculate streak changes when logging a task."""
          
        # If brand new user (no last active date), start streak at 1
        if not self.last_active_date:
            self.current_streak = 1
        else:
            days_inactive = self.get_days_inactive()
            
            # If they haven't logged yesterday or today, it breaks.
            if days_inactive == 0:
                pass # Streak stays unchanged for multiple tasks in one day
            elif days_inactive <= STREAK_CONTINUE_DAYS:
                self.current_streak += 1  # Kept the streak alive!
            else:
                self.current_streak = 1   # Reset
            
        # Update the last active date to right now
        self.last_active_date = Analytics.get_local_today_str()

    # -----------------------------------------
    # MAIN ACTIONS (Replacing heavily nested home.py logic)
    # -----------------------------------------
    def apply_login_decay(self) -> bool:
        """
        Called once on login. Decays the pet and resets streak if needed.
        Returns True if changes were made (so you know to save to the DB).
        """
        days_inactive = self.get_days_inactive()
        
        if days_inactive == 0:
            return False
            
        # Decay the pet
        self.pet.apply_decay(days_inactive)
        
        # Nuke the streak if they missed too many days
        if days_inactive >= STREAK_RESET_DAYS:
            self.current_streak = 0
            
        # We don't update last_active_date here! That only happens on TASK completion.
        return True

    def log_task(self, task: dict) -> dict:
        """
        The massive orchestrated action when a user completes a task.
        Returns the new 'evolved state' if the pet grew!
        """
        points_earned = task.get("points", 0)
        
        # 1. Earn currency and XP
        self.coins += points_earned
        
        # 2. Update streaks
        self._update_streak()
        
        # 3. Apply task boost to the pet (hunger/happiness)
        self.pet.apply_task_boost()
        
        # 4. Give the pet the XP and check for evolution
        new_total_xp = self.pet.total_points + points_earned
        evolved_state = self.pet.check_evolution(new_total_xp)
        
        # Must update the total points AFTER checking evolution 
        self.pet.total_points = new_total_xp
        
        # Ensure the stage name is updated in the raw dictionary for the DB
        self.profile["pet_stage"] = self.pet.current_stage["name"]
        
        return evolved_state

    # -----------------------------------------
    # UTILITY
    # -----------------------------------------
    def to_dict(self) -> dict:
        """
        Returns the raw manipulated dictionary perfectly formatted 
        to be saved directly to the database.
        """
        return self.profile
