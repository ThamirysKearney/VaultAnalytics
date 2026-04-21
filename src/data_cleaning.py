import pandas as pd

def load_data(path):
    df = pd.read_csv(path)
    return df

def clean_data(df):
    # Drop useless columns
    df = df.dropna(axis=1, how='all')

    # Rename columns manually (adjust if needed)
    df.columns = [
        "timestamp", "teacher_email", "empty", "cargar",
        "course_edition", "name", "first_name",
        "surname1", "surname2", "full_surname",
        "dob", "age", "student_email",
        "phone", "replacement"
    ]

    # Drop irrelevant columns
    df = df.drop(columns=[
        "empty", "cargar", "name",
        "first_name", "surname1",
        "surname2", "full_surname", "dob"
    ])

    # Convert timestamp
    df["timestamp"] = pd.to_datetime(df["timestamp"], dayfirst=True)

    # Feature engineering
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.day_name()

    return df