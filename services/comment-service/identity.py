from fastapi import Header, HTTPException

from .tokens import decode_token


def get_current_user(
    authorization: str | None = Header(default=None)
) -> int:

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header"
        )

    token = authorization.replace("Bearer ", "", 1)

    try:
        payload = decode_token(token)

        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        return int(user_id)

    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )