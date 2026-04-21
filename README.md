# 🔐 Secure Student Enrollment Analytics Dashboard

## 🎯 Objective
This project analyzes student enrollment patterns while preserving sensitive personal data using anonymization and encryption techniques.

---

## 🔐 Data Security Approach

### Data Minimization
Removed:
- Names
- Surnames
- Date of birth

### Pseudonymization
Applied SHA-256 hashing to:
- Student emails
- Teacher emails
- Phone numbers

### Encryption
- Dataset encrypted using Fernet symmetric encryption
- Encryption key stored separately

---

## 🧰 Tech Stack

- Python (pandas, hashlib, cryptography)
- Streamlit
- Plotly
- OpenSpec (Spec-Driven Development)

---

## 📊 Features

- Enrollment trends over time
- Course popularity analysis
- Age group segmentation
- Replacement vs new enrollment analysis

---

## 🧠 Key Insights (To be completed)

- Peak enrollment times
- Most popular courses
- Age-based preferences
- Courses with high replacement rates

---

## 📁 Project Structure
app/
data/
specs/
src/

---

## 🚀 How to Run

```bash
pip install -r requirements.txt
streamlit run app/dashboard.py