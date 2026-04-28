"""
Streamlit dashboard for the Enrollment Analytics project.

Run from the project root:

    python -m streamlit run app/dashboard.py

Author: Thamirys Kearney
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------------
# PAGE CONFIG — must be the very first Streamlit call
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Enrollment Analytics",
    layout="wide",
)

# ------------------------------------------------------------------
# DATA LOAD
# ------------------------------------------------------------------
DATA_PATH = "data/processed/data.csv"
MAPPING_PATH = "data/raw/course_mapping.csv"


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Load processed enrollment data with Streamlit caching."""
    return pd.read_csv(path)


@st.cache_data
def load_mapping(path: str) -> pd.DataFrame:
    """Load course mapping reference data with Streamlit caching."""
    return pd.read_csv(path)


try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error(
        "Processed data not found. "
        "Please run `python src/run_pipeline.py` first."
    )
    st.stop()

try:
    mapping = load_mapping(MAPPING_PATH)
except FileNotFoundError:
    st.error(
        "Course mapping file not found at data/raw/course_mapping.csv."
    )
    st.stop()

# ------------------------------------------------------------------
# SIDEBAR — CASCADING FILTERS
# ------------------------------------------------------------------
st.sidebar.header("Filters")

# Step 1 — category filter (Ciudadania / Mayores)
all_categories = sorted(mapping["category"].dropna().unique())
selected_category = st.sidebar.selectbox(
    "Programme",
    options=["All"] + all_categories,
)

# Step 2 — filter mapping to selected category
if selected_category == "All":
    filtered_mapping = mapping
else:
    filtered_mapping = mapping[mapping["category"] == selected_category]

# Step 3 — build course options from filtered mapping using human-readable names
available_codes = filtered_mapping["course_code"].unique()
code_to_name = dict(zip(filtered_mapping["course_code"], filtered_mapping["course_name"]))

course_options = sorted(
    [code for code in available_codes if code in df["course_code"].values],
    key=lambda c: code_to_name.get(c, c),
)
course_display = [code_to_name.get(c, c) for c in course_options]

selected_display = st.sidebar.multiselect(
    "Course(s)",
    options=course_display,
    default=course_display,
)

# map selected display names back to codes
name_to_code = {v: k for k, v in code_to_name.items()}
selected_codes = [name_to_code.get(name, name) for name in selected_display]

# Step 4 — age group filter
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
df_filtered = df[df["course_code"].isin(selected_codes)]
if selected_age_groups:
    df_filtered = df_filtered[df_filtered["age_group"].isin(selected_age_groups)]

# ------------------------------------------------------------------
# TITLE
# ------------------------------------------------------------------
st.title("Enrollment Analytics Dashboard")
st.caption("Explore enrollment patterns, age demographics, and course popularity.")

# ------------------------------------------------------------------
# KPI METRICS
# ------------------------------------------------------------------
st.subheader("Key Metrics")

total_enrollments = len(df_filtered)
unique_courses = df_filtered["course_code"].nunique()
avg_age = (
    round(df_filtered["age"].mean(), 1)
    if "age" in df_filtered.columns and df_filtered["age"].notna().any()
    else "N/A"
)
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
    st.subheader("Enrollments by Day of Week")
    if "day_of_week" in df_filtered.columns:
        day_order = [
            "Monday", "Tuesday", "Wednesday",
            "Thursday", "Friday", "Saturday", "Sunday",
        ]
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
    st.subheader("Age Distribution")
    if "age" in df_filtered.columns and df_filtered["age"].notna().any():
        fig2 = px.histogram(
            df_filtered,
            x="age",
            nbins=20,
            color_discrete_sequence=["#F58518"],
            labels={"age": "Age", "count": "Students"},
        )
        fig2.update_layout(bargap=0.1)
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("No age data available.")

st.divider()

# ------------------------------------------------------------------
# ROW 2 — Replacement vs New  |  Enrollments by Course
# ------------------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("Replacement vs New Enrollment")
    st.caption("SI = student repeating a course. NO = new student.")
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
    st.subheader("Enrollments per Course")
    if not df_filtered.empty:
        course_counts = (
            df_filtered["course_code"]
            .value_counts()
            .reset_index()
        )
        course_counts.columns = ["course_code", "count"]
        course_counts["course_name"] = course_counts["course_code"].map(code_to_name)
        fig4 = px.bar(
            course_counts,
            x="course_name",
            y="count",
            color_discrete_sequence=["#72B7B2"],
            labels={"course_name": "Course", "count": "Enrollments"},
        )
        fig4.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No data available for selected filters.")

# ------------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------------
st.divider()
st.caption("All personal data has been anonymised before analysis.")