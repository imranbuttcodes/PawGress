import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
from database import get_task_logs
import pytz
from models.analytics import Analytics



def show_logbook():
    """
    Displays an interactive history logbook where users can search,
    sort, filter, and export their past logged tasks.
    """
    st.markdown("<h2 style='text-align:center'>Logbook</h2>", unsafe_allow_html=True)
    st.markdown("")

    user_id = st.session_state.user_id

    with st.spinner("Loading records..."):
        task_logs = get_task_logs(user_id)

    if not task_logs:
        st.info("No records found.")
        return

    # Extract all unique task types for the filter dropdown
    all_categories = sorted(list(set(log["task_name"] for log in task_logs)))
    all_categories.insert(0, "All")

    # ── Filters ──────────────────────────
    st.markdown("### Filters")
    with st.container(border = True):
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            search_query = st.text_input("Search", placeholder="Search task name or details...")
        with col2:
            category_filter = st.selectbox("Category", all_categories)
        with col3:
            time_filter = st.selectbox("Date Range", ["All Time", "Last 7 Days", "Last 30 Days", "This Year"])


    # ── Filtering Logic ──────────────────
    today = Analytics.get_local_today_date()
    cutoff_date = None

    if time_filter == "Last 7 Days":
        cutoff_date = today - timedelta(days=7)
    elif time_filter == "Last 30 Days":
        cutoff_date = today - timedelta(days=30)
    elif time_filter == "This Year":
        cutoff_date = today.replace(month=1, day=1)

    formatted_logs = []
    
    for log in task_logs:
        raw_date_str, time_str = Analytics.convert_to_local(log["completed_at"])
        try:
            log_date = datetime.strptime(raw_date_str, "%Y-%m-%d").date()
        except ValueError:
            continue

        #  Date filter
        if cutoff_date and log_date < cutoff_date:
            continue

        name = log["task_name"]
        detail = log.get("task_detail", "") or ""
        pts = log["points_earned"]

        #  Category filter
        if category_filter != "All" and name != category_filter:
            continue

        #  Text search filter
        if search_query:
            search_text = f"{name} {detail}".lower()
            if search_query.lower() not in search_text:
                continue
            
        formatted_logs.append({
            "Date": raw_date_str,
            "Time": time_str,
            "Task": name,
            "Details": detail,
            "XP": pts
        })

    # ── Display Table ────────────────────
    if not formatted_logs:
        st.warning("No records match the current filters.")
        return

    df = pd.DataFrame(formatted_logs)
    st.caption(f"Displaying {len(df)} records")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Date":    st.column_config.DateColumn("Date"),
            "Time":    st.column_config.TextColumn("Time"),
            "Task":    st.column_config.TextColumn("Task"),
            "Details": st.column_config.TextColumn("Details"),
            "XP":      st.column_config.NumberColumn("XP Earned", format="+%d"),
        }
    )

    st.markdown("")

    # ── Export ───────────────────────────
    st.markdown("### Export")
    
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    
    st.download_button(
        label="Download subset as CSV",
        data=csv_buffer.getvalue().encode("utf-8"),
        file_name=f"pawgress_logbook_{today.strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
