"""
Orchestrates the full data processing pipeline:

    Raw CSV  →  Clean  →  Anonymise PII  →  Feature Engineer  →  Save

Run from the project root::

    python src/run_pipeline.py
"""

import os

import pandas as pd
from cryptography.fernet import Fernet

from data_cleaning import load_data, clean_data
from encryption import anonymize_pii, generate_key
from feature_engineering import extract_course_code, map_course_info, create_age_groups


# ---------------------------------------------------------------------------
# Path configuration
# ---------------------------------------------------------------------------

RAW_DATA_PATH = "data/raw/Inscripciones_alumnos_nuevos_respuestas_de_formulario_2.csv"
MAPPING_PATH = "data/raw/course_mapping.csv"
OUTPUT_PATH = "data/processed/data.csv"
KEY_ENV_VAR = "ENROLLMENT_FERNET_KEY"


# ---------------------------------------------------------------------------
# Pipeline
# ---------------------------------------------------------------------------

def run():
    print("=" * 55)
    print("  ENROLLMENT ANALYTICS — DATA PIPELINE")
    print("=" * 55)

    # ------------------------------------------------------------------
    # Step 1 — Load
    # ------------------------------------------------------------------
    print("\n[1/5] Loading raw data …")
    df = load_data(RAW_DATA_PATH, header_row=1)

    # ------------------------------------------------------------------
    # Step 2 — Clean
    # ------------------------------------------------------------------
    print("\n[2/5] Cleaning data …")
    df = clean_data(df)

    # ------------------------------------------------------------------
    # Step 3 — Anonymise PII  (hashing — one-way, irreversible)
    # ------------------------------------------------------------------
    print("\n[3/5] Anonymising PII columns …")
    df = anonymize_pii(df)

    # Fernet encryption 
    # Commented out because this pipeline doesn't actually need it
    # Hashing is sufficient for this pipeline.
    #
    # key = _load_or_create_key()
    # cipher = Fernet(key)
    # df = encrypt_column(df, "teacher_email", cipher)

    # ------------------------------------------------------------------
    # Step 4 — Feature engineering
    # ------------------------------------------------------------------
    print("\n[4/5] Engineering features …")
    df = extract_course_code(df)
    df = map_course_info(df, MAPPING_PATH)
    df = create_age_groups(df)

    # ------------------------------------------------------------------
    # Step 5 — Save processed output
    # ------------------------------------------------------------------
    print("\n[5/5] Saving processed data …")
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)
    print(f" Saved to {OUTPUT_PATH}  ({len(df)} rows)")

    print("\n" + "=" * 55)
    print("  Pipeline complete.")
    print("=" * 55)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_or_create_key() -> bytes:
    """
    Load the Fernet key from the environment, or generate a new one.

    In production, set the ENROLLMENT_FERNET_KEY environment variable.
    NEVER hard-code or commit the key.
    """
    key = os.environ.get(KEY_ENV_VAR)
    if key:
        return key.encode()

    print(
        f"[WARNING] '{KEY_ENV_VAR}' env var not set. "
        "Generating a new key — store it safely!"
    )
    new_key = generate_key()
    print(f"  KEY (save this securely): {new_key.decode()}")
    return new_key


if __name__ == "__main__":
    run()