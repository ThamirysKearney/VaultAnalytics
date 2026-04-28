# Enrollment Analytics Dashboard

A Spec-Driven Development project for analysing course enrollment patterns
with a full PII protection layer built for portfolio demonstration.

---

## Project Summary

This project analyses enrollment data to identify patterns in course popularity,
student demographics, and registration behaviour. The goal is to support
promotional decisions for low-attendance courses.

The raw dataset contains personally identifiable information — email addresses,
phone numbers, and names. Before any analysis takes place, this data is protected
using a two-layer security approach:

- Names and dates of birth are dropped entirely — they have no analytical value.
- Emails and phone numbers are irreversibly hashed using SHA-256.
- Fernet symmetric encryption is available for fields that may need to be
  recovered later by an authorised party.

All analysis is performed exclusively on the anonymised output.

---

## Cybersecurity Layer

Built while completing the Google Cybersecurity Certificate. Demonstrates the
following skills in practice:

| Skill                | Implementation                                            |
|----------------------|-----------------------------------------------------------|
| PII identification   | Columns audited and documented in the spec                |
| One-way hashing      | SHA-256 via hashlib for emails and phone numbers          |
| Symmetric encryption | AES-128-CBC via cryptography.fernet.Fernet                |
| Key management       | Keys loaded from environment variables, never committed   |
| Secure Git hygiene   | .gitignore prevents raw PII files from ever being tracked |

---

## Project Structure

enrollment-project/
├── app/
│   └── dashboard.py                  # Streamlit analytics dashboard
├── data/
│   ├── raw/                          # Source files, gitignored
│   │   └── course_mapping.csv        # Safe reference data, no PII
│   └── processed/                    # Pipeline output, gitignored
├── specs/
│   ├── current/
│   │   └── enrollment_dashboard.md   # Master spec (SDD)
│   └── changes/
│       └── add_pipeline.md
├── src/
│   ├── data_cleaning.py              # Load, rename, parse, clean
│   ├── encryption.py                 # Hashing and Fernet encryption
│   ├── feature_engineering.py        # Course codes, age groups, mapping
│   └── run_pipeline.py               # Pipeline orchestrator
├── Planning.md
├── README.md
└── requirements.txt

---

## Getting Started

### 1. Install dependencies

    pip install -r requirements.txt

### 2. Add raw data

Place your source CSV in data/raw/. It will be automatically gitignored.

### 3. Run the pipeline

    python src/run_pipeline.py

The pipeline will:

- Load and validate the raw data
- Drop PII columns (names, DOB)
- Hash remaining PII (emails, phone numbers)
- Remove test rows inserted during form testing
- Calculate age from date of birth
- Extract course codes and enrich with course metadata
- Save the anonymised output to data/processed/data.csv

### 4. Launch the dashboard

    python -m streamlit run app/dashboard.py

---

## Tech Stack

| Layer           | Technology                      |
|-----------------|---------------------------------|
| Language        | Python 3.10+                    |
| Data processing | pandas 2.x                      |
| Encryption      | cryptography (Fernet / SHA-256) |
| Dashboard       | Streamlit                       |
| Charts          | Plotly Express                  |
| Methodology     | Spec-Driven Development         |
| Version control | Git + GitHub                    |

---

## Methodology: Spec-Driven Development

This project follows Spec-Driven Development (SDD). The specification is written
before any code. All implementation decisions must trace back to the spec.
Changes go through a formal Change Proposal process documented in specs/changes/.

The master spec lives at specs/current/enrollment_dashboard.md.

---

## Dashboard Features

- KPI strip: total enrollments, unique courses, average age, replacement rate
- Enrollments by day of week: identify peak registration days
- Age distribution: understand student demographics
- Replacement vs new enrollment: SI = repeating student, NO = new student
- Enrollments per course: spot low-popularity courses at a glance
- Cascading sidebar filters: filter by programme (Ciudadania / Mayores), then by course name

---

## Data Privacy Statement

All personal data (names, email addresses, phone numbers) is either dropped or
irreversibly hashed before any analysis is performed. The processed dataset
contains no plain-text PII. Raw source files are excluded from version control
via .gitignore.

---

## Author

Thamirys Kearney
Data Analytics | Cybersecurity (Google Certificate — in progress)
https://github.com/ThamirysKearney
