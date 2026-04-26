import streamlit as st
import plotly.graph_objects as go
from datetime import date
from fpdf import FPDF
import calplot
import pandas as pd


from database import get_task_logs
from models.user import User
from models.analytics import Analytics
from config import (
    APP_NAME, APP_VERSION,
    MAX_RECENT_LOGS,
    APP_LOGO
)


# ----------------------------------------
# ACTIVITY GRAPH
# ----------------------------------------


def build_activity_graph(task_logs):
    """
    Builds a GitHub-style calendar heatmap using calplot.
    Shows task activity for all time.

    Args:
        task_logs (list): List of task log dicts

    Returns:
        matplotlib.figure.Figure: Calendar heatmap figure
    """


    #  Use your existing function to get a clean dictionary like {"2026-03-19": 2}
    logs_dict = Analytics.group_logs_by_date(task_logs)

    if not logs_dict:
        return None
    
    #  Convert that dictionary straight to a Pandas Series
    events = pd.Series(logs_dict)
    
    #  Tell Pandas that the index (the keys) are actual dates
    events.index = pd.to_datetime(events.index)
    
    #  Draw the GitHub calendar!
    fig, ax = calplot.calplot(
        events,
        cmap='YlGn',                         # Authentic GitHub Yellow-to-Green gradient
        linewidth=1.5,                       # Slightly thicker borders around the squares
        linecolor='white',                   # Clean white spacing
        edgecolor='gray',                    # Gives depth to the squares
        suptitle='Your PawGress Tracking History' # Professional chart title
    )
    
    
    return fig


# ----------------------------------------
# POINTS HISTORY CHART
# ----------------------------------------

def build_points_chart(task_logs):
    """
    Builds a line chart showing points earned per day over time.

    Args:
        task_logs (list): List of task log dicts

    Returns:
        plotly.graph_objects.Figure: Line chart figure
    """
    points_by_date = Analytics.get_points_by_date(task_logs)

    if not points_by_date:
        return None

    # Sort by date
    sorted_dates = sorted(points_by_date.keys())
    sorted_points = [points_by_date[d] for d in sorted_dates]

    fig = go.Figure(data=go.Scatter(
        x=sorted_dates,
        y=sorted_points,
        mode="lines+markers",
        line=dict(color="#40c463", width=2),
        marker=dict(color="#216e39", size=6),
        fill="tozeroy",
        fillcolor="rgba(64, 196, 99, 0.1)",
    ))

    fig.update_layout(
        xaxis=dict(showgrid=False, title="Date"),
        yaxis=dict(showgrid=True, title="Points Earned"),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=10, t=10, b=40),
        height=250,
    )

    return fig


# ----------------------------------------
# TASK BREAKDOWN CHART
# ----------------------------------------

def build_task_breakdown_chart(task_logs):
    """
    Builds a horizontal bar chart showing task completion counts.

    Args:
        task_logs (list): List of task log dicts

    Returns:
        plotly.graph_objects.Figure: Bar chart figure
    """
    task_counts = Analytics.get_task_count_by_type(task_logs)

    if not task_counts:
        return None

    # Sort by count
    sorted_tasks = sorted(task_counts.items(), key=lambda x: x[1], reverse=True)
    tasks = [t[0] for t in sorted_tasks]
    counts = [t[1] for t in sorted_tasks]

    fig = go.Figure(data=go.Bar(
        x=counts,
        y=tasks,
        orientation="h",
        marker=dict(
            color=counts,
            colorscale="Greens",
            showscale=False
        ),
    ))

    fig.update_layout(
        xaxis=dict(showgrid=True, title="Times Completed"),
        yaxis=dict(showgrid=False),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=150, r=10, t=10, b=40),
        height=250,
    )

    return fig


# ----------------------------------------
# PDF REPORT GENERATOR
# ----------------------------------------

def generate_pdf_report(profile, task_logs):
    """
    Generates a downloadable PDF productivity report.

    Args:
        profile (dict): User's full profile dict
        task_logs (list): List of task log dicts

    Returns:
        bytes: PDF file as bytes for download
    """
    pdf = FPDF()
    pdf.add_page()

    try:
        # Center the logo
        logo_width = 25  # mm
        page_width = 210  # A4 width in mm
        x_position = (page_width - logo_width) / 2  # center calculation
        pdf.image(APP_LOGO, x=x_position, y=10, w=logo_width)
        pdf.ln(25)  # space after logo
    except:
        pdf.ln(3)  # fallback if logo not found

    # ── Header ───────────────────────────
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(26, 26, 46)
    pdf.cell(0, 15, f"{APP_NAME} - Productivity Report", ln=1, align="C")

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(100, 100, 100)
    today_format = Analytics.get_local_today_date().strftime('%B %d, %Y')
    pdf.cell(0, 7, f"Generated: {today_format}", ln=1, align="C")
    pdf.cell(0, 7, f"Version: {APP_VERSION}", ln=1, align="C")
    pdf.ln(3)

    # ── Divider ──────────────────────────
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    # ── Pet Status ───────────────────────
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(26, 26, 46)
    pdf.cell(0, 10, "Pet Status", ln=1)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(50, 50, 50)

    user = User(profile)
    stage = user.pet.current_stage
    mood = user.pet.mood
    full_name = profile.get("full_name", "N/A")
    pdf.cell(0, 7, f"Full Name:      {full_name}", ln=1)
    pdf.cell(0, 7, f"Username:      {profile['username']}", ln=1)
    pdf.cell(0, 7, f"Pet Stage:     {stage['name']}", ln=1)
    pdf.cell(0, 7, f"Pet Mood:      {mood['mood']}", ln=1)
    pdf.cell(0, 7, f"Total XP:  {profile['total_points']} pts", ln=1)
    pdf.cell(0, 7, f"Available Coins:{profile.get('available_points', 0)}", ln=1)
    pdf.cell(0, 7, f"Hunger Level:  {profile['hunger_level']}/100", ln=1)
    pdf.cell(0, 7, f"Happiness:     {profile['happiness_level']}/100", ln=1)
    pdf.cell(0, 7, f"Streak:        {profile['current_streak']} days", ln=1)
    pdf.ln(3)

    # ── Task Summary ─────────────────────
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(5)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(26, 26, 46)
    pdf.cell(0, 10, "Task Summary", ln=1)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)

    total_tasks = len(task_logs)
    total_pts_from_logs = sum(log["points_earned"] for log in task_logs)
    most_completed = Analytics.get_most_completed_task(task_logs)
    task_counts = Analytics.get_task_count_by_type(task_logs)

    pdf.cell(0, 7, f"Total Tasks Completed: {total_tasks}", ln=1)
    pdf.cell(0, 7, f"Total Points Earned:   {total_pts_from_logs} pts", ln=1)
    pdf.cell(0, 7, f"Most Completed Task:   {most_completed or 'None yet'}", ln=1)
    pdf.ln(3)

    # Task breakdown
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(0, 7, "Task Breakdown:", ln=1)
    pdf.set_font("Helvetica", "", 10)

    for task_name, count in sorted(task_counts.items(), key=lambda x: x[1], reverse=True):
        pdf.cell(0, 7, f"  {task_name}: {count} time{'s' if count != 1 else ''}", ln=1)

    pdf.ln(3)

    # ── Recent Activity ───────────────────
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(8)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(26, 26, 46)
    pdf.cell(0, 10, f"Recent Activity (Last {MAX_RECENT_LOGS} Tasks)", ln=1)

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(50, 50, 50)

    recent_logs = task_logs[:MAX_RECENT_LOGS]

    for log in recent_logs:
        local_date, _ = Analytics.convert_to_local(log["completed_at"])
        date_str = Analytics.format_date(local_date)
        detail   = f" - {log['task_detail']}" if log.get("task_detail") else ""
        line     = f"{log['task_name']}{detail} | +{log['points_earned']}pts | {date_str}"
        pdf.cell(0, 7, line, ln=1)

    pdf.ln(5)

    # ── Footer ────────────────────────────
    pdf.set_draw_color(200, 200, 200)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(3)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(150, 150, 150)
    pdf.cell(0, 8, f"{APP_NAME} v{APP_VERSION} - Stay productive. Keep your pet happy.", ln=1, align="C")

    # Return as bytes
    return bytes(pdf.output())


# ----------------------------------------
# STATS SCREEN
# ----------------------------------------

def show_stats():
    """
    Displays the full stats screen including:
    - Overview metrics
    - GitHub-style activity graph
    - Points history line chart
    - Task breakdown bar chart
    - Most completed task
    - Recent activity log
    - Download PDF report button
    """
    profile  = st.session_state.profile
    user_id  = st.session_state.user_id

    # ── Header ───────────────────────────
    st.markdown("<h2 style='text-align:center'>Your Productivity Stats</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center; color:gray'>Productivity and Contribution Metrics</p>", unsafe_allow_html=True)
    st.markdown("")

    # ── Load Task Logs ───────────────────
    with st.spinner("Loading your stats..."):
        task_logs = get_task_logs(user_id)

    # ── Overview Metrics ─────────────────
    total_tasks      = len(task_logs)
    total_pts        = profile["total_points"]
    available_pts    = profile.get("available_points", 0)
    current_streak   = profile["current_streak"]
    most_completed   = Analytics.get_most_completed_task(task_logs)

    user = User(profile)
    stage_name = user.pet.current_stage["name"]

    st.markdown(f"""
    <style>
    .stats-container {{
        display: flex;
        justify-content: space-around;
        align-items: center;
        gap: 10px;
        background: rgba(128, 128, 128, 0.05);
        padding: 25px 15px;
        border-radius: 20px;
        margin-bottom: 35px;
        border: 1px solid rgba(128, 128, 128, 0.1);
        backdrop-filter: blur(10px);
        flex-wrap: wrap;
    }}

    .stat-card {{
        text-align: center;
        flex: 1;
        min-width: 120px;
    }}

    .stat-value {{
        font-size: 24px;
        font-weight: 800;
        margin: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
    }}

    .stat-label {{
        font-size: 11px;
        color: #888;
        margin-top: 5px;
        text-transform: uppercase;
        letter-spacing: 1.5px;
        font-weight: 600;
    }}
    </style>

    <div class="stats-container">
        <div class="stat-card">
            <p class="stat-value">⭐ {total_pts}</p>
            <p class="stat-label">XP</p>
        </div>
        <div class="stat-card">
            <p class="stat-value">🪙 {available_pts}</p>
            <p class="stat-label">Coins</p>
        </div>
        <div class="stat-card">
            <p class="stat-value">✅ {total_tasks}</p>
            <p class="stat-label">Tasks</p>
        </div>
        <div class="stat-card">
            <p class="stat-value">🔥 {current_streak} days</p>
            <p class="stat-label">Streak</p>
        </div>
        <div class="stat-card">
            <p class="stat-value">🐾 {stage_name}</p>
            <p class="stat-label">Stage</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Activity Graph ───────────────────
    st.markdown("### Activity Graph")
    st.markdown(f"<span style='color:gray; font-size:14px'>Your complete productivity history</span>", unsafe_allow_html=True)

    if task_logs:
        fig = build_activity_graph(task_logs)
        if fig:
            st.pyplot(fig)
        else:
            st.info("No activity yet!")
    else:
        st.info("No activity yet - log your first task to see the graph!")

    st.markdown("")

    # ── Points History ───────────────────
    st.markdown("### Points History")

    if task_logs:
        fig = build_points_chart(task_logs)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No points history yet - start logging tasks!")

    st.markdown("")

    # ── Task Breakdown ───────────────────
    st.markdown("### Task Breakdown")

    if most_completed:
        st.markdown(f"**Your strongest habit:** {most_completed} 💪")

    if task_logs:
        fig = build_task_breakdown_chart(task_logs)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No tasks logged yet!")

    st.markdown("")

    # ── Recent Activity ──────────────────
    st.markdown("### Recent Activity")

    if task_logs:
        recent = task_logs[:MAX_RECENT_LOGS]
        for log in recent:
            col1, col2 = st.columns([3, 1])
            with col1:
                detail = f" - *{log['task_detail']}*" if log.get("task_detail") else ""
                local_date, _ = Analytics.convert_to_local(log["completed_at"])
                date_str = Analytics.format_date(local_date)
                st.markdown(f"**{log['task_name']}**{detail}")
                st.markdown(f"<p style='color:gray; font-size:12px'>{date_str}</p>", unsafe_allow_html=True)
            with col2:
                st.markdown(f"<p style='color:green; font-weight:bold; text-align:right'>+{log['points_earned']} pts</p>", unsafe_allow_html=True)
            st.divider()
    else:
        st.info("No tasks logged yet - go log your first task!")

    # ------ Download Report --------------------
    st.markdown("### Download Report")
    st.markdown("<span style='color:gray; font-size:14px'>Download your full productivity report as a PDF</span>", unsafe_allow_html=True)

    if st.button("Generate PDF Report", use_container_width=True, key="download_report_btn"):
        with st.spinner("Generating your report..."):
            pdf_bytes = generate_pdf_report(profile, task_logs)

        st.download_button(
            label="⬇️ Download PDF Report",
            data=pdf_bytes,
            file_name=f"pawgress_report_{Analytics.get_local_today_str().replace('-', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            key="download_pdf_btn"
        )
        st.success("Report ready! Click above to download 🎉")