from google.ds_python_interpreter import HTML
import os

# Define the content of the markdown file
md_content = """# Student Enrollment Analysis & Data Privacy Project

## 1. New Project Direction (Clear + Strong)
### 🎯 New Goal
"Analyze student enrollment patterns while preserving sensitive data using anonymization and encryption techniques."

**This is:**
* ✅ **Realistic** with your data.
* ✅ **Strong** for data analyst roles.
* ✅ **Still valid** for a cybersecurity portfolio.

---

## 2. Dataset Capabilities
Let’s translate the raw columns into a usable schema:

| Raw Column | Meaning | Action |
| :--- | :--- | :--- |
| **Timestamp** | Enrollment date | ✅ Keep (Split into Date/Time) |
| **Email (x2)** | PII | 🔐 Hash |
| **Empty column** | Useless | ❌ Drop |
| **"cargar" column** | Useless | ❌ Drop |
| **Course edition code** | Course ID | ⚠️ Map to course name |
| **Name** | PII | ❌ Drop |
| **Surnames** | PII | ❌ Drop |
| **DOB** | Sensitive | ⚠️ Convert to Age / Drop |
| **Age** | Demographic | ✅ Keep |
| **Phone** | PII | 🔐 Hash |
| **Replacement (Sí/No)** | Behavior | ✅ Keep |

---

## 3. Security Layer
This dataset is ideal for demonstrating cybersecurity principles. 

**Your pipeline:** `Raw Data → Remove PII → Hash Identifiers → Clean → Analyze`

**Recruiter Value:**
* **Data Minimization:** Applying GDPR principles.
* **Pseudonymization:** Hashing emails and phone numbers.
* **Secure Processing:** Handling sensitive records correctly.

---

## 4. Key Insights to Extract
Since attendance data is missing, we focus on behavioral, demographic, and temporal data.

### 🔍 A. Enrollment Trends
* Enrollments per day/week/month.
* Peak registration times (hour of day).
* **Insight:** Identifying optimal times for user engagement.

### 👥 B. Demographics
* Age distribution across the student body.
* Age groups vs. course selection.
* **Insight:** Understanding which age groups prefer specific courses.

### 📚 C. Course Demand
* Most popular courses vs. least popular courses.
* **Insight:** Guiding marketing focus and resource allocation.

### 🔁 D. Replacement Behavior (High Value)
* Percentage of replacements vs. new enrollments.
* **Insight:** High replacement rates may indicate a potential dropout problem or course instability.

---

## 5. Constraints (What NOT to do)
To maintain professional credibility, avoid:
* Analyzing attendance.
* Explaining why people don't attend.
* Measuring drop-off after enrollment.

---

## 6. Analytics Questions (Phase 3)
1.  **Enrollment Behavior:** When do most users enroll? Are there peak days?
2.  **Course Popularity:** Which courses have the highest demand?
3.  **User Demographics:** Which age groups enroll the most?
4.  **Replacement Analysis:** What % of enrollments are replacements?
5.  **Operational Insight:** Are certain courses unstable?

---

## 7. Feature Engineering
We will derive new variables from existing data:
* **From Timestamp:** `enrollment_date`, `enrollment_hour`, `day_of_week`.
* **From Age:** `age_group` (e.g., 18–25, 26–35, 36–45, 46+).
* **From Course Code:** Mapping IDs (e.g., `C001`) to readable names (e.g., `Data Analytics`).

---

## 8. Dashboard Layout (Streamlit Idea)
* **Charts:** Enrollments over time, Course popularity, Age distribution, Replacement vs. New.
* **Filters:** Course Name, Age Group, Date Range.

---

## 9. Project Title Options
1.  **Secure Enrollment Analytics Dashboard**
2.  **Privacy-Preserving Student Enrollment Analysis**
3.  **Enrollment Intelligence with Data Anonymization**

---

## 10. OpenSpec Feature
> "Build an interactive dashboard to analyze student enrollment patterns while ensuring data privacy through anonymization and encryption."

---

## 11. Critical Data Cleaning (The "Real World" Story)
The project highlights your ability to handle messy data: