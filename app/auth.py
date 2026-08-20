from fastapi import Header, HTTPException


DEMO_TOKENS = {
    "phase1-viewer": "viewer",
    "phase1-admin": "admin",
}


def authenticate(
    authorization: str | None = Header(default=None)
) -> str:

    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authentication required"
        )

    expected_prefix = "Bearer "

    if not authorization.startswith(expected_prefix):
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication scheme"
        )

    token = authorization[len(expected_prefix):]

    role = DEMO_TOKENS.get(token)

    if role is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

    return role


def require_admin(role: str) -> None:

    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions"
        )