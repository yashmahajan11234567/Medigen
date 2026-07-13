from jose import JWTError

from app.auth.jwt import create_access_token, decode_access_token
from app.auth.password import hash_password, verify_password


def test_password_hashing_round_trip():
    hashed_password = hash_password("Password123")

    assert hashed_password != "Password123"
    assert verify_password("Password123", hashed_password) is True


def test_access_token_round_trip():
    token = create_access_token(subject="42")
    payload = decode_access_token(token)

    assert payload["sub"] == "42"


def test_invalid_token_raises():
    try:
        decode_access_token("invalid-token")
    except JWTError:
        assert True
    else:
        assert False, "Expected JWTError for an invalid token"
