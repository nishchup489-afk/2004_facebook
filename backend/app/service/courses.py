from app.config.settings import pool
from app.service.friends import (
    friendship_status_for_view,
)


SEMESTER_ORDER = """
    CASE c.semester
        WHEN 'fall' THEN 1
        WHEN 'summer' THEN 2
        WHEN 'spring' THEN 3
        WHEN 'winter' THEN 4
        ELSE 5
    END
"""


def course_from_row(
    row,
) -> dict:

    return {
        "course_id": row[0],
        "course_code": row[1],
        "course_name": row[2],
        "university_name": row[3],
        "academic_year": row[4],
        "semester": row[5],
        "enrollment_count": row[6] or 0,
        "is_enrolled": bool(row[7]),
    }


def student_from_row(
    row,
    current_user_id: int,
) -> dict:

    return {
        "user_id": row[0],
        "first_name": row[1],
        "last_name": row[2],
        "profile_pic": row[3],
        "university_name": row[4],
        "status": row[5],
        "username": row[6],
        "looking_for": row[7],
        "relationship_status": row[8],
        "friendship_status": (
            "self"
            if row[0] == current_user_id
            else friendship_status_for_view(
                current_user_id=current_user_id,
                requested_by=row[9],
                friendship_status=row[10],
            )
        ),
    }


def get_my_courses(
    current_user_id: int,
) -> dict:

    with pool.connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                f"""
                SELECT
                    c.id,
                    c.course_code,
                    c.course_name,
                    uni.name,
                    c.academic_year,
                    c.semester,
                    COUNT(all_enrollments.student_id)::INT,
                    TRUE AS is_enrolled

                FROM users AS u

                JOIN students AS s
                    ON s.id = u.student_id

                JOIN enrollments AS mine
                    ON mine.student_id = s.id

                JOIN courses AS c
                    ON c.id = mine.course_id

                JOIN universities AS uni
                    ON uni.id = c.university_id

                LEFT JOIN enrollments AS all_enrollments
                    ON all_enrollments.course_id = c.id

                WHERE u.id = %s
                  AND u.is_active = TRUE

                GROUP BY
                    c.id,
                    c.course_code,
                    c.course_name,
                    uni.name,
                    c.academic_year,
                    c.semester

                ORDER BY
                    c.academic_year DESC,
                    {SEMESTER_ORDER},
                    c.course_code;
                """,
                (
                    current_user_id,
                ),
            )

            rows = cur.fetchall()


    courses = [
        course_from_row(row)
        for row in rows
    ]


    return {
        "courses": courses,
        "count": len(courses),
    }


def search_courses(
    current_user_id: int,
    query: str | None = None,
    semester: str | None = None,
    academic_year: int | None = None,
) -> dict:

    conditions = [
        "c.university_id = me.university_id"
    ]

    params = [
        current_user_id,
    ]


    if query:

        query = query.strip()

        if query:

            conditions.append(
                """
                (
                    c.course_code ILIKE %s
                    OR
                    c.course_name ILIKE %s
                )
                """
            )

            params.extend(
                [
                    f"{query}%",
                    f"%{query}%",
                ]
            )


    if semester:

        conditions.append(
            "LOWER(c.semester) = LOWER(%s)"
        )

        params.append(
            semester
        )


    if academic_year is not None:

        conditions.append(
            "c.academic_year = %s"
        )

        params.append(
            academic_year
        )


    where_clause = " AND ".join(
        conditions
    )


    with pool.connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                f"""
                WITH me AS (

                    SELECT
                        s.id AS student_id,
                        s.university_id

                    FROM users AS u

                    JOIN students AS s
                        ON s.id = u.student_id

                    WHERE u.id = %s
                      AND u.is_active = TRUE
                )

                SELECT
                    c.id,
                    c.course_code,
                    c.course_name,
                    uni.name,
                    c.academic_year,
                    c.semester,
                    COUNT(all_enrollments.student_id)::INT,
                    CASE
                        WHEN mine.course_id IS NULL
                            THEN FALSE
                        ELSE TRUE
                    END AS is_enrolled

                FROM courses AS c

                CROSS JOIN me

                JOIN universities AS uni
                    ON uni.id = c.university_id

                LEFT JOIN enrollments AS all_enrollments
                    ON all_enrollments.course_id = c.id

                LEFT JOIN enrollments AS mine
                    ON mine.course_id = c.id
                   AND mine.student_id = me.student_id

                WHERE {where_clause}

                GROUP BY
                    c.id,
                    c.course_code,
                    c.course_name,
                    uni.name,
                    c.academic_year,
                    c.semester,
                    mine.course_id

                ORDER BY
                    c.academic_year DESC,
                    {SEMESTER_ORDER},
                    c.course_code

                LIMIT 100;
                """,
                params,
            )

            rows = cur.fetchall()


    courses = [
        course_from_row(row)
        for row in rows
    ]


    return {
        "courses": courses,
        "count": len(courses),
    }


def get_course_for_user(
    cur,
    current_user_id: int,
    course_id: int,
):

    cur.execute(
        """
        SELECT
            c.id,
            c.course_code,
            c.course_name,
            uni.name,
            c.academic_year,
            c.semester,
            COUNT(all_enrollments.student_id)::INT,
            CASE
                WHEN mine.course_id IS NULL
                    THEN FALSE
                ELSE TRUE
            END AS is_enrolled,
            s.id AS current_student_id

        FROM users AS u

        JOIN students AS s
            ON s.id = u.student_id

        JOIN courses AS c
            ON c.university_id = s.university_id
           AND c.id = %s

        JOIN universities AS uni
            ON uni.id = c.university_id

        LEFT JOIN enrollments AS all_enrollments
            ON all_enrollments.course_id = c.id

        LEFT JOIN enrollments AS mine
            ON mine.course_id = c.id
           AND mine.student_id = s.id

        WHERE u.id = %s
          AND u.is_active = TRUE

        GROUP BY
            c.id,
            c.course_code,
            c.course_name,
            uni.name,
            c.academic_year,
            c.semester,
            mine.course_id,
            s.id;
        """,
        (
            course_id,
            current_user_id,
        ),
    )

    return cur.fetchone()


def get_course_students(
    current_user_id: int,
    course_id: int,
) -> dict:

    with pool.connection() as conn:

        with conn.cursor() as cur:

            course_row = get_course_for_user(
                cur,
                current_user_id,
                course_id,
            )


            if course_row is None:

                raise LookupError(
                    "Course not found."
                )


            cur.execute(
                """
                SELECT
                    u.id,
                    u.first_name,
                    u.last_name,
                    p.profile_pic,
                    uni.name,
                    p.status,
                    p.username,
                    p.looking_for,
                    p.relationship_status,
                    f.requested_by,
                    f.status

                FROM enrollments AS e

                JOIN students AS s
                    ON s.id = e.student_id

                JOIN users AS u
                    ON u.student_id = s.id

                JOIN universities AS uni
                    ON uni.id = s.university_id

                LEFT JOIN profile AS p
                    ON p.user_id = u.id

                LEFT JOIN friendships AS f
                    ON f.user_id_low =
                        LEAST(%s, u.id)

                   AND f.user_id_high =
                        GREATEST(%s, u.id)

                WHERE e.course_id = %s
                  AND u.is_active = TRUE

                ORDER BY
                    u.last_name,
                    u.first_name;
                """,
                (
                    current_user_id,
                    current_user_id,
                    course_id,
                ),
            )

            rows = cur.fetchall()


    course = course_from_row(
        course_row
    )

    students = [
        student_from_row(
            row,
            current_user_id,
        )
        for row in rows
    ]


    return {
        "course": course,
        "students": students,
        "count": len(students),
    }


def enroll_in_course(
    current_user_id: int,
    course_id: int,
) -> dict:

    with pool.connection() as conn:

        with conn.cursor() as cur:

            course_row = get_course_for_user(
                cur,
                current_user_id,
                course_id,
            )


            if course_row is None:

                raise LookupError(
                    "Course not found."
                )


            current_student_id = course_row[8]

            cur.execute(
                """
                INSERT INTO enrollments (
                    student_id,
                    course_id
                )

                VALUES (
                    %s,
                    %s
                )

                ON CONFLICT DO NOTHING;
                """,
                (
                    current_student_id,
                    course_id,
                ),
            )


    return {
        "status": "enrolled",
        "message": "Course added.",
    }


def drop_course(
    current_user_id: int,
    course_id: int,
) -> dict:

    with pool.connection() as conn:

        with conn.cursor() as cur:

            course_row = get_course_for_user(
                cur,
                current_user_id,
                course_id,
            )


            if course_row is None:

                raise LookupError(
                    "Course not found."
                )


            current_student_id = course_row[8]

            cur.execute(
                """
                DELETE FROM enrollments
                WHERE student_id = %s
                  AND course_id = %s;
                """,
                (
                    current_student_id,
                    course_id,
                ),
            )


    return {
        "status": "dropped",
        "message": "Course removed.",
    }
