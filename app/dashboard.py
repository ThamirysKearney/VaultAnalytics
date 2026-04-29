"""
Streamlit dashboard for the Enrolment Analytics project.

Run from the project root:

    python -m streamlit run app/dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px

# ------------------------------------------------------------------
# PAGE CONFIG — must be the very first Streamlit call
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Enrolment Analytics",
    layout="wide",
)

# ------------------------------------------------------------------
# DATA LOAD
# ------------------------------------------------------------------
DATA_PATH = "data/processed/data.csv"
MAPPING_PATH = "data/raw/course_mapping.csv"


@st.cache_data
def load_data(path: str) -> pd.DataFrame:
    """Load processed enrolment data with Streamlit caching."""
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
    st.error("Course mapping file not found at data/raw/course_mapping.csv.")
    st.stop()

# ------------------------------------------------------------------
# SIDEBAR — CASCADING FILTERS
# ------------------------------------------------------------------
st.sidebar.header("Filters")

all_categories = sorted(mapping["category"].dropna().unique())
selected_category = st.sidebar.selectbox(
    "Programme",
    options=["All"] + all_categories,
)

if selected_category == "All":
    filtered_mapping = mapping
else:
    filtered_mapping = mapping[mapping["category"] == selected_category]

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
    default=[],
)
if st.sidebar.checkbox("Select all courses", value=False):
    selected_display = course_display

name_to_code = {v: k for k, v in code_to_name.items()}
selected_codes = [name_to_code.get(name, name) for name in selected_display]

if "age_group" in df.columns:
    all_age_groups = sorted(df["age_group"].dropna().unique())
    selected_age_groups = st.sidebar.multiselect(
        "Age group(s)",
        options=all_age_groups,
        default=[],
    )
    if st.sidebar.checkbox("Select all age groups", value=False):
        selected_age_groups = all_age_groups
else:
    selected_age_groups = None

# apply filters — if no courses selected, show all
if selected_codes:
    df_filtered = df[df["course_code"].isin(selected_codes)]
else:
    df_filtered = df.copy()

if selected_age_groups:
    df_filtered = df_filtered[df_filtered["age_group"].isin(selected_age_groups)]

# build full code_to_name for charts (not just filtered)
full_code_to_name = dict(zip(mapping["course_code"], mapping["course_name"]))

# ------------------------------------------------------------------
# TITLE
# ------------------------------------------------------------------
st.title("Enrolment Analytics Dashboard")
st.caption("Explore enrolment patterns, age demographics, and course popularity.")

# ------------------------------------------------------------------
# KPI METRICS
# ------------------------------------------------------------------
st.subheader("Key Metrics")

total_enrolments = len(df_filtered)
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
kpi1.metric("Total Enrolments", total_enrolments)
kpi2.metric("Unique Courses", unique_courses)
kpi3.metric("Average Age", avg_age)
kpi4.metric("Replacement Rate (%)", replacement_rate)

st.divider()

# ------------------------------------------------------------------
# ROW 1 — Enrolments by day  |  Age distribution
# ------------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Enrolments by Day of Week")
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
            labels={"day_of_week": "Day", "count": "Enrolments"},
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
# ROW 2 — Replacement vs New  |  Enrolments by Course
# ------------------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("Replacement vs New Enrolment")
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
    st.subheader("Enrolments per Course")
    if not df_filtered.empty:
        course_counts = (
            df_filtered["course_code"]
            .value_counts()
            .reset_index()
        )
        course_counts.columns = ["course_code", "count"]
        course_counts["course_name"] = course_counts["course_code"].map(full_code_to_name)
        fig4 = px.bar(
            course_counts,
            x="course_name",
            y="count",
            color_discrete_sequence=["#72B7B2"],
            labels={"course_name": "Course", "count": "Enrolments"},
        )
        fig4.update_layout(xaxis_tickangle=-45)
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.info("No data available for selected filters.")

st.divider()

# ------------------------------------------------------------------
# INSIGHTS SECTION
# ------------------------------------------------------------------
st.header("Insights")
st.caption(
    "Analysis of enrolment patterns to support course promotion decisions. "
    "All insights are calculated from anonymised data."
)

# -- Insight 1: Course popularity ranking --
st.subheader("Course Popularity Ranking")

popularity = (
    df_filtered["course_code"]
    .value_counts()
    .reset_index()
)
popularity.columns = ["course_code", "enrolments"]
popularity["course_name"] = popularity["course_code"].map(full_code_to_name)
popularity["category"] = popularity["course_code"].map(
    dict(zip(mapping["course_code"], mapping["category"]))
)
popularity = popularity.sort_values("enrolments", ascending=False)

fig5 = px.bar(
    popularity,
    x="course_name",
    y="enrolments",
    color="category",
    color_discrete_map={"Ciudadania": "#4C78A8", "Mayores": "#F58518"},
    labels={"course_name": "Course", "enrolments": "Enrolments", "category": "Programme"},
    title="Enrolments per Course — sorted by popularity",
)
fig5.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig5, use_container_width=True)

# -- Insight 2: Low-enrolment courses --
st.subheader("Low-Enrolment Courses")
st.caption(
    "Courses in the bottom 20% by enrolment count. "
    "These are candidates for promotional action."
)

threshold = popularity["enrolments"].quantile(0.20)
low_enrolment = popularity[popularity["enrolments"] <= threshold].copy()

if low_enrolment.empty:
    st.info("No low-enrolment courses found for the current filter selection.")
else:
    st.dataframe(
        low_enrolment[["course_name", "category", "enrolments"]]
        .rename(columns={
            "course_name": "Course",
            "category": "Programme",
            "enrolments": "Enrolments",
        })
        .reset_index(drop=True),
        use_container_width=True,
    )
    st.caption(
        f"Threshold: courses with {int(threshold)} enrolments or fewer "
        f"({len(low_enrolment)} courses flagged)."
    )

st.divider()

# -- Insight 3: Replacement rate by course --
st.subheader("Replacement Rate by Course")
st.caption("Courses with high replacement rates may indicate repeated demand or unmet need.")

if "replacement" in df_filtered.columns:
    replacement_by_course = (
        df_filtered.groupby("course_code")["replacement"]
        .apply(lambda x: round((x == "SI").mean() * 100, 1))
        .reset_index()
    )
    replacement_by_course.columns = ["course_code", "replacement_rate"]
    replacement_by_course["course_name"] = replacement_by_course["course_code"].map(
        full_code_to_name
    )
    replacement_by_course = replacement_by_course.sort_values(
        "replacement_rate", ascending=False
    )

    fig6 = px.bar(
        replacement_by_course,
        x="course_name",
        y="replacement_rate",
        color_discrete_sequence=["#72B7B2"],
        labels={
            "course_name": "Course",
            "replacement_rate": "Replacement Rate (%)",
        },
    )
    fig6.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig6, use_container_width=True)
else:
    st.info("No replacement column found.")

st.divider()

# -- Insight 4: Age distribution by programme --
st.subheader("Age Distribution by Programme")
st.caption("Compares the age profile of students between Ciudadania and Mayores programmes.")

if "age" in df_filtered.columns and "category" in df_filtered.columns:
    age_data = df_filtered[df_filtered["age"].notna()].copy()
    if not age_data.empty:
        fig7 = px.histogram(
            age_data,
            x="age",
            color="category",
            nbins=20,
            barmode="overlay",
            opacity=0.7,
            color_discrete_map={"Ciudadania": "#4C78A8", "Mayores": "#F58518"},
            labels={"age": "Age", "count": "Students", "category": "Programme"},
        )
        fig7.update_layout(bargap=0.1)
        st.plotly_chart(fig7, use_container_width=True)
    else:
        st.info("No valid age data available for the current filter selection.")
else:
    st.info("Age or category column not found.")

# ------------------------------------------------------------------
# FOOTER
# ------------------------------------------------------------------
st.divider()
st.caption("All personal data has been anonymised before analysis.")