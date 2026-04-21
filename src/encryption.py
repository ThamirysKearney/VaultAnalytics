import hashlib
from cryptography.fernet import Fernet

def hash_value(value):
    if pd.isna(value):
        return value
    return hashlib.sha256(str(value).encode()).hexdigest()

def anonymize(df):
    df["teacher_email"] = df["teacher_email"].apply(hash_value)
    df["student_email"] = df["student_email"].apply(hash_value)
    df["phone"] = df["phone"].apply(hash_value)
    return df

def encrypt_data(data, key):
    cipher = Fernet(key)
    return cipher.encrypt(data)

def generate_key():
    return Fernet.generate_key()