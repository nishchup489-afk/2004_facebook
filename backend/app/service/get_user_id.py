import os
from dotenv import load_dotenv
from fastapi import Request
from app.config.settings import pool
from app.service.auth import _hash_session_token


load_dotenv()

COOKIE_NAME = os.getenv("COOKIE_NAME")


def get_user_id_from_session(
    request: Request,
) -> int:

    raw_session_token = request.cookies.get(
        COOKIE_NAME
    )

    if raw_session_token is None:
        raise ValueError(
            "You are not logged in."
        )


    session_token_hash = _hash_session_token(
        raw_session_token
    )


    with pool.connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT s.user_id
                FROM sessions s
                JOIN users u
                    ON u.id = s.user_id
                WHERE s.token_hash = %s
                  AND s.expires_at > NOW()
                  AND u.is_active = TRUE;
                """,
                (session_token_hash,),
            )

            session = cursor.fetchone()


    if session is None:
        raise ValueError(
            "Session is invalid or expired."
        )


    return session[0]
