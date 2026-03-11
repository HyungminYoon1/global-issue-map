import uuid

from fastapi import Request, Response


COOKIE_NAME = "gim_session"
COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # 1년


def get_session_id(request: Request, response: Response) -> str:
    session_id = request.cookies.get(COOKIE_NAME)
    if not session_id:
        session_id = uuid.uuid4().hex
        response.set_cookie(
            key=COOKIE_NAME,
            value=session_id,
            max_age=COOKIE_MAX_AGE,
            httponly=True,
            samesite="lax",
        )
    return session_id
