import pandas as pd
from data_cleaning import load_data, clean_data
from encryption import anonymize
from feature_engineering import (
    extract_course_code,
    map_course_info,
    create_age_groups
)


def run_pipeline():
    """
    Main data pipeline:
    - Load raw data
    - Clean data
    - Anonymize sensitive fields
    - Extract course codes
    - Map course metadata
    - Create features
    - Save processed dataset
    """

    df = load_data("data/raw/sample.csv")

    df = clean_data(df)
    df = anonymize(df)

    df = extract_course_code(df)
    df = map_course_info(df, "data/raw/course_mapping.csv")

    df = create_age_groups(df)

    df.to_csv("data/processed/data.csv", index=False)

    print("✅ Pipeline executed successfully")


if __name__ == "__main__":
    run_pipeline()