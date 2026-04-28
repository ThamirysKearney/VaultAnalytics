# Enrollment Analytics Project — Planning

## Goal

Analyse student enrollment patterns while protecting sensitive personal data
using anonymisation and encryption techniques.

---

## Security Focus

- Remove PII columns: names, surnames, date of birth
- Hash PII that has analytical value: emails, phone numbers
- Calculate age from DOB before dropping DOB
- Never commit raw data files to version control

---

## Analytics Focus

- Enrollment trends over time and by day of week
- Course popularity by programme (Ciudadania / Mayores)
- Age distribution of students
- Replacement vs new enrollment rates
- Identify low-attendance courses for promotional decisions

---

## Why This Project

Demonstrates practical skills in:

- Data cleaning of messy, real-world form exports
- Privacy-preserving analytics following GDPR-inspired principles
- Feature engineering from raw identifiers
- Interactive dashboard creation with Streamlit
- Spec-Driven Development methodology
- Cybersecurity practices applied to a real dataset