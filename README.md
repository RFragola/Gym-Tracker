# Gym Tracker

Gym Tracker is a simple, easy-to-use fitness tracker that tracks your progress in the gym over time.

---

## Current Features

### Weekly Schedule
- Set a custom exercise schedule for each day of the week
- App automatically detects today's day and displays your planned exercises
- Editable schedule form with persistent storage

### Workout Logging
- Log any exercise with individual reps and weight per set
- Dynamically add or remove sets before saving
- New sets auto-fill with the previous set's values for convenience
- Optional notes field per exercise
- Full workout history displayed in a sortable table

### Progress Charts
- Select any logged exercise to view its progress over time
- Switch between three metrics: max weight, total volume, or average reps
- Interactive line chart with hover details (powered by Plotly)
- Summary stats cards: total sessions, max weight, best volume, total sets

---

## Planned Features

### Calorie Tracker
- Log daily meal calorie counts
- Tracking over time to track bulking vs cutting
- Progress toward custom calorie goals

### Persistent Storage
- Migrate from local JSON files to better storage
- Data survives app restarts and is accessible across devices
- Unique (per-user) data storage

### Expanded Progress Stats
- Muscle group breakdown (e.g. push/pull/legs split analysis)
- Estimated 1-rep max calculator (using the Epley formula)
- Streak tracking — consecutive weeks hitting your scheduled workouts

---

## Tech Stack

- [Streamlit](https://streamlit.io/) — frontend & deployment
- [Pandas](https://pandas.pydata.org/) — data handling
- [Plotly](https://plotly.com/python/) — interactive charts
- Python `json` + local filesystem — current storage layer

---

## Running Locally

1. Clone the repo and navigate to the project folder
2. Install dependencies:
```bash
   pip install -r requirements.txt
```
3. Launch the app:
```bash
   streamlit run app.py
```