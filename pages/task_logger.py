import streamlit as st
from tasks import TASKS
from models.user import User
from pages.achievements import process_badges
from database import (
    add_task_log,
    update_profile,
    get_achievements,
    get_task_logs
)



# ----------------------------------------
# TASK LOGGER SCREEN
# ----------------------------------------

def show_task_logger():
    """
    Displays the task logging screen.
    User can log predefined or custom tasks to earn points.
    Updates profile and task_logs in Supabase after each task.
    """


    if st.session_state.get("evolution_stage"):
        evolved = st.session_state.evolution_stage
        st.balloons()
        st.success(f"Evolution complete. Your pet is now a {evolved['name']} {evolved['emoji']}.")

        if st.button("Continue →", use_container_width=True, key="evolve_continue_btn"):
            del st.session_state.evolution_stage
            st.rerun()
        return
    
    # ── New badge notifications ───────────
    if st.session_state.get("new_badges"):
        for badge in st.session_state.new_badges:
            st.success(f"Badge unlocked: {badge}")
        del st.session_state.new_badges
    

    user = User(st.session_state.profile)
    

    # Get current values
    total_points    = user.pet.total_points
    available_points = user.coins
    hunger_level    = user.pet.hunger
    happiness_level = user.pet.happiness
    current_streak  = user.current_streak

    # ----- Header ----------------------------
    st.markdown("<h2 style='text-align:center'>Log a Task</h2>", unsafe_allow_html=True )
    st.markdown(
        "<p style='text-align:center; color:gray'>Complete tasks to earn points and keep your pet happy!</p>",
        unsafe_allow_html=True
    )
    st.markdown("")


    # --- Sleek Stats Bar (Theme Compatible) -----------------
    st.markdown("""
        <style>
        .stats-container {
            display: flex;
            justify-content: space-around;
            background: rgba(128, 128, 128, 0.05);
            padding: 25px 15px;
            border-radius: 20px;
            margin-bottom: 35px;
            border: 1px solid rgba(128, 128, 128, 0.1);
            backdrop-filter: blur(10px);
        }
        .stat-card {
            text-align: center;
            flex: 1;
        }
        .stat-value {
            font-size: 24px;
            font-weight: 800;
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        .stat-label {
            font-size: 11px;
            color: #888;
            margin-top: 5px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 600;
        }
        .task-card-inner {
            padding: 5px;
        }
        </style>
        <div class="stats-container">
            <div class="stat-card">
                <p class="stat-value">⭐ """ + str(total_points) + """</p>
                <p class="stat-label">Total XP</p>
            </div>
            <div class="stat-card">
                <p class="stat-value">🪙 """ + str(available_points) + """</p>
                <p class="stat-label">Coins</p>
            </div>
            <div class="stat-card">
                <p class="stat-value">😊 """ + str(happiness_level) + """%</p>
                <p class="stat-label">Happy</p>
            </div>
            <div class="stat-card">
                <p class="stat-value">🔥 """ + str(current_streak) + """</p>
                <p class="stat-label">Streak</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # --- Task Detail Popup State -------------
    # Initialize selected task state
    if "selected_task" not in st.session_state:
        st.session_state.selected_task = None

    # --- Professional Task Grid -----------------
    st.markdown("### Choose a Task")
    st.markdown("<p style='color:#888; font-size:14px; margin-bottom:20px;'>Record your wins and grow your pet.</p>", unsafe_allow_html=True)

    # Use a 2-column grid for tasks for a more 'app-like' feel
    task_cols = st.columns(2)
    
    for i, task in enumerate(TASKS):
        col_idx = i % 2
        with task_cols[col_idx]:
            with st.container(border=True):
                # Using a single row of columns for better vertical alignment
                tc1, tc2 = st.columns([3, 2])
                with tc1:
                    st.markdown(f"**:material/{task['icon']}: {task['name']}**")
                    st.markdown(f"<p style='color:#40c463; font-size:18px; font-weight:700; margin:0;'>+{task['points']} XP</p>", unsafe_allow_html=True)
                with tc2:
                    st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
                    if st.button("Log Now", key=f"task_{task['name']}", use_container_width=True):
                        st.session_state.selected_task = task
                        st.rerun()

    # --- Task Detail Logic (Glassmorphism Modal-like container) ---
    if st.session_state.selected_task:
        task = st.session_state.selected_task
        
        st.markdown("")
        
        # We wrap the confirmation in a clean container with custom CSS for the 'modal' look
        st.markdown(f"""
            <style>
            .confirm-container {{
                background: rgba(64, 196, 99, 0.08);
                padding: 25px;
                border-radius: 20px;
                border: 1px solid rgba(64, 196, 99, 0.3);
                box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                margin-bottom: 20px;
            }}
            .confirm-label {{
                color: #888;
                font-size: 14px;
                margin-top: -10px;
            }}
            </style>
            <div class="confirm-container">
            <h3 style='margin:0;'>Confirm: {task['name']}</h3>
            <p class="confirm-label">Earning +{task['points']} XP for your pet's growth</p>
            </div>
        """, unsafe_allow_html=True)

        # Show detail input if needed
        task_detail = None


        if task["ask_detail"]:
            st.markdown("")
            task_detail = st.text_input(
                "Add context (optional):",
                placeholder=task["detail_prompt"],
                key="task_detail_input"
            )

        st.markdown("")
        col1, col2 = st.columns(2)

        with col1:
            if st.button("Confirm Activity", use_container_width=True, key="confirm_task_btn"):
                log_task(user, task, task_detail)

        with col2:
            if st.button("Change Mind", use_container_width=True, key="cancel_task_btn"):
                st.session_state.selected_task = None
                st.rerun()


# ----------------------------------------
# LOG TASK FUNCTION
# ----------------------------------------


def log_task(user: User, task: dict, task_detail: str):
    """
    Handles the full task logging flow using the OOP User.
    """
    # Save task log to DB
    add_task_log(
        user_id       = user.user_id,
        task_name     = task["name"],
        points_earned = task["points"],
        task_detail   = task_detail if task_detail else None
    )

    # All calculation logic is handled magically right here:
    evolved = user.log_task(task)

    # Save all updates to Supabase
    update_profile(user.user_id, user.to_dict())

    # Update local session state
    st.session_state.profile.update(user.to_dict())

    # Clear selected task
    st.session_state.selected_task = None

    # Check for new badges
    earned    = get_achievements(user.user_id)
    logs      = get_task_logs(user.user_id)
    new_badges = process_badges(
        user.user_id,
        st.session_state.profile,
        logs,
        earned
    )

    if new_badges:
        st.session_state.new_badges = new_badges
    
    # Show celebration or success
    if evolved:
        st.session_state.evolution_stage = evolved
        st.rerun()
    else:
        st.success(f"{task['name']} logged! +{task['points']} points earned!")
        st.rerun()