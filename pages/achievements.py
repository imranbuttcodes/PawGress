import streamlit as st
from database import get_achievements, award_badge, get_task_logs
from badges import BADGES, get_new_badges
from models.analytics import Analytics


# ─────────────────────────────────────────
# BADGE CATEGORIES
# ─────────────────────────────────────────

CATEGORIES = [
    {"key": "streak",  "label": "Streak",  "color": "amber"},
    {"key": "tasks",   "label": "Tasks",   "color": "purple"},
    {"key": "xp",      "label": "XP",      "color": "green"},
    {"key": "time",    "label": "Time",    "color": "blue"},
    {"key": "pet",     "label": "Pet",     "color": "teal"},
]

# Color maps for each category
COLOR_MAP = {
    "amber":  {"bg": "#FAEEDA", "border": "#EF9F27", "text": "#633806", "tier_bg": "#EF9F27", "tier_text": "#412402"},
    "purple": {"bg": "#EEEDFE", "border": "#7F77DD", "text": "#3C3489", "tier_bg": "#7F77DD", "tier_text": "#EEEDFE"},
    "green":  {"bg": "#EAF3DE", "border": "#639922", "text": "#27500A", "tier_bg": "#639922", "tier_text": "#EAF3DE"},
    "blue":   {"bg": "#E6F1FB", "border": "#378ADD", "text": "#0C447C", "tier_bg": "#378ADD", "tier_text": "#E6F1FB"},
    "teal":   {"bg": "#E1F5EE", "border": "#1D9E75", "text": "#085041", "tier_bg": "#1D9E75", "tier_text": "#E1F5EE"},
}


# ─────────────────────────────────────────
# CHECK AND AWARD NEW BADGES
# ─────────────────────────────────────────

def process_badges(user_id, profile, task_logs, earned):
    """
    Checks and awards any new badges user has earned.
    Returns list of newly awarded badge names.

    Args:
        user_id (str): User's ID
        profile (dict): User's profile
        task_logs (list): All task logs
        earned (list): Already earned achievements

    Returns:
        list: Newly awarded badge names
    """
    earned_keys = [a["badge_key"] for a in earned]
    new_badges  = get_new_badges(profile, task_logs, earned_keys)
    newly_awarded = []

    for badge in new_badges:
        awarded = award_badge(
            user_id,
            badge["key"],
            badge["name"],
            badge["icon"],
            badge["tier"]
        )
        if awarded:
            newly_awarded.append(badge["name"])

    return newly_awarded


# ─────────────────────────────────────────
# BADGE CARD HTML
# ─────────────────────────────────────────

def render_category(cat_badges, earned_keys, color, newly_awarded):
    """
    Renders all badges in a category as one HTML block
    """
    c = COLOR_MAP[color]
    
    cards_html = ""
    for badge in cat_badges:
        earned_data = earned_keys.get(badge["key"])
        is_earned   = earned_data is not None
        is_new      = badge["name"] in newly_awarded

        if is_earned:
            local_date, _ = Analytics.convert_to_local(earned_data["earned_at"])
            earned_date   = Analytics.format_date(local_date)
            tier          = earned_data["badge_tier"]
            new_pill    = f"<div style='position:absolute;top:-9px;left:50%;transform:translateX(-50%);font-size:10px;font-weight:500;padding:2px 10px;border-radius:20px;white-space:nowrap;background:#EEEDFE;color:#3C3489;border:0.5px solid #AFA9EC;'>New!</div>" if is_new else ""

            cards_html += (
                f"<div style='background:var(--background-color);border:1.5px solid {c['border']};"
                f"border-radius:12px;padding:16px 10px 14px;display:flex;flex-direction:column;"
                f"align-items:center;gap:6px;position:relative;min-height:150px;'>"
                f"{new_pill}"
                f"<div style='width:52px;height:52px;border-radius:50%;background:{c['bg']};"
                f"display:flex;align-items:center;justify-content:center;font-size:22px;"
                f"margin-bottom:2px;'>{badge['icon']}</div>"
                f"<div style='position:absolute;top:8px;right:8px;width:18px;height:18px;"
                f"border-radius:50%;background:{c['tier_bg']};display:flex;align-items:center;"
                f"justify-content:center;font-size:9px;font-weight:500;color:{c['tier_text']};'>"
                f"{tier}</div>"
                f"<span style='font-size:12px;font-weight:500;color:var(--text-color);"
                f"text-align:center;line-height:1.3;'>{badge['name']}</span>"
                f"<span style='font-size:11px;color:#888;text-align:center;line-height:1.3;'>"
                f"{badge['desc']}</span>"
                f"<span style='font-size:10px;color:{c['text']};text-align:center;margin-top:2px;'>"
                f"{earned_date}</span>"
                f"</div>"
            )
        else:
            cards_html += (
                f"<div style='background:var(--background-color);border:0.5px solid #e0e0e0;"
                f"border-radius:12px;padding:16px 10px 14px;display:flex;flex-direction:column;"
                f"align-items:center;gap:6px;opacity:0.38;min-height:150px;'>"
                f"<div style='width:52px;height:52px;border-radius:50%;background:{c['bg']};"
                f"display:flex;align-items:center;justify-content:center;font-size:22px;"
                f"margin-bottom:2px;'>{badge['icon']}</div>"
                f"<span style='font-size:12px;font-weight:500;color:var(--text-color);"
                f"text-align:center;line-height:1.3;'>{badge['name']}</span>"
                f"<span style='font-size:11px;color:#888;text-align:center;line-height:1.3;'>"
                f"{badge['desc']}</span>"
                f"</div>"
            )

    # Render ALL cards in ONE markdown call
    st.markdown(
        f"<div style='display:grid;grid-template-columns:repeat(4, 1fr);gap:10px;margin-bottom:1rem;'>"
        f"{cards_html}</div>",
        unsafe_allow_html=True
    )


# ─────────────────────────────────────────
# ACHIEVEMENTS SCREEN
# ─────────────────────────────────────────

def show_achievements():
    """
    Displays the achievements screen with all badges.
    Checks and awards new badges on load.
    """
    user_id = st.session_state.user_id
    profile = st.session_state.profile

    # ── Header ───────────────────────────
    st.markdown(
        "<h2 style='text-align:center'>🏆 Achievements</h2>",
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align:center; color:gray'>Earn badges by completing tasks and reaching milestones!</p>",
        unsafe_allow_html=True
    )
    

    # ── Load data ─────────────────────────
    with st.spinner("Loading achievements..."):
        earned      = get_achievements(user_id)
        task_logs   = get_task_logs(user_id)

    # ── Check + award new badges ──────────
    newly_awarded = process_badges(user_id, profile, task_logs, earned)

    # Reload after awarding
    if newly_awarded:
        earned = get_achievements(user_id)
        for name in newly_awarded:
            st.success(f"🎉 New badge unlocked: **{name}**!")

    # ── Overview ──────────────────────────
    total_badges  = len(BADGES)
    earned_count  = len(earned)
    progress_pct  = int((earned_count / total_badges) * 100)
    earned_keys   = {a["badge_key"]: a for a in earned}
    
    # --- Sleek Achievement Bar (Unified Design) -----------------
    bronze = sum(1 for a in earned if a["badge_tier"] == "B")
    silver = sum(1 for a in earned if a["badge_tier"] == "S")
    gold   = sum(1 for a in earned if a["badge_tier"] == "G")

    st.markdown(f"""
        <style>
        .stats-container {{
            display: flex;
            justify-content: space-around;
            align-items: center;
            gap: 15px;
            background: rgba(128, 128, 128, 0.05);
            padding: 25px 15px;
            border-radius: 20px;
            margin-bottom: 25px;
            border: 1px solid rgba(128, 128, 128, 0.1);
            backdrop-filter: blur(10px);
            flex-wrap: wrap;
        }}
        .stat-card {{
            text-align: center;
            flex: 1;
            min-width: 100px;
        }}
        .stat-value {{
            font-size: 24px;
            font-weight: 800;
            margin: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            color: var(--text-color);
        }}
        .stat-label {{
            font-size: 11px;
            color: var(--secondary-text-color);
            margin-top: 5px;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 600;
        }}
        </style>

        <div class="stats-container">
            <div class="stat-card">
                <p class="stat-value">🏆 {earned_count}/{total_badges}</p>
                <p class="stat-label">Earned</p>
            </div>
            <div class="stat-card">
                <p class="stat-value">📊 {progress_pct}%</p>
                <p class="stat-label">Progress</p>
            </div>
            <div class="stat-card">
                <p class="stat-value">🥇 {bronze}/{silver}/{gold}</p>
                <p class="stat-label">B / S / G</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Progress bar
    st.progress(progress_pct / 100)
    

    # ── Badges by category ────────────────
    for cat in CATEGORIES:
        c       = COLOR_MAP[cat["color"]]
        cat_badges = [
            b for b in BADGES.values()
            if b["category"] == cat["key"]
        ]
        cat_earned = sum(
            1 for b in cat_badges
            if b["key"] in earned_keys
        )

        # Category header
        st.markdown(
            f"<div style='display:flex; align-items:center; gap:8px; margin:1.5rem 0 0.75rem;'>"
            f"<div style='flex:1; height:0.5px; background:#e0e0e0;'></div>"
            f"<span style='font-size:11px; font-weight:500; letter-spacing:0.08em; "
            f"padding:3px 12px; border-radius:20px; background:{c['bg']}; color:{c['text']};'>"
            f"{cat['label'].upper()} — {cat_earned}/{len(cat_badges)}</span>"
            f"<div style='flex:1; height:0.5px; background:#e0e0e0;'></div>"
            f"</div>", 
            unsafe_allow_html=True
        )

        # Badge grid
        render_category(cat_badges, earned_keys, cat["color"], newly_awarded)

