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
# Schema definition
# ---------------------------------------------------------------------------

# Map from positional index → desired column name.
# I can just adjust the ORDER here if the source CSV changes column positions.
COLUMN_SCHEMA: dict[int, str] = {
    0: "timestamp",
    1: "teacher_email",
    2: "_drop_empty",
    3: "_drop_cargar",
    4: "course_edition",
    5: "_drop_name",
    6: "_drop_first_name",
    7: "_drop_surname1",
    8: "_drop_surname2",
    9: "_drop_full_surname",
    10: "dob",
    11: "age",
    12: "student_email",
    13: "phone",
    14: "replacement",
}

# Columns whose names start with "_drop_" are removed after renaming.
DROP_PREFIX = "_drop_"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def load_data(path: str) -> pd.DataFrame:
    """
    Read a CSV file and return a raw DataFrame.

    Parameters
    ----------
    path : str
        Relative or absolute path to the CSV file.

    Returns
    -------
    pd.DataFrame

    Raises
    ------
    FileNotFoundError
        If the file does not exist at *path*.
    """
    df = pd.read_csv(path)
    print(f"[load_data] Loaded {len(df)} rows, {len(df.columns)} columns.")
    return df


def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Rename columns by positional index using COLUMN_SCHEMA.

    Columns not present in the schema keep their original name.
    An informative warning is printed if the column count does not match.
    """
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
    """Drop columns flagged with the DROP_PREFIX and fully-empty columns."""
    # Drop marked columns
    drop_cols = [c for c in df.columns if c.startswith(DROP_PREFIX)]
    df = df.drop(columns=drop_cols, errors="ignore")

    # Drop columns that are 100 % empty
    df = df.dropna(axis=1, how="all")

    return df


def _parse_timestamps(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parse the 'timestamp' column to datetime.

    The source data uses day-first format (DD/MM/YYYY).
    Invalid values become NaT (not silently discarded).
    """
    if "timestamp" not in df.columns:
        print("[WARNING] 'timestamp' column not found — skipping date parsing.")
        return df

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        dayfirst=True,
        errors="coerce",   # bad values → NaT instead of crashing
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


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply the full cleaning pipeline to a raw enrollment DataFrame.

    Steps
    -----
    1. Drop fully-empty columns and rename to schema.
    2. Remove irrelevant / PII columns not needed for analytics.
    3. Parse timestamps.
    4. Derive temporal features.

    Parameters
    ----------
    df : pd.DataFrame
        Raw DataFrame returned by :func:`load_data`.

    Returns
    -------
    pd.DataFrame
        Cleaned DataFrame.
    """
    df = _rename_columns(df)
    df = _drop_irrelevant_columns(df)
    df = _parse_timestamps(df)
    df = _derive_temporal_features(df)

    print(f"[clean_data] Done. Shape after cleaning: {df.shape}")
    return df