import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, date
import plotly.express as px

st.set_page_config(page_title="Gym Tracker", layout="wide")
st.title("🏋️ Gym Tracker")

# ---------- Data Persistence ----------
LOG_FILE = "workout_log.json"
SCHEDULE_FILE = "schedule.json"

def load_json(filepath):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return {}

def save_json(filepath, data):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

workout_log = load_json(LOG_FILE)   # { "2024-01-01": [ {exercise, sets, reps, weight}, ... ] }
schedule    = load_json(SCHEDULE_FILE)  # { "Monday": ["Squat", "Bench"], ... }

DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# ---------- Tabs ----------
tab1, tab2, tab3 = st.tabs(["📅 Today's Workout", "📝 Log Workout", "📈 Progress"])


# ══════════════════════════════════════════
# TAB 1 – Today's Workout (schedule viewer)
# ══════════════════════════════════════════
with tab1:
    st.header("Today's Workout")
    today_name = date.today().strftime("%A")
    st.subheader(f"Today is **{today_name}**")

    today_exercises = schedule.get(today_name, [])
    if today_exercises:
        st.success(f"You have {len(today_exercises)} exercise(s) scheduled today:")
        for i, ex in enumerate(today_exercises, 1):
            st.write(f"**{i}.** {ex}")
    else:
        st.info("No exercises scheduled for today. Set up your schedule below!")

    st.divider()
    st.subheader("⚙️ Edit Weekly Schedule")
    st.write("Enter comma-separated exercises for each day (e.g. `Squat, Bench Press, Deadlift`).")

    with st.form("schedule_form"):
        new_schedule = {}
        for day in DAYS:
            existing = ", ".join(schedule.get(day, []))
            val = st.text_input(day, value=existing, placeholder="Rest day")
            new_schedule[day] = [e.strip() for e in val.split(",") if e.strip()]

        if st.form_submit_button("💾 Save Schedule"):
            save_json(SCHEDULE_FILE, new_schedule)
            schedule.update(new_schedule)
            st.success("Schedule saved!")
            st.rerun()


# ══════════════════════════════════════════
# TAB 2 – Log a Workout
# ══════════════════════════════════════════
with tab2:
    st.header("Log a Workout")
    st.write("Record your sets, reps, and weight for any exercise.")

    with st.form("log_form"):
        col1, col2 = st.columns(2)

        with col1:
            log_date  = st.date_input("📆 Date", value=date.today())
            exercise  = st.text_input("🏋️ Exercise name", placeholder="e.g. Bench Press")
            sets      = st.number_input("Sets", min_value=1, max_value=20, value=3, step=1)

        with col2:
            reps      = st.number_input("Reps per set", min_value=1, max_value=100, value=10, step=1)
            weight    = st.number_input("Weight (lbs)", min_value=0.0, max_value=2000.0,
                                        value=135.0, step=2.5)
            notes     = st.text_area("Notes (optional)", placeholder="How did it feel?")

        submitted = st.form_submit_button("➕ Log Set")

    if submitted:
        if not exercise.strip():
            st.error("Please enter an exercise name.")
        else:
            date_key = str(log_date)
            entry = {
                "exercise": exercise.strip().title(),
                "sets": sets,
                "reps": reps,
                "weight": weight,
                "volume": sets * reps * weight,
                "notes": notes.strip(),
            }
            workout_log.setdefault(date_key, []).append(entry)
            save_json(LOG_FILE, workout_log)
            st.success(f"✅ Logged: **{entry['exercise']}** — {sets}×{reps} @ {weight} lbs")

    # Recent log preview
    st.divider()
    st.subheader("📋 Recent Entries")
    all_entries = [
        {"date": d, **e}
        for d, entries in workout_log.items()
        for e in entries
    ]
    if all_entries:
        df = pd.DataFrame(all_entries).sort_values("date", ascending=False)
        st.dataframe(df[["date", "exercise", "sets", "reps", "weight", "volume", "notes"]],
                     use_container_width=True, hide_index=True)
    else:
        st.info("No workouts logged yet.")


# ══════════════════════════════════════════
# TAB 3 – Progress Charts
# ══════════════════════════════════════════
with tab3:
    st.header("📈 Progress Over Time")

    all_entries = [
        {"date": d, **e}
        for d, entries in workout_log.items()
        for e in entries
    ]

    if not all_entries:
        st.info("Log some workouts first to see your progress here.")
    else:
        df = pd.DataFrame(all_entries)
        df["date"] = pd.to_datetime(df["date"])

        exercises_available = sorted(df["exercise"].unique())
        selected_exercise = st.selectbox("Select an exercise to chart", exercises_available)

        metric = st.radio("Metric to plot", ["weight", "volume", "reps"], horizontal=True,
                          help="Volume = sets × reps × weight")

        filtered = df[df["exercise"] == selected_exercise].sort_values("date")

        if filtered.empty:
            st.warning("No data for this exercise.")
        else:
            # Aggregate by date (max weight / total volume / avg reps per day)
            if metric == "volume":
                agg = filtered.groupby("date")["volume"].sum().reset_index()
                y_label = "Total Volume (lbs)"
            elif metric == "weight":
                agg = filtered.groupby("date")["weight"].max().reset_index()
                y_label = "Max Weight (lbs)"
            else:
                agg = filtered.groupby("date")["reps"].mean().reset_index()
                y_label = "Avg Reps"

            fig = px.line(
                agg, x="date", y=metric,
                title=f"{selected_exercise} — {y_label} Over Time",
                markers=True,
                labels={"date": "Date", metric: y_label},
            )
            fig.update_traces(line_color="#FF4B4B", marker=dict(size=8))
            fig.update_layout(hovermode="x unified")
            st.plotly_chart(fig, use_container_width=True)

            # Summary stats
            st.subheader("📊 Summary Stats")
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Sessions", filtered["date"].nunique())
            c2.metric("Max Weight",     f'{filtered["weight"].max():.1f} lbs')
            c3.metric("Best Volume",    f'{filtered["volume"].max():,.0f} lbs')
            c4.metric("Total Sets",     int(filtered["sets"].sum()))