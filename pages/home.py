import streamlit as st
from database import update_profile
from models.user import User
from models.analytics import Analytics
from datetime import date
from streamlit_lottie import st_lottie
import json
from config import (
    FEED_COST, FEED_RESTORE,
    HUNGER_CRITICAL, HUNGER_WARNING,
    HAPPY_CRITICAL, HAPPY_WARNING,
    PET_LOTTIES  
)


# ----------------------------------------
# HELPER — Pet Display Emoji
# ----------------------------------------

def get_pet_display(stage_name, mood):
    """
    Returns the correct emoji combination based on
    pet stage and current mood.

    Args:
        stage_name (str): Current stage name e.g. "Baby"
        mood (str): Current mood e.g. "Happy"

    Returns:
        str: Emoji string to display
    """
    pet_emojis = {
        "Egg":   {"Happy": "🥚✨", "Neutral": "🥚",   "Sad": "🥚💔"},
        "Baby":  {"Happy": "🐣😊", "Neutral": "🐣",   "Sad": "🐣😢"},
        "Child": {"Happy": "🐥😊", "Neutral": "🐥",   "Sad": "🐥😢"},
        "Teen":  {"Happy": "🐦😊", "Neutral": "🐦",   "Sad": "🐦😢"},
        "Adult": {"Happy": "🦅😊", "Neutral": "🦅",   "Sad": "🦅😢"},
    }
    return pet_emojis.get(stage_name, {}).get(mood, "🥚")



def load_lottie_file(filepath):
    """
    Loads Lottie animation from local JSON file.
    Returns None if file not found — emoji fallback used.

    Args:
        filepath (str): Path to .json file

    Returns:
        dict or None: Lottie JSON data
    """
    try:
        with open(filepath, "r") as f:
            return json.load(f)
    except:
        return None
    

# -----------------------------------------------------------------
# PET FALLBACK FUNCTION IF COULDN'T LOAD LOTTIE FILE FOR ANY REASON
# -----------------------------------------------------------------    

def show_pet_fallback(stage_name, mood_name):
    """Shows emoji fallback when Lottie unavailable"""
    pet_emoji = get_pet_display(stage_name, mood_name)
    st.markdown(
        f"<h1 style='text-align:center; font-size:80px'>{pet_emoji}</h1>",
        unsafe_allow_html=True
    )    


# ----------------------------------------
# HOME SCREEN
# ----------------------------------------

def show_home():
    """
    Displays the home screen with pet, stats and feed button.
    Reads from st.session_state.profile.
    Updates profile in DB when pet is fed.
    """
    profile = st.session_state.profile

    # ── Pet Naming Popup ─────────────────
    # Show ONLY if pet hasn't been named yet
    if not profile.get("pet_name"):
        st.markdown(
            "<h2 style='text-align:center'>🥚 Your pet just hatched!</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='text-align:center; color:gray'>Give your new companion a name!</p>",
            unsafe_allow_html=True
        )

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            pet_name_input = st.text_input(
                "Pet Name",
                placeholder="e.g. Fluffy, Buddy, Max...",
                max_chars=20,
                key="first_pet_name_input"
            )
            if st.button(
                "Name my pet! 🐾",
                use_container_width=True,
                key="first_pet_name_btn"
            ):
                if not pet_name_input.strip():
                    st.error("Please enter a name!")
                else:
                    update_profile(
                        st.session_state.user_id,
                        {"pet_name": pet_name_input.strip()}
                    )
                    st.session_state.profile["pet_name"] = pet_name_input.strip()
                    st.balloons()
                    st.success(f"Your pet is now called **{pet_name_input.strip()}**! 🎉")
                    st.rerun()
        return 


    # Get pet data
    user = User(profile)
    
    total_points    = user.pet.total_points
    available_points = user.coins
    hunger_level    = user.pet.hunger
    happiness_level = user.pet.happiness
    current_streak  = user.current_streak
    last_active_date = user.last_active_date
    
    # OOP Calculate pet state 
    stage      = user.pet.current_stage
    next_stage = user.pet.next_stage
    mood       = user.pet.mood
    pts_needed = user.pet.points_to_next

    # ── Welcome Message ──────────────────
    display_name = profile.get("full_name") or profile["username"]

    st.markdown(
        f"<h2 style='text-align:center'>Welcome back, {display_name}! 👋</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        f"<p style='text-align:center; color:gray'>🔥 {current_streak} day streak</p>",
        unsafe_allow_html=True
    )


    today_str = Analytics.get_local_today_str()
    if last_active_date is not None and last_active_date != today_str:
        st.info("You haven't logged a task today yet — log one task to keep your streak going")

    # ── Pet Display ──────────────────────
    lottie_filepath = PET_LOTTIES.get(stage["name"], {}).get(mood["mood"])

    if lottie_filepath:
        pet_animation = load_lottie_file(lottie_filepath)
        if pet_animation:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st_lottie(
                    pet_animation,
                    height=250,
                    key="pet_anim",
                    loop=True,
                    speed=1
                )
        else:
            # Fallback to emoji
            show_pet_fallback(stage["name"], mood["mood"])
    else:
        # Fallback to emoji
        show_pet_fallback(stage["name"], mood["mood"])

    pet_name = profile.get("pet_name", "My Pet")

    st.markdown(
        f"<h3 style='text-align:center'>✨ {pet_name}</h3>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<h3 style='text-align:center'>{stage['name']} Stage</h3>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<p style='text-align:center; color:{mood['color']}'>{mood['emoji']} {mood['mood']}</p>",
        unsafe_allow_html=True
    )
    st.markdown("")

    # ── Hunger & Happiness Bars ──────────
    with st.container(border=True):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**🍖 Hunger**")
            st.progress(hunger_level / 100)
            st.markdown(f"<p style='text-align:center'>{hunger_level}/100</p>", unsafe_allow_html=True)

        with col2:
            st.markdown("**😊 Happiness**")
            st.progress(happiness_level / 100)
            st.markdown(f"<p style='text-align:center'>{happiness_level}/100</p>", unsafe_allow_html=True)

    st.markdown("")

    # ── Sleek Stats Bar (Mobile Optimized) ───────────────
    evolution_label = f"{next_stage['emoji']} {next_stage['name']}" if next_stage else "Evolution"
    evolution_val   = f"{pts_needed} pts away" if next_stage else "🏆 Max Stage!"

    st.markdown(f"""
        <style>
        .home-stats-container {{
            display: flex;
            justify-content: space-around;
            align-items: center;
            gap: 10px;
            background: rgba(128, 128, 128, 0.05);
            padding: 20px 10px;
            border-radius: 20px;
            margin-bottom: 25px;
            border: 1px solid rgba(128, 128, 128, 0.1);
            backdrop-filter: blur(10px);
            flex-wrap: wrap;
        }}
        .home-stat-card {{
            text-align: center;
            flex: 1;
            min-width: 90px;
            padding: 5px;
        }}
        .home-stat-value {{
            font-size: 20px;
            font-weight: 800;
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 6px;
            color: var(--text-color);
        }}
        .home-stat-label {{
            font-size: 10px;
            color: var(--secondary-text-color);
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 1.2px;
            font-weight: 600;
        }}
        </style>

        <div class="home-stats-container">
            <div class="home-stat-card">
                <p class="home-stat-value">⭐ {total_points}</p>
                <p class="home-stat-label">Total XP</p>
            </div>
            <div class="home-stat-card">
                <p class="home-stat-value">🪙 {available_points}</p>
                <p class="home-stat-label">Coins</p>
            </div>
            <div class="home-stat-card">
                <p class="home-stat-value">{pts_needed if next_stage else "🏆"}</p>
                <p class="home-stat-label">{evolution_label if next_stage else "Max Level"}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Evolution progress bar
    if next_stage:
        progress = 1 - (pts_needed / (next_stage["min_points"] - stage["min_points"]))
        progress = max(0.0, min(1.0, progress))
        st.markdown(f"**Evolution Progress → {next_stage['name']}**")
        st.progress(progress)

    st.markdown("")

    # ---- Feed Pet Button -----------------
    with st.container(border=True):
        st.markdown("### Feed Your Pet")

        if hunger_level >= 100:
            st.info("Your pet is already full! 😊 Log tasks to keep it happy!")
        elif available_points < FEED_COST:
            st.warning(f"Not enough points to feed! You need {FEED_COST} coins.")
        else:
            st.markdown(f"_Costs {FEED_COST} coins — fills hunger meter by +{FEED_RESTORE} hunger_")
            if st.button(f"Feed Pet 🍖 (-{FEED_COST} coins)", use_container_width=True, key="feed_btn"):
                user.coins -= FEED_COST
                user.pet.feed(FEED_RESTORE)

                update_profile(st.session_state.user_id, {
                    "available_points": user.coins,
                    "hunger_level": user.pet.hunger
                })

                st.session_state.profile.update(user.to_dict())

                st.success("Your pet has been fed! 🎉")
                st.rerun()

    # ---- Pet Status Warning ------------
    if hunger_level <= HUNGER_CRITICAL:
        st.error("Your pet is very hungry! Feed it now!")
    elif hunger_level <= HUNGER_WARNING:
        st.warning("Your pet is getting hungry. Log tasks to earn points!")

    if happiness_level <= HAPPY_CRITICAL:
        st.error("😢 Your pet is very sad! Complete tasks to cheer it up!")
    elif happiness_level <= HAPPY_WARNING:
        st.warning("😐 Your pet is feeling down. Log some tasks!")