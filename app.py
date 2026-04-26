import streamlit as st
from auth import show_auth  
from database import get_profile, update_profile, sign_out
from models.user import User
from pages.home import show_home
from pages.task_logger import show_task_logger
from pages.stats import show_stats
from pages.logbook import show_logbook
from config import APP_NAME, APP_ICON, APP_LOGO
from PIL import Image
from pages.achievements import show_achievements

# ----------------------------------------
# PAGE CONFIGURATION
# ----------------------------------------


# Load the app logo
try:
    icon = Image.open(APP_LOGO)
except:
    icon = APP_ICON

st.set_page_config(
    page_title=APP_NAME,
    page_icon=icon,
    layout="centered",
    initial_sidebar_state="auto"
)


# ----------------------------------------
# CUSTOM CSS
# ----------------------------------------

st.markdown("""
    <style>
        /* Hide Streamlit default menu and footer */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
            
        /* Hide default sidebar navigation */
        [data-testid="stSidebarNav"] {display: none !important;}

        /* Custom button styling */
        .stButton > button {
            border-radius: 12px;
            font-weight: 600;
        }

        /* Center the main content */
        .block-container {
            padding-top: 2rem;
            max-width: 700px;
        }
    </style>
""", unsafe_allow_html=True)


# ----------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------

def load_user_profile():
    """
    Loads user profile from Supabase and stores in session state.
    Called once after login and on every page refresh.

    Returns:
        dict: User profile or None if not found
    """
    profile = get_profile(st.session_state.user_id)
    if profile:
        st.session_state.profile = profile
    return profile


def handle_login_decay():
    """
    Applies hunger and happiness decay based on days inactive.
    Called once per session after profile is loaded.
    Only runs if not already handled this session.
    """
    # Only run once per session
    if st.session_state.get("decay_applied"):
        return

    user = User(st.session_state.profile)
    changes_made = user.apply_login_decay()

    if changes_made:
        updates = user.to_dict()
        update_profile(st.session_state.user_id, updates)
        # Update local profile too
        st.session_state.profile.update(updates)

    # Mark decay as applied for this session
    st.session_state.decay_applied = True


def show_sidebar():
    """
    Displays the sidebar with navigation buttons and logout.
    Shows current pet stage and points at the top.
    """
    with st.sidebar:
        # ── Global App Logo ──
        try:
            st.image(APP_LOGO, use_container_width=True)
        except Exception:
            pass # Fails gracefully if no image is found
            
        profile = st.session_state.profile

        # User info
        st.markdown(f"### :material/account_circle: {profile['username']}")
        st.markdown(f"**Total XP:** ⭐ {profile['total_points']}")
        st.markdown(f"**Coins:** 🪙 {profile.get('available_points', 0)}")
        st.markdown(f"**Streak:** 🔥 {profile['current_streak']} days")
        st.markdown("---")

        # Navigation
        st.markdown("### Navigation")

        if st.button("Home", use_container_width=True, key="nav_home", icon = ":material/home:"):
            st.session_state.current_page = "home"
            st.rerun()

        if st.button("Log Task", use_container_width=True, key="nav_tasks",  icon=":material/check_circle:"):
            st.session_state.current_page = "tasks"
            st.rerun()

        if st.button("Stats", use_container_width=True, key="nav_stats", icon=":material/bar_chart:"):
            st.session_state.current_page = "stats"
            st.rerun()

        if st.button("Logbook", use_container_width=True, key="nav_logbook", icon=":material/menu_book:"):
            st.session_state.current_page = "logbook"
            st.rerun()
        
        if st.button("Achievements", use_container_width=True,
             key="nav_achievements",
             icon=":material/emoji_events:"):
                st.session_state.current_page = "achievements"
                st.rerun()

        if st.button("Profile & Settings", use_container_width=True,
             key="nav_profile",
             icon=":material/manage_accounts:"):
                st.session_state.current_page = "profile"
                st.rerun()


# ----------------------------------------
# MAIN APP
# ----------------------------------------

def main():
    """
    Main entry point of the app.
    Routes between auth screen and main app based on login state.
    """
    # Check if user is logged in

    if "user" not in st.session_state:
        show_auth()
        return

    # User is logged in — load their profile
    profile = load_user_profile()

    # If profile not found something went wrong
    if not profile:
        st.error("Profile not found. Please logout and login again.")
        if st.button("Logout"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        return
    
    # Apply login decay once per session
    handle_login_decay()

    # Initialize current page if not set
    if "current_page" not in st.session_state:
        st.session_state.current_page = "home"

    # Show sidebar
    show_sidebar()

    # Route to correct page
    if st.session_state.current_page == "home":
        show_home()
    elif st.session_state.current_page == "tasks":
        show_task_logger()
    elif st.session_state.current_page == "stats":
        show_stats()
    elif st.session_state.current_page == "logbook":
        show_logbook()
    elif st.session_state.current_page == "achievements":
        show_achievements()
    elif st.session_state.current_page == "profile":
        from pages.profile import show_profile
        show_profile()


# ----------------------------------------
# RUN APP
# ----------------------------------------
if __name__ == "__main__":
    main()