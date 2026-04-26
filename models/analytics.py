from datetime import datetime
import pytz
import streamlit as st
from config import DEFAULT_TIMEZONE

class Analytics:
    """
    Object handling complex data manipulation for charts and reports.
    Uses static methods because it doesn't need to store live state,
    it just processes arrays of dictionaries into clean chart data!
    """

    @staticmethod
    def convert_to_local(timestamp_str):
        """
        Converts UTC timestamp to user's browser timezone.
        Falls back to UTC if timezone unavailable.
        
        Args:
            timestamp_str (str): Supabase UTC timestamp
            
        Returns:
            tuple: (date_str, time_str) in local timezone
        """
        try:
            tz_str = st.context.timezone or DEFAULT_TIMEZONE
            tz     = pytz.timezone(tz_str)
        except:
            tz = pytz.timezone(DEFAULT_TIMEZONE)

        try:
            raw    = timestamp_str.replace("Z", "+00:00")
            utc_dt = datetime.fromisoformat(raw)
            local  = utc_dt.astimezone(tz)
            return local.strftime("%Y-%m-%d"), local.strftime("%I:%M %p")
        except:
            return timestamp_str[:10], "--:--"

    @staticmethod
    def get_local_today_date():
        """Returns the current date mathematically locked strictly to the user's timezone."""
        try:
            tz_str = st.context.timezone or DEFAULT_TIMEZONE
            tz     = pytz.timezone(tz_str)
        except:
            tz = pytz.timezone(DEFAULT_TIMEZONE)
        return datetime.now(tz).date()

    @staticmethod
    def get_local_today_str() -> str:
        """Returns today's date formatted as YYYY-MM-DD in the user's timezone."""
        return Analytics.get_local_today_date().strftime("%Y-%m-%d")
    

    @staticmethod
    def get_local_hour(timestamp_str):
        """
        Returns local hour from UTC timestamp.
        Used for Early Bird and Night Owl badge checks.
        
        Args:
            timestamp_str (str): Supabase UTC timestamp
            
        Returns:
            int: Local hour (0-23)
        """
        try:
            tz_str = st.context.timezone or DEFAULT_TIMEZONE
            tz     = pytz.timezone(tz_str)
        except:
            tz = pytz.timezone(DEFAULT_TIMEZONE)

        try:
            raw    = timestamp_str.replace("Z", "+00:00")
            utc_dt = datetime.fromisoformat(raw)
            local  = utc_dt.astimezone(tz)
            return local.hour
        except:
            return int(timestamp_str[11:13])  # fallback UTC hour

    @staticmethod
    def format_date(date_str: str) -> str:
        """Converts YYYY-MM-DD to readable format."""
        if not date_str:
            return "Never"
        dt = datetime.strptime(date_str[:10], "%Y-%m-%d")
        return dt.strftime("%B %d, %Y")

    @staticmethod
    def group_logs_by_date(task_logs: list) -> dict:
        """Groups logs by date for heatmap using local timezone!"""
        grouped = {}
        for log in task_logs:
            local_date, _ = Analytics.convert_to_local(log["completed_at"])
            grouped[local_date] = grouped.get(local_date, 0) + 1
        return grouped

    @staticmethod
    def get_most_completed_task(task_logs: list) -> str:
        """Finds most completed task."""
        if not task_logs:
            return None
        task_counts = Analytics.get_task_count_by_type(task_logs)
        if not task_counts:
            return None
        return max(task_counts, key=lambda k: task_counts[k])

    @staticmethod
    def get_points_by_date(task_logs: list) -> dict:
        """Groups points by date for line chart using local timezone"""
        points_by_date = {}
        for log in task_logs:
            local_date, _ = Analytics.convert_to_local(log["completed_at"])
            points_by_date[local_date] = points_by_date.get(local_date, 0) + log["points_earned"]
        return points_by_date

    @staticmethod
    def get_task_count_by_type(task_logs: list) -> dict:
        """Counts how many times each task was done."""
        task_counts = {}
        for log in task_logs:
            name = log["task_name"]
            task_counts[name] = task_counts.get(name, 0) + 1
        return task_counts
