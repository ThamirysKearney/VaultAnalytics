import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
DATA_PATH = "data/processed/data.csv"

try:
    df = pd.read_csv(DATA_PATH)
except FileNotFoundError:
    st.error("Run the pipeline first.")
    st.stop()

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(layout="wide")

st.title("📊 Enrollment Analytics Dashboard")

# --------------------------------------------------
# KPI SECTION (🔥 VERY IMPORTANT)
# --------------------------------------------------
total_students = len(df)
unique_courses = df["course_code"].nunique()
avg_age = round(df["age"].mean(), 1)
replacement_rate = round((df["replacement"] == "SI").mean() * 100, 2)

col1, col2, col3, col4 = st.columns(4)

col1.metric("Total Enrollments", total_students)
col2.metric("Courses", unique_courses)
col3.metric("Average Age", avg_age)
col4.metric("Replacement Rate (%)", replacement_rate)

# --------------------------------------------------
# FILTERS
# --------------------------------------------------
st.sidebar.header("Filters")

selected_course = st.sidebar.selectbox(
    "Course",
    sorted(df["course_code"].dropna().unique())
)

df_filtered = df[df["course_code"] == selected_course]

# --------------------------------------------------
# CHARTS
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    st.subheader("📅 Enrollments by Day")
    fig1 = px.histogram(df_filtered, x="day_of_week")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("👥 Age Distribution")
    fig2 = px.histogram(df_filtered, x="age_group")
    st.plotly_chart(fig2, use_container_width=True)

# Full width
st.subheader("🔁 Replacement vs New")
fig3 = px.pie(df_filtered, names="replacement")
st.plotly_chart(fig3, use_container_width=True)