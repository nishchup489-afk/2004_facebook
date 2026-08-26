from datetime import datetime, timedelta, timezone

import hashlib
import hmac
import secrets

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

from app.config.settings import pool
from app.schema import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
)


password_hasher = PasswordHasher()

SESSION_DURATION = timedelta(days=7)


def _generate_session_token() -> str:
    return secrets.token_urlsafe(32)


def _hash_session_token(token: str) -> str:
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def _generate_password_hash(password: str) -> str:
    return password_hasher.hash(password)


def _verify_password(
    password: str,
    password_hash: str,
) -> bool:
    try:
        return password_hasher.verify(
            password_hash,
            password,
        )

    except VerifyMismatchError:
        return False


def _match_registration_code(
    prompt: str,
    stored_hash: str,
) -> bool:
    normalized = (
        prompt
        .replace("-", "")
        .strip()
        .upper()
    )

    prompt_hash = hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()

    return hmac.compare_digest(
        prompt_hash,
        stored_hash,
    )


def _create_session(
    cursor,
    user_id: int,
) -> str:
    raw_session_token = _generate_session_token()

    session_token_hash = _hash_session_token(
        raw_session_token
    )

    expires_at = (
        datetime.now(timezone.utc)
        + SESSION_DURATION
    )

    cursor.execute(
        """
        INSERT INTO sessions (
            user_id,
            token_hash,
            expires_at
        )
        VALUES (%s, %s, %s);
        """,
        (
            user_id,
            session_token_hash,
            expires_at,
        ),
    )

    return raw_session_token


def register_user(
    credentials: RegisterRequest,
) -> tuple[RegisterResponse, str]:

    with pool.connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    first_name,
                    last_name,
                    university_email,
                    registration_code_hash,
                    claimed_at,
                    is_active
                FROM students
                WHERE LOWER(university_email) = LOWER(%s)
                FOR UPDATE;
                """,
                (credentials.university_email,),
            )

            student = cursor.fetchone()

            if student is None:
                raise ValueError(
                    "Student does not exist in university records."
                )

            (
                student_id,
                first_name,
                last_name,
                university_email,
                registration_code_hash,
                claimed_at,
                is_active,
            ) = student


            if not is_active:
                raise ValueError(
                    "Student account is inactive."
                )


            if claimed_at is not None:
                raise ValueError(
                    "User already exists. Try logging in."
                )


            cursor.execute(
                """
                SELECT id
                FROM users
                WHERE student_id = %s;
                """,
                (student_id,),
            )

            existing_user = cursor.fetchone()

            if existing_user is not None:
                raise ValueError(
                    "User already exists. Try logging in."
                )


            if (
                credentials.first_name.strip().casefold()
                != first_name.strip().casefold()
            ):
                raise ValueError(
                    "First name does not match university records."
                )


            if (
                credentials.last_name.strip().casefold()
                != last_name.strip().casefold()
            ):
                raise ValueError(
                    "Last name does not match university records."
                )


            if not _match_registration_code(
                credentials.registration_code,
                registration_code_hash,
            ):
                raise ValueError(
                    "Registration code didn't match. "
                    "Check your university portfolio."
                )


            password_hash = _generate_password_hash(
                credentials.password
            )


            cursor.execute(
                """
                INSERT INTO users (
                    student_id,
                    first_name,
                    last_name,
                    university_email,
                    password_hash
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING id;
                """,
                (
                    student_id,
                    first_name,
                    last_name,
                    university_email,
                    password_hash,
                ),
            )

            user = cursor.fetchone()

            user_id = user[0]


            cursor.execute(
                """
                UPDATE students
                SET claimed_at = NOW()
                WHERE id = %s;
                """,
                (student_id,),
            )


            raw_session_token = _create_session(
                cursor,
                user_id,
            )


    response = RegisterResponse(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        university_email=university_email,
        message="Registration successful",
    )

    return response, raw_session_token


def login_user(
    credentials: LoginRequest,
) -> tuple[LoginResponse, str]:

    with pool.connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    first_name,
                    last_name,
                    university_email,
                    password_hash,
                    is_active
                FROM users
                WHERE LOWER(university_email) = LOWER(%s);
                """,
                (credentials.university_email,),
            )

            user = cursor.fetchone()


            if user is None:
                raise ValueError(
                    "Invalid email or password."
                )


            (
                user_id,
                first_name,
                last_name,
                university_email,
                password_hash,
                is_active,
            ) = user


            if not is_active:
                raise ValueError(
                    "User account is inactive."
                )


            if not _verify_password(
                credentials.password,
                password_hash,
            ):
                raise ValueError(
                    "Invalid email or password."
                )


            raw_session_token = _create_session(
                cursor,
                user_id,
            )


    response = LoginResponse(
        user_id=user_id,
        first_name=first_name,
        last_name=last_name,
        university_email=university_email,
        message="Login successful",
    )

    return response, raw_session_token



def logout_user(raw_session_token: str) -> None:
    session_token_hash = _hash_session_token(
        raw_session_token
    )

    with pool.connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                DELETE FROM sessions
                WHERE token_hash = %s;
                """,
                (session_token_hash,),
            )


