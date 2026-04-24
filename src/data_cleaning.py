"""
Loads and cleans raw enrollment data exported from the registration form.

Responsibilities
----------------
- Load the raw CSV safely.
- Rename columns to a consistent snake_case schema.
- Drop columns that carry no analytical value.
- Parse and validate the timestamp column.
- Derive basic temporal features (hour, day_of_week).
- Return a clean DataFrame ready for feature engineering.

"""

import pandas as pd


# ---------------------------------------------------------------------------
# Schema definition — maps positional index to column name
# Columns prefixed "_drop_" are removed after renaming.
# ---------------------------------------------------------------------------

COLUMN_SCHEMA: dict[int, str] = {
    0:  "timestamp",
    1:  "teacher_email",
    2:  "_drop_empty",
    3:  "_drop_cargar",
    4:  "course_edition",
    5:  "_drop_first_name",
    6:  "_drop_first_name2",
    7:  "_drop_surname1",
    8:  "_drop_surname2",
    9:  "_drop_full_surname",
    10: "dob",
    11: "_drop_age_placeholder",
    12: "student_email",
    13: "phone",
    14: "replacement",
    15: "_drop_col15",
    16: "_drop_col16",
}

DROP_PREFIX = "_drop_"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_data(path: str, header_row: int = 0) -> pd.DataFrame:
    """Read a CSV or Excel file and return a raw DataFrame."""
    if path.endswith((".xlsx", ".xls")):
        df = pd.read_excel(path, header=header_row)
    else:
        df = pd.read_csv(path, header=header_row)
    print(f"[load_data] Loaded {len(df)} rows, {len(df.columns)} columns.")
    return df


def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Rename columns by positional index using COLUMN_SCHEMA."""
    expected = len(COLUMN_SCHEMA)
    actual = len(df.columns)

    if actual != expected:
        print(
            f"[WARNING] Expected {expected} columns, found {actual}. "
            "Review COLUMN_SCHEMA in data_cleaning.py."
        )

    rename_map = {
        df.columns[i]: name
        for i, name in COLUMN_SCHEMA.items()
        if i < actual
    }
    return df.rename(columns=rename_map)


def _drop_irrelevant_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Drop columns flagged with DROP_PREFIX and fully-empty columns."""
    drop_cols = [c for c in df.columns if c.startswith(DROP_PREFIX)]
    df = df.drop(columns=drop_cols, errors="ignore")
    df = df.dropna(axis=1, how="all")
    return df


def _parse_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """Parse the timestamp column to datetime (day-first format)."""
    if "timestamp" not in df.columns:
        print("[WARNING] 'timestamp' column not found — skipping date parsing.")
        return df

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        dayfirst=True,
        errors="coerce",
    )

    n_invalid = df["timestamp"].isna().sum()
    if n_invalid:
        print(f"[WARNING] {n_invalid} rows had an unparseable timestamp (set to NaT).")

    return df


def _derive_temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    """Extract hour and day-of-week from the parsed timestamp."""
    if "timestamp" not in df.columns:
        return df

    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.day_name()
    return df



def _remove_test_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Drop test rows inserted during form testing.

    Detects prueba entries by checking course_edition and student_email
    for the word prueba, and drops rows where phone is the placeholder 126.
    """
    mask = (
        df["course_edition"].astype(str).str.lower().str.contains("prueba", na=False)
        | df["student_email"].astype(str).str.lower().str.contains("prueba", na=False)
        | (df["phone"].astype(str).str.strip() == "126")
    )
    n_dropped = mask.sum()
    if n_dropped:
        print(f"[remove_test_rows] Dropped {n_dropped} test rows.")
    return df[~mask].reset_index(drop=True)


def _calculate_age(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate age in years from dob column where available.

    Replicates the SIFECHA(dob, HOY(), Y) formula from the source Google Sheet.
    Rows with missing or unparseable DOB get NaN for age.
    """
    if "dob" not in df.columns:
        print("[WARNING] dob column not found — skipping age calculation.")
        return df

    dob = pd.to_datetime(df["dob"], dayfirst=True, errors="coerce")
    today = pd.Timestamp.today()
    df["age"] = ((today - dob).dt.days // 365).where(dob.notna())
    valid = df["age"].notna().sum()
    print(f"[calculate_age] Age calculated for {valid} rows.")
    return df


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the full cleaning pipeline to a raw enrollment DataFrame.

    Steps
    -----
    1. Rename columns to schema.
    2. Drop irrelevant / PII columns.
    3. Parse timestamps.
    4. Derive temporal features.

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame from load_data().

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame.
    """
    df = df.iloc[1:].reset_index(drop=True)  # skip Column1/Column2 header row
    df = _rename_columns(df)
    df = _drop_irrelevant_columns(df)
    df = _remove_test_rows(df)
    df = _parse_timestamps(df)
    df = _calculate_age(df)
    df = _derive_temporal_features(df)

    print(f"[clean_data] Done. Shape after cleaning: {df.shape}")
    return df
