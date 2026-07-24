
def validate_password_strength(password: str) -> None:
    if len(password) < 8:
        raise ValueError("Password must be at least 8 characters long.")

    has_letter = any(char.isalpha() for char in password)
    has_digit = any(char.isdigit() for char in password)
    if not has_letter or not has_digit:
        raise ValueError("Password must contain at least one letter and one digit.")

