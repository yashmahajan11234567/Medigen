from passlib.context import CryptContext


# PBKDF2 keeps the foundation dependency-light and avoids bcrypt wheel issues on Python 3.12.
password_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def hash_password(password: str) -> str:
    return password_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_context.verify(plain_password, hashed_password)
