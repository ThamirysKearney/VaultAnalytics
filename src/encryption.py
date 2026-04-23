"""
Handles PII protection via two strategies:
  1. One-way hashing (SHA-256)  — for identifiers that only need to be
     compared, never recovered (e-mails, phone numbers).
  2. Symmetric encryption (Fernet / AES-128-CBC) — for fields that may
     need to be decrypted later by an authorised party.

Part of the Enrollment Analytics Project — Cybersecurity layer.

"""

import hashlib

import pandas as pd
from cryptography.fernet import Fernet


# ---------------------------------------------------------------------------
# Hashing
# ---------------------------------------------------------------------------

def hash_value(value: str) -> str:
    """
    Return the SHA-256 hex-digest of *value*.

    SHA-256 is a one-way function: the original value CANNOT be recovered.
    Only for columns that  need to be compared (e.g. detect duplicates)
    but never display in plain text.

    Parameters
    ----------
    value : str
        Raw PII string (e-mail, phone, etc.).

    Returns
    -------
    str | original type
        64-character hex string, or the original value if it is NaN/None.
    """
    if pd.isna(value):
        return value
    return hashlib.sha256(str(value).encode()).hexdigest()


def anonymize_pii(df: pd.DataFrame) -> pd.DataFrame:
    """
    Replace PII columns with their SHA-256 hashes IN PLACE.

    Columns anonymised
    ------------------
    - teacher_email
    - student_email
    - phone

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned (but not yet anonymised) enrollment data.

    Returns
    -------
    pd.DataFrame
        Same DataFrame with PII columns replaced by hashes.
    """
    pii_columns = ["teacher_email", "student_email", "phone"]

    for col in pii_columns:
        if col in df.columns:
            df[col] = df[col].apply(hash_value)
        else:
            print(f"[WARNING] Column '{col}' not found — skipping anonymisation.")

    return df


# ---------------------------------------------------------------------------
# Symmetric encryption (Fernet)
# ---------------------------------------------------------------------------

def generate_key() -> bytes:
    """
    Generate a new Fernet key.

    IMPORTANT — save the returned key securely (e.g. environment variable
    or secrets manager).  Without it the encrypted data CANNOT be recovered.

    Returns
    -------
    bytes
        32-byte URL-safe base64-encoded key.
    """
    return Fernet.generate_key()


def encrypt_value(value: str, cipher: Fernet) -> str:
    """
    Encrypt a single string value with the provided Fernet cipher.

    Parameters
    ----------
    value : str
        Plaintext string to encrypt.
    cipher : Fernet
        Initialised Fernet instance (created from a saved key).

    Returns
    -------
    str
        URL-safe base64 ciphertext string, or the original value if NaN.
    """
    if pd.isna(value):
        return value
    return cipher.encrypt(str(value).encode()).decode()


def decrypt_value(value: str, cipher: Fernet) -> str:
    """
    Decrypt a single value previously encrypted with *encrypt_value*.

    Parameters
    ----------
    value : str
        Ciphertext string.
    cipher : Fernet
        Same Fernet instance used during encryption.

    Returns
    -------
    str
        Decrypted plaintext string, or the original value if NaN.
    """
    if pd.isna(value):
        return value
    return cipher.decrypt(str(value).encode()).decode()


def encrypt_column(df: pd.DataFrame, column: str, cipher: Fernet) -> pd.DataFrame:
    """
    Encrypt every non-null value in *column* using Fernet symmetric encryption.

    Use this (instead of hashing) when the original value may need to be recovered 
    later (e.g. to contact a student).

    Parameters
    ----------
    df : pd.DataFrame
    column : str
        Name of the column to encrypt.
    cipher : Fernet
        Initialised Fernet instance.

    Returns
    -------
    pd.DataFrame
        DataFrame with the specified column encrypted.
    """
    if column not in df.columns:
        raise KeyError(f"Column '{column}' not found in DataFrame.")

    df[column] = df[column].apply(lambda v: encrypt_value(v, cipher))
    return df