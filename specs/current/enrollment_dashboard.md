# Spec: Enrollment Analytics Dashboard 

## 1. Overview

This document is the **single source of truth** for the Enrollment Analytics Dashboard.  
All code, tests, and features must conform to the specifications defined here.  
Any change to the system behaviour must be proposed via a **Change Proposal** (see `specs/changes/`).

> This spec follows the **Spec-Driven Development** methodology, where the specification is written *before* the implementation. Code that conflicts with this spec is considered a bug.

---

## 2. Problem Statement

The company collects enrollment data that contains **personally identifiable information (PII)** — names, email addresses, and phone numbers.

This creates a conflict:

| Goal | Constraint |
|---|---|
| Analyse enrollment patterns and course popularity | Must not expose raw PII during analysis |
| Identify low-attendance courses and suggest promotions | Data must be safe to use in a development environment |
| Build a portfolio-worthy project | Must demonstrate cybersecurity best practices |

**Solution:** Implement a two-layer data protection strategy (hashing + optional symmetric encryption) *before* any analytics are performed.

---

## 3. Goals

- [x] **G1** — Protect PII before any data leaves the raw data folder.
- [x] **G2** — Produce a clean, anonymised dataset safe for analysis.
- [x] **G3** — Identify which courses have low enrollment.
- [x] **G4** — Analyse the age distribution of students per course.
- [x] **G5** — Detect enrollment patterns by day and hour.
- [ ] **G6** — Suggest promotional actions for low-popularity courses *(Phase 2)*.
- [ ] **G7** — Analyse and visualise attendance (vs enrollment) drop-off *(Phase 2)*.

---

## 4. Non-Goals (Out of Scope)

- Real-time data ingestion.
- User authentication on the dashboard.
- Sending promotional emails automatically.
- Mobile-native app.

---

## 5. Data Specification

### 5.1 Raw Data Schema

| Column Position | Raw Name | Mapped Name | Keep? | Reason |
|---|---|---|---|---|
| 0 | *(timestamp)* | `timestamp` | keep | Core analytical dimension |
| 1 | *(teacher email)* | `teacher_email` | keep (hashed) | Needed to identify course runs |
| 2 | *(empty)* | `_drop_empty` | drop | No analytical value |
| 3 | *(cargar)* | `_drop_cargar` | drop | System artefact |
| 4 | *(course edition)* | `course_edition` | keep | Base for `course_code` |
| 5 | *(name)* | `_drop_name` | drop | PII — not needed for analysis |
| 6 | *(first name)* | `_drop_first_name` | drop | PII |
| 7 | *(surname 1)* | `_drop_surname1` | drop | PII |
| 8 | *(surname 2)* | `_drop_surname2` | drop | PII |
| 9 | *(full surname)* | `_drop_full_surname` | drop | PII |
| 10 | *(date of birth)* | `dob` | drop | Age is derived; DOB itself is PII |
| 11 | *(age)* | `age` | keep | Demographic analysis |
| 12 | *(student email)* | `student_email` | keep (hashed) | Deduplication |
| 13 | *(phone)* | `phone` | keep (hashed) | Deduplication |
| 14 | *(replacement)* | `replacement` | keep | Replacement vs new metric |

### 5.2 Processed Data Schema

After the pipeline runs, `data/processed/data.csv` must contain:

| Column | Type | Description |
|---|---|---|
| `timestamp` | datetime | Parsed enrollment timestamp |
| `teacher_email` | str (SHA-256) | Hashed teacher identifier |
| `course_edition` | str | Full course edition string |
| `course_code` | str | First 4 segments of `course_edition` |
| `age` | int | Student age at enrollment |
| `age_group` | category | One of: 18-25, 26-35, 36-45, 46+ |
| `student_email` | str (SHA-256) | Hashed student identifier |
| `phone` | str (SHA-256) | Hashed phone number |
| `replacement` | str | "SI" or "NO" |
| `hour` | int | Hour extracted from timestamp |
| `day_of_week` | str | Day name extracted from timestamp |
| `course_name` | str | From course mapping CSV |
| `category` | str | From course mapping CSV |
| `theme` | str | From course mapping CSV |

---

## 6. Security Specification

### 6.1 PII Protection Strategy

| Data Type | Strategy | Reversible? | Justification |
|---|---|---|---|
| Email addresses | SHA-256 hash | No | Only needed for deduplication |
| Phone numbers | SHA-256 hash | No | Only needed for deduplication |
| Names / Surnames | **Dropped entirely** | N/A | No analytical use case |
| Date of birth | **Dropped** (age kept) | N/A | Age is sufficient; DOB is PII |

### 6.2 Key Management (Fernet — optional reversible encryption)

- Keys are **never** hard-coded or committed to version control.
- Keys are loaded from the `ENROLLMENT_FERNET_KEY` environment variable.
- If no key is set, the pipeline generates one and prints it — the operator must save it securely.

### 6.3 Git Data Rules

The following must **always** be present in `.gitignore`:

```
data/raw/*.csv
data/raw/*.xlsx
data/processed/
*.key
.env
```

`course_mapping.csv` is the **only** file in `data/raw/` that may be committed, because it contains no PII.

---

## 7. Pipeline Specification

The pipeline must execute in this exact order:

```
1. load_data()          → raw DataFrame
2. clean_data()         → renamed + deduplicated + parsed timestamps
3. anonymize_pii()      → PII columns replaced with SHA-256 hashes
4. extract_course_code() → course_code derived from course_edition
5. map_course_info()    → metadata joined from course_mapping.csv
6. create_age_groups()  → age_group column added
7. save to CSV          → data/processed/data.csv
```

**Rule:** Steps 3 (anonymise) must always run **before** steps 4–6 (feature engineering).  
Reason: feature engineering should never operate on plain-text PII.

---

## 8. Dashboard Specification

### 8.1 Required KPIs (always visible, unfiltered)

| KPI | Formula |
|---|---|
| Total Enrollments | `len(df_filtered)` |
| Unique Courses | `df_filtered["course_code"].nunique()` |
| Average Age | `df_filtered["age"].mean()` |
| Replacement Rate (%) | `(df_filtered["replacement"] == "SI").mean() * 100` |

### 8.2 Required Charts

| Chart | Type | Columns Used |
|---|---|---|
| Enrollments by Day of Week | Histogram | `day_of_week` |
| Age Group Distribution | Histogram | `age_group` |
| Replacement vs New | Pie chart | `replacement` |
| Enrollments per Course | Bar chart | `course_code` |

### 8.3 Filters (sidebar)

- Multi-select: Course(s)
- Multi-select: Age group(s)

### 8.4 Non-functional Requirements

- Charts must use `use_container_width=True`.
- `set_page_config()` must be the first Streamlit call.
- Data must be loaded with `@st.cache_data`.
- A footer note must confirm: *"All personal data has been anonymised before analysis."*

---

## 9. Tech Stack

| Layer | Technology | Version |
|---|---|---|
| Language | Python | 3.10+ |
| Data processing | pandas | 2.x |
| Encryption | cryptography (Fernet) | 41.x |
| Dashboard | Streamlit | 1.x |
| Charts | Plotly Express | 5.x |
| Version control | Git + GitHub | — |

---

## 10. Folder Structure

```
enrollment-project/
├── app/
│   └── dashboard.py          # Streamlit app
├── data/
│   ├── raw/                   # Source files — gitignored (except mapping)
│   │   └── course_mapping.csv # safe to commit — no PII
│   └── processed/             # Pipeline output — gitignored
│       └── data.csv
├── specs/
│   ├── current/
│   │   └── enrollment_dashboard.md  # ← this file
│   └── changes/
│       └── add_pipeline.md
├── src/
│   ├── data_cleaning.py
│   ├── encryption.py
│   ├── feature_engineering.py
│   └── run_pipeline.py
├── Planning.md
├── README.md
└── requirements.txt
```

---

## 11. Change Proposal Process

To change any behaviour described in this spec:

1. Create a new file in `specs/changes/` named `<feature_slug>.md`.
2. Fill in the Change Proposal template (see `specs/changes/add_pipeline.md`).
3. Get the proposal reviewed before implementing.
4. Update this spec document to reflect the accepted change.
5. Reference the change file in your commit message.

---

## 12. Out-of-scope / Future Phases

| Feature | Phase |
|---|---|
| Attendance drop-off analysis | Phase 2 |
| Promotional course suggestions (rule-based) | Phase 2 |
| Interactive Kanban board for action items | Phase 2 |
| Predictive attendance model | Phase 3 |