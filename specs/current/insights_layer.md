# Spec: Insights Layer
# Status: approved

# Goal: Identify enrolment patterns and low-performing courses to support
# promotional decisions, presented as a new insights section in the dashboard.

# Inputs:
#   - data/processed/data.csv (pipeline output)
#   - data/raw/course_mapping.csv (course metadata)

# Outputs:
#   - New insights section in app/dashboard.py with four analyses:
#     1. Course popularity ranking (enrolments per course, sorted descending)
#     2. Replacement rate by course (which courses have most repeat students)
#     3. Age distribution by programme (Ciudadania vs Mayores)
#     4. Low-enrolment course flagging (bottom 20% by enrolment count)

# Constraints:
#   - Filter out invalid ages (age < 0 or age > 100) before any age analysis
#   - No hardcoded thresholds — low-enrolment cutoff calculated dynamically
#   - All charts follow existing colour scheme (#4C78A8, #F58518, #72B7B2)
#   - No emojis anywhere
#   - Idempotent — running pipeline twice does not change output
