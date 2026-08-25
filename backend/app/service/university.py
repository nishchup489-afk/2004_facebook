import hashlib
import secrets

from datetime import datetime

from app.schema import (
    UniversityAdmissionRequest,
    UniversityAdmissionResponse,
)

from app.config.settings import pool


ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _get_university_prefix(university_name: str) -> str:
    prefixes = {
        "Harvard University": "HARV",
        "Yale University": "YALE",
        "Massachusetts Institute of Technology": "MIT",
        "Columbia University": "COLU",
        "Stanford University": "STAN",
    }

    return prefixes[university_name]


def _get_registration_number(
    university_name: str,
) -> str:
    prefix = _get_university_prefix(university_name)

    year = datetime.now().year

    random_part = secrets.token_hex(5).upper()

    return f"{prefix}-{year}-{random_part}"


def _generate_registration_code() -> str:
    parts = []

    for _ in range(4):
        part = "".join(
            secrets.choice(ALPHABET)
            for _ in range(4)
        )

        parts.append(part)

    return "-".join(parts)


def _hash_registration_code(code: str) -> str:
    normalized = code.replace("-", "").upper()

    return hashlib.sha256(
        normalized.encode("utf-8")
    ).hexdigest()


def _get_university_email(
    first_name: str,
    last_name: str,
    email_domain: str,
) -> str:
    first_name = first_name.lower().strip()
    last_name = last_name.lower().strip()

    random_part = secrets.token_hex(4).lower()

    return (
        f"{first_name}.{last_name}.{random_part}"
        f"@{email_domain}"
    )


def admit_to_university(
    credentials: UniversityAdmissionRequest,
) -> UniversityAdmissionResponse:

    with pool.connection() as conn:
        with conn.cursor() as cursor:

            cursor.execute(
                """
                SELECT
                    id,
                    name,
                    email_domain
                FROM universities
                WHERE name = %s;
                """,
                (credentials.university,),
            )

            university = cursor.fetchone()

            if university is None:
                raise ValueError(
                    "University does not exist"
                )


            university_id = university[0]
            university_name = university[1]
            email_domain = university[2]


            first_name = credentials.first_name.strip()
            last_name = credentials.last_name.strip()


            university_email = _get_university_email(
                first_name,
                last_name,
                email_domain,
            )


            registration_number = (
                _get_registration_number(
                    university_name
                )
            )


            registration_code = (
                _generate_registration_code()
            )


            registration_code_hash = (
                _hash_registration_code(
                    registration_code
                )
            )


            cursor.execute(
                """
                INSERT INTO students (
                    university_id,
                    first_name,
                    last_name,
                    university_email,
                    registration_number,
                    registration_code_hash
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    %s,
                    %s
                )
                RETURNING id;
                """,
                (
                    university_id,
                    first_name,
                    last_name,
                    university_email,
                    registration_number,
                    registration_code_hash,
                ),
            )


            student = cursor.fetchone()

            student_id = student[0]


    return UniversityAdmissionResponse(
        student_id=student_id,
        university=university_name,
        first_name=first_name,
        last_name=last_name,
        university_email=university_email,
        registration_number=registration_number,
        registration_code=registration_code,
    )