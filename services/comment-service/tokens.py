import os

from jose import jwt, JWTError


SECRET_KEY = os.getenv(
    "JWT_SECRET",
    "change-this-secret"
)

ALGORITHM = os.getenv(
    "JWT_ALGORITHM",
    "HS256"
)


def decode_token(token: str) -> dict:

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except JWTError:
        raise ValueError("Invalid token")