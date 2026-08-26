# [
#     {
#         "user_id": 8,
#         "first_name": "Alex",
#         "last_name": "Smith",
#         "profile_pic": "https://res.cloudinary.com/...",
#         "university_name": "Harvard University",
#         "status": "Student"
#     },
#     {
#         "user_id": 21,
#         "first_name": "Alex",
#         "last_name": "Johnson",
#         "profile_pic": null,
#         "university_name": "Harvard University",
#         "status": "Student"
#     }
# ]


from app.config.settings import pool


MAX_SEARCH_RESULTS = 50


def search_users(
    query: str,
    university_id: int | None = None,
    profile_status: str | None = None,
) -> list[dict]:

    query = query.strip()

    if not query:
        return []



        # Example:

        # "Alex Smith"
        #     ↓
        # ["Alex", "Smith"]
  

    parts = query.split()


    conditions = [
        "u.is_active = TRUE"
    ]

    params = []


    # /*
    #     NAME SEARCH
    # */

    if len(parts) == 1:

        name = parts[0]

        # /*
        #     One word could mean:

        #     Alex
        #     Smith

        #     So search both first and last name.
        # */

        conditions.append(
            """
            (
                u.first_name ILIKE %s
                OR
                u.last_name ILIKE %s
            )
            """
        )

        params.extend(
            [
                f"{name}%",
                f"{name}%",
            ]
        )


    else:

        # /*
        #     Alex Smith
        #        ↓
        #     first_name = Alex
        #     last_name = Smith

        #     For names like:

        #     Alex Van Smith

        #     first_name = Alex
        #     last_name = Van Smith
        # */

        first_name = parts[0]

        last_name = " ".join(
            parts[1:]
        )


        conditions.append(
            """
            (
                u.first_name ILIKE %s
                AND
                u.last_name ILIKE %s
            )
            """
        )


        params.extend(
            [
                f"{first_name}%",
                f"{last_name}%",
            ]
        )


    # /*
    #     UNIVERSITY FILTER
    # */

    if university_id is not None:

        conditions.append(
            "s.university_id = %s"
        )

        params.append(
            university_id
        )


    # /*
    #     PROFILE STATUS FILTER

    #     Student
    #     Alumni
    #     Faculty
    #     etc.
    # */

    if profile_status:

        conditions.append(
            """
            LOWER(p.status)
            =
            LOWER(%s)
            """
        )

        params.append(
            profile_status
        )


    # /*
    #     Combine:

    #     condition
    #     AND condition
    #     AND condition
    # */

    where_clause = " AND ".join(
        conditions
    )


    sql = f"""
        SELECT
            u.id,
            u.first_name,
            u.last_name,

            p.profile_pic,

            uni.id,
            uni.name,

            p.status,
            p.username

        FROM users AS u

        JOIN students AS s
            ON s.id = u.student_id

        JOIN universities AS uni
            ON uni.id = s.university_id

        LEFT JOIN profile AS p
            ON p.user_id = u.id

        WHERE
            {where_clause}

        ORDER BY

            /*
                Exact names first.
            */

            CASE

                WHEN
                    LOWER(
                        u.first_name
                        || ' '
                        || u.last_name
                    )
                    =
                    LOWER(%s)

                THEN 0

                ELSE 1

            END,

            u.last_name,
            u.first_name

        LIMIT %s;
    """


    # /*
    #     ORDER BY needs original query.

    #     LIMIT is parameterized too.
    # */

    params.extend(
        [
            query,
            MAX_SEARCH_RESULTS,
        ]
    )


    with pool.connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                sql,
                params,
            )

            rows = cur.fetchall()


    return [
        {
            "user_id": row[0],

            "first_name": row[1],

            "last_name": row[2],

            "profile_pic": row[3],

            "university_id": row[4],

            "university_name": row[5],

            "status": row[6],

            "username": row[7],
        }

        for row in rows
    ]



