from supabase import create_client
from dotenv import load_dotenv
import os
import requests
import streamlit as st

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or ""
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or ""
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY") or ""

# Create Supabase client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Admin client for privileged operations
supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

def get_authenticated_client(access_token):
    """
    Creates a new Supabase client that is 'signed in' as a specific user.
    This allows RLS (auth.uid() = user_id) to work correctly.
    """
    client = create_client(SUPABASE_URL, SUPABASE_KEY)
    client.postgrest.headers.update({"Authorization": f"Bearer {access_token}"})
    return client

def _get_db():
    """
    Helper to automatically pick the best client.
    Priority: 
    1. The user's private session client (for RLS)
    2. Create the private client if access_token exists
    3. The default anon client
    """
    if "supabase_client" in st.session_state:
        return st.session_state.supabase_client
    
    token = st.session_state.get("access_token")
    if token:
        st.session_state.supabase_client = get_authenticated_client(token)
        return st.session_state.supabase_client
        
    return supabase

# AUTH FUNCTIONS


def sign_up(email, password):
    """
    Creates a new Supabase Auth account and sends OTP to email.
    Profile is created only after OTP verification.

    Args:
        email (str): User's email address
        password (str): Min 8 chars, must contain letters and digits

    Returns:
        dict: {"success": True} or {"success": False, "error": "..."}
    """
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def sign_in(email, password):
    """
    Authenticates an existing user with email and password.

    Args:
        email (str): User's email address
        password (str): User's password

    Returns:
        dict: {"success": True, "user": user} or {"success": False, "error": "..."}
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        # Phantom capture: Store token for RLS secretly
        if response.session and response.session.access_token:
            st.session_state.access_token = response.session.access_token
            # Clear old client cache so it's rebuilt with the fresh token
            if "supabase_client" in st.session_state:
                del st.session_state.supabase_client

        return {"success": True, "user": response.user, "session": response.session}
    except Exception as e:
        return {"success": False, "error": str(e)}


def sign_out():
    """
    Ends the current Supabase auth session.

    Returns:
        dict: {"success": True} or {"success": False, "error": "..."}
    """
    try:
        supabase.auth.sign_out()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def verify_otp(email, otp_code, username, full_name):
    """
    Verifies the OTP code sent to user's email during signup.
    Creates the user profile after successful verification.

    Args:
        email (str): User's email address
        otp_code (str): 6-digit code entered by user
        username (str): Username to store in profile

    Returns:
        dict: {"success": True, "user": user} or {"success": False, "error": "..."}
    """
    try:
        response = supabase.auth.verify_otp({
            "email": email,
            "token": otp_code,
            "type": "signup"
        })
        user = response.user

        # Create profile only after OTP verified
        if user is None:
            return {"success": False, "error": "OTP verification failed"}

        supabase_admin.table("profiles").insert({
            "user_id": user.id,
            "username": username,
            "email": user.email,
            "full_name": full_name
        }).execute()

        # Phantom capture: Store token for RLS secretly
        if response.session and response.session.access_token:
            st.session_state.access_token = response.session.access_token
            # Clear old client cache so it's rebuilt with fresh token
            if "supabase_client" in st.session_state:
                del st.session_state.supabase_client

        return {"success": True, "user": user, "session": response.session}
    except Exception as e:
        return {"success": False, "error": str(e)}

def resend_otp(email):
    """
    Resends OTP verification email to user.
    Called when user clicks "Resend OTP" on verification screen.

    Args:
        email (str): User's email address

    Returns:
        dict: {"success": True} or {"success": False, "error": "..."}
    """
    try:
        supabase.auth.resend({
            "type": "signup",
            "email": email
        })
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def is_username_taken(username):
    """
    Checks if a username already exists in profiles table.
    Uses admin client to bypass RLS for this pre-login check.
    """
    try:
        response = supabase_admin.table("profiles").select("username").eq("username", username).execute()
        return len(response.data) > 0
    except Exception as e:
        return False


# PROFILE FUNCTIONS


def get_profile(user_id):
    """
    Fetches a user's profile from the profiles table.
    """
    db = _get_db()
    try:
        response = db.table("profiles").select("*").eq("user_id", user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        return None


def update_profile(user_id, updates):
    """
    Updates any fields in the user's profile.
    """
    db = _get_db()
    try:
        db.table("profiles").update(updates).eq("user_id", user_id).execute()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}



# TASK LOG FUNCTIONS

def add_task_log(user_id, task_name, points_earned, task_detail=None):
    """
    Inserts a new task log row when user completes a task.
    """
    db = _get_db()
    try:
        db.table("task_logs").insert({
            "user_id": user_id,
            "task_name": task_name,
            "points_earned": points_earned,
            "task_detail": task_detail
        }).execute()
        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}


def get_task_logs(user_id):
    """
    Fetches all task logs for a user, ordered newest first.
    """
    db = _get_db()
    try:
        response = db.table("task_logs").select("*").eq("user_id", user_id).order("completed_at", desc=True).execute()
        return response.data
    except Exception as e:
        return []
    
def get_email_by_username(username):
    """
    Fetches email from profiles table by username.
    Uses admin client to bypass RLS for this pre-login check.
    """
    try:
        response = supabase_admin.table("profiles").select("email").eq("username", username).execute()
        if response.data:
            return response.data[0]["email"]
        return None
    except Exception as e:
        return None
    

def is_email_taken(email):
    """
    Checks if email already exists in profiles table.
    Uses admin client for pre-login check.
    """
    try:
        response = supabase_admin.table("profiles").select("email").eq("email", email).execute()
        return len(response.data) > 0
    except Exception as e:
        return False



    

def get_user_id_by_email(email):
    """
    Gets Supabase auth user ID by email via profiles table.
    Uses admin client to bypass RLS.
    """
    try:
        response = supabase_admin.table("profiles").select("user_id").eq("email", email).execute()
        if response.data:
            return response.data[0]["user_id"]
        return None
    except:
        return None




def update_password(user_email, new_password):
    """
    Updates password for user by email.
    First signs in with admin privileges then updates password.

    Args:
        user_email (str): User's email
        new_password (str): New password to set

    Returns:
        dict: {"success": True} or {"success": False, "error": str}
    """
       
    try:
        user_id = get_user_id_by_email(user_email)
        if not user_id:
            return {"success": False, "error": "User not found"}

        # Use Supabase REST API with service role key
        headers = {
            "apikey": SUPABASE_SERVICE_KEY,
            "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
            "Content-Type": "application/json"
        }

        response = requests.put(
            f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}",
            headers=headers,
            json={"password": new_password}
        )

        if response.status_code == 200:
            return {"success": True}
        else:
            return {"success": False, "error": response.json()}

    except Exception as e:
        return {"success": False, "error": str(e)}

# ─────────────────────────────────────────
# ACHIEVEMENTS FUNCTIONS
# ─────────────────────────────────────────

def get_achievements(user_id):
    """
    Fetches all earned achievements for a user.
    """
    db = _get_db()
    try:
        response = db.table("achievements").select("*").eq("user_id", user_id).order("earned_at", desc=False).execute()
        return response.data
    except Exception as e:
        return []


def award_badge(user_id, badge_key, badge_name, badge_icon, badge_tier):
    """
    Awards a badge to user if not already earned.
    """
    db = _get_db()
    try:
        # Check if already earned
        existing = db.table("achievements").select("id").eq("user_id", user_id).eq("badge_key", badge_key).execute()

        if existing.data:
            return False  # Already earned

        # Award it!
        db.table("achievements").insert({
            "user_id":    user_id,
            "badge_key":  badge_key,
            "badge_name": badge_name,
            "badge_icon": badge_icon,
            "badge_tier": badge_tier
        }).execute()
        return True  # Newly earned!

    except Exception as e:
        return False


def has_badge(user_id, badge_key):
    """
    Checks if user already has a specific badge.
    """
    db = _get_db()
    try:
        response = db.table("achievements").select("id").eq("user_id", user_id).eq("badge_key", badge_key).execute()
        return len(response.data) > 0
    except:
        return False


def delete_account(user_id):
    """
    Permanently deletes a user's entire account and all related data.
    Uses admin privileges (Service Role Key).
    """
    try:
        # 1. Delete all related data first
        supabase_admin.table("task_logs").delete().eq("user_id", user_id).execute()
        supabase_admin.table("achievements").delete().eq("user_id", user_id).execute()
        supabase_admin.table("profiles").delete().eq("user_id", user_id).execute()

        # 2. Delete the user from Supabase Auth
        supabase_admin.auth.admin.delete_user(user_id)

        return {"success": True}
    except Exception as e:
        return {"success": False, "error": str(e)}
