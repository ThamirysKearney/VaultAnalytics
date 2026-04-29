#  Enrolment Analytics Dashboard

> A Spec-Driven Development project for analysing course enrolment patterns  
> with a full PII encryption layer.

---

##  Project Summary

This project looks at enrolment data to figure out which courses are popular, who's signing up, and how people register. The goal is to help market the courses that don't have many students yet.

The problem: The raw data has personal info like email addresses, phone numbers, and names. I need to protect that before I can do any analysis.

What I did: I used two layers of security:

Some PII gets removed entirely (like names and dates of birth)

Other PII gets hashed with SHA-256 (like emails and phone numbers) - this is one-way, so it can't be reversed

I also added Fernet encryption as an option for cases where someone with permission might need to recover the original data later

All the analysis is done on the anonymised data, never the raw stuff.

---

##  Cybersecurity Layer

Since I´m studying for the **Google Cybersecurity Certificate**, I wan to practice the following skills:

| Skill | Implementation |
|---|---|
| PII identification | Columns audited and documented in the spec |
| One-way hashing | SHA-256 via `hashlib` for emails and phone numbers |
| Symmetric encryption | AES-128-CBC via `cryptography.fernet.Fernet` |
| Key management | Keys loaded from environment variables — never committed |
| Secure Git hygiene | `.gitignore` prevents raw PII files from ever being tracked |

---

##  Project Structure

```
enrolment-project/
├── app/
│   └── dashboard.py           # Streamlit analytics dashboard
├── data/
│   ├── raw/                    # Source files — gitignored
│   │   └── course_mapping.csv  # Safe reference data (no PII)
│   └── processed/              # Pipeline output — gitignored
├── specs/
│   ├── current/
│   │   └── enrolment_dashboard.md  # Master spec (SDD)
│   └── changes/
│       └── add_pipeline.md
├── src/
│   ├── data_cleaning.py        # Load, rename, parse, clean
│   ├── encryption.py           # Hashing + Fernet encryption
│   ├── feature_engineering.py  # Course codes, age groups, mapping
│   └── run_pipeline.py         # Pipeline orchestrator
├── Planning.md
├── README.md
└── requirements.txt
```

---

##  Getting Started

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add raw data

Place source CSV in `data/raw/`. It will be automatically gitignored.

### 3. Run the pipeline

```bash
python src/run_pipeline.py
```

This will:
- Clean and validate the raw data
- Hash all PII columns
- Engineer features (course codes, age groups, course metadata)
- Save the anonymised output to `data/processed/data.csv`

### 4. Launch the dashboard

```bash
streamlit run app/dashboard.py
```

---

##  Tech Stack

| Layer | Technology |
|---|---|
| Language | Python 3.10+ |
| Data processing | pandas 2.x |
| Encryption | cryptography (Fernet / SHA-256) |
| Dashboard | Streamlit |
| Charts | Plotly Express |
| Methodology | Spec-Driven Development |
| Version control | Git + GitHub |

---

##  Methodology: Spec-Driven Development

This project follows **Spec-Driven Development (SDD)**:

> The specification is written *before* any code. All implementation decisions must trace back to the spec. Changes go through a formal Change Proposal process.

The master spec lives at [`specs/current/enrolment_dashboard.md`](specs/current/enrolment_dashboard.md).

---

##  Dashboard Features

- **KPI strip** — Total enrolments, unique courses, average age, replacement rate
- **Enrolments by day of week** — identify peak registration days
- **Age group distribution** — understand student demographics per course
- **Replacement vs new** — track re-enrolment patterns
- **Enrolments per course** — spot low-popularity courses at a glance
- **Sidebar filters** — filter by course and age group

---

##  Data Privacy Statement

All personal data (names, email addresses, phone numbers) is either dropped or irreversibly hashed before any analysis is performed. The processed dataset contains no plain-text PII. Raw source files are excluded from version control via `.gitignore`.

---

##  Author

**Thamirys Kearney**  
Data Analytics | Cybersecurity (Google Certificate — in progress)  
[GitHub](https://github.com/ThamirysKearney)