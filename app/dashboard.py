import streamlit as st
import pandas as pd
import plotly.express as px

df = pd.read_csv("data/processed/data.csv")

st.title("📊 Enrollment Dashboard")

# Filters
course = st.selectbox("Select Course", df["course_code"].unique())
df_filtered = df[df["course_code"] == course]

# Enrollment by day
fig = px.histogram(df_filtered, x="day_of_week")
st.plotly_chart(fig)

# Age distribution
fig2 = px.histogram(df_filtered, x="age_group")
st.plotly_chart(fig2)

# Replacement
fig3 = px.pie(df_filtered, names="replacement")
st.plotly_chart(fig3)