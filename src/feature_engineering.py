"""
Derives analytical features from cleaned enrolment data.

Responsibilities
----------------
- Extract a stable course code from the verbose course_edition string.
- Enrich the DataFrame by merging the external course mapping CSV.
- Create age-group bands for demographic analysis.

"""

import pandas as pd


# ---------------------------------------------------------------------------
# Course code extraction
# ---------------------------------------------------------------------------
 
def extract_course_code(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract a stable base course code from the full course edition string.
 
    The raw ``course_edition`` field follows this naming convention::
 
        240534_L4_T2_COCOIA_0076_15122025_LR
        └─── base code ────┘ └── edition metadata ──┘
 
    We keep only the first 4 underscore-separated segments.
 
    Null-safe: rows with NaN in course_edition produce NaN in course_code.
 
    Parameters
    ----------
    df : pd.DataFrame
        Cleaned DataFrame containing a ``course_edition`` column.
 
    Returns
    -------
    pd.DataFrame
        Same DataFrame with a new ``course_code`` column added.
 
    Example
    -------
    >>> extract_course_code(pd.DataFrame({"course_edition": ["240534_L4_T2_COCOIA_0076"]}))
       course_edition             course_code
    0  240534_L4_T2_COCOIA_0076   240534_L4_T2_COCOIA
    """
    if "course_edition" not in df.columns:
        raise KeyError("'course_edition' column not found. Check the cleaning step.")
 
    def _extract(val):
        if pd.isna(val):
            return None
        return "_".join(str(val).split("_")[:4])
 
    df["course_code"] = df["course_edition"].apply(_extract)
    return df
 
 
# ---------------------------------------------------------------------------
# Course mapping enrichment
# ---------------------------------------------------------------------------
 
def map_course_info(df: pd.DataFrame, mapping_path: str) -> pd.DataFrame:
    """
    Enrich the DataFrame with course metadata from an external CSV.
 
    The mapping CSV must contain at least a ``course_code`` column.
    Expected additional columns: ``course_name``, ``category``, ``theme``.
 
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with a ``course_code`` column
        (created by :func:`extract_course_code`).
    mapping_path : str
        Path to ``course_mapping.csv``.
 
    Returns
    -------
    pd.DataFrame
        DataFrame with course metadata columns added via a left join.
        Rows with unmatched course codes keep NaN for metadata columns.
    """
    mapping_df = pd.read_csv(mapping_path)
 
    if "course_code" not in mapping_df.columns:
        raise ValueError(
            f"Mapping file '{mapping_path}' has no 'course_code' column."
        )
 
    df = df.merge(mapping_df, on="course_code", how="left")
 
    unmatched = df["course_code"].isna().sum() if "course_name" in df.columns \
        else df[mapping_df.columns[1]].isna().sum()
    if unmatched:
        print(f"[map_course_info] {unmatched} rows had no mapping match.")
 
    return df
 
 
# ---------------------------------------------------------------------------
# Age-group segmentation
# ---------------------------------------------------------------------------
 
# Bin edges and their human-readable labels.
AGE_BINS   = [0, 25, 35, 45, 100]
AGE_LABELS = ["18-25", "26-35", "36-45", "46+"]
 
 
def create_age_groups(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add an ``age_group`` column that segments students into bands.
 
    Bands
    -----
    - 18-25
    - 26-35
    - 36-45
    - 46+
 
    Skips gracefully if the ``age`` column is missing, printing a warning
    instead of raising an exception — so the rest of the pipeline continues.
 
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing an ``age`` column (numeric).
 
    Returns
    -------
    pd.DataFrame
        Same DataFrame with ``age_group`` (Categorical) column added.
    """
    if "age" not in df.columns:
        print("[WARNING] 'age' column not found — skipping age groups.")
        return df
 
    df["age_group"] = pd.cut(
        pd.to_numeric(df["age"], errors="coerce"),
        bins=AGE_BINS,
        labels=AGE_LABELS,
        right=True,
    )
    return df

# ---------------------------------------------------------------------------
# Age group mapping from raw source labels
# ---------------------------------------------------------------------------

# Maps the Spanish age labels from the source form to our standard bands.
AGE_LABEL_MAP = {
    'Mayores menor a 60': '46-60',
    'Mayores mayor a 60': '60+',
}


def map_age_groups(df: pd.DataFrame) -> pd.DataFrame:
    """Map raw Spanish age labels to standard age band strings.

    Skips gracefully if age_group_raw column is missing.
    """
    if 'age_group_raw' not in df.columns:
        print("[WARNING] 'age_group_raw' column not found — skipping age mapping.")
        return df

    df['age_group'] = df['age_group_raw'].map(AGE_LABEL_MAP)
    unmapped = df['age_group'].isna().sum()
    if unmapped:
        print(f"[WARNING] {unmapped} rows had unrecognised age labels.")
    return df
