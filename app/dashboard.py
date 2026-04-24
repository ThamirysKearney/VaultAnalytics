"""
Streamlit dashboard for the Enrollment Analytics project.

Run from the project root::

    streamlit run app/dashboard.py

"""

import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------------
# PAGE CONFIG — must be the very first Streamlit call
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Enrollment Analytics",
    page_icon="📊",
    layout="wide",
)

# ------------------------------------------------------------------
# DATA LOAD
# ------------------------------------------------------------------
DATA_PATH = "data/processed/data.csv"


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Load processed data with Streamlit caching."""
    return pd.read_csv(path)


try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        "⚠️  Processed data not found. "
        "Please run `python src/run_pipeline.py` first."
    )
    st.stop()

# ------------------------------------------------------------------
# SIDEBAR — FILTERS
# ------------------------------------------------------------------
st.sidebar.header("🔎 Filters")

# Course filter
all_courses = sorted(df["course_code"].dropna().unique())
selected_courses = st.sidebar.multiselect(
    "Course(s)",
    options=all_courses,
    default=all_courses,
)

# Age group filter (if column exists)
if "age_group" in df.columns:
    all_age_groups = sorted(df["age_group"].dropna().unique())
    selected_age_groups = st.sidebar.multiselect(
        "Age group(s)",
        options=all_age_groups,
        default=all_age_groups,
    )
else:
    selected_age_groups = None

# Apply filters
df_filtered = df[df["course_code"].isin(selected_courses)]
if selected_age_groups is not None:
    df_filtered = df_filtered[df_filtered["age_group"].isin(selected_age_groups)]

# ------------------------------------------------------------------
# TITLE
# ------------------------------------------------------------------
st.title("📊 Enrollment Analytics Dashboard")
st.caption("Explore enrollment patterns, age demographics, and course popularity.")

# ------------------------------------------------------------------
# KPI METRICS
# ------------------------------------------------------------------
st.subheader("📌 Key Metrics")

total_enrollments = len(df_filtered)
unique_courses = df_filtered["course_code"].nunique()
avg_age = round(df_filtered["age"].mean(), 1) if "age" in df_filtered.columns else "N/A"
replacement_rate = (
    round((df_filtered["replacement"] == "SI").mean() * 100, 1)
    if "replacement" in df_filtered.columns
    else "N/A"
)

kpi1, kpi2, kpi3, kpi4 = st.columns(4)
kpi1.metric("Total Enrollments", total_enrollments)
kpi2.metric("Unique Courses", unique_courses)
kpi3.metric("Average Age", avg_age)
kpi4.metric("Replacement Rate (%)", replacement_rate)

st.divider()

# ------------------------------------------------------------------
# ROW 1 — Enrollments by day  |  Age distribution
# ------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Enrollments by Day of Week")
    if "day_of_week" in df_filtered.columns:
        day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        fig1 = px.histogram(
            df_filtered,
            x="day_of_week",
            category_orders={"day_of_week": day_order},
            color_discrete_sequence=["#4C78A8"],
            labels={"day_of_week": "Day", "count": "Enrollments"},
        )
        fig1.update_layout(bargap=0.2)
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.info("No day_of_week column found.")

with col2:
    st.subheader("👥 Age Group Distribution")
    if "age_group" in df_filtered.columns:
        fig2 = px.histogram(
            df_filtered,
            x="age_group",
            color_discrete_sequence=["#F58518"],
            labels={"age_group": "Age Group", "count": "Students"},
        )
        fig2.update_layout(bargap=0.2)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No age_group column found.")

st.divider()

# ------------------------------------------------------------------
# ROW 2 — Replacement vs New  |  Enrollments by Course
# ------------------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("🔁 Replacement vs New Enrollment")
    if "replacement" in df_filtered.columns:
        fig3 = px.pie(
            df_filtered,
            names="replacement",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("No replacement column found.")

with col4:
    st.subheader("📚 Enrollments per Course")
    course_counts = (
        df_filtered["course_code"]
        .value_counts()
        .reset_index()
        .rename(columns={"index": "course_code", "course_code": "count"})
    )
    fig4 = px.bar(
        course_counts,
        x="course_code",
        y="count",
        color_discrete_sequence=["#72B7B2"],
        labels={"course_code": "Course", "count": "Enrollments"},
    )
    fig4.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig4, use_container_width=True)

# ------------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------------
st.divider()
st.caption("🔒 All personal data has been anonymised before analysis.")