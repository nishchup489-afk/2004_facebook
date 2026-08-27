from app.config.settings import pool


SUGGESTION_LIMIT = 20


def normalize_pair(
    user_a: int,
    user_b: int,
) -> tuple[int, int]:

    return (
        min(user_a, user_b),
        max(user_a, user_b),
    )


def friendship_status_for_view(
    current_user_id: int,
    requested_by: int | None,
    friendship_status: str | None,
) -> str:

    if friendship_status is None:
        return "none"

    if friendship_status == "accepted":
        return "accepted"

    if friendship_status == "rejected":
        return "none"

    if requested_by == current_user_id:
        return "pending_sent"

    return "pending_received"


def get_suggestion_reason(
    mutual_friend_count: int,
    looking_for: str | None,
    current_looking_for: str | None,
    friendship_status: str,
) -> str:

    if friendship_status == "pending_sent":
        return "Request pending"

    if friendship_status == "pending_received":
        return "Sent you a request"

    if (
        looking_for
        and current_looking_for
        and looking_for.lower()
        == current_looking_for.lower()
    ):
        return f"Also looking for {looking_for}"

    if looking_for:
        return f"Looking for {looking_for}"

    if mutual_friend_count == 1:
        return "1 mutual friend"

    if mutual_friend_count > 1:
        return f"{mutual_friend_count} mutual friends"

    return "Same university"


def send_friend_request(
    current_user_id: int,
    target_user_id: int,
) -> dict:

    if current_user_id == target_user_id:

        raise ValueError(
            "You cannot add yourself as a friend."
        )


    user_id_low, user_id_high = (
        normalize_pair(
            current_user_id,
            target_user_id,
        )
    )


    with pool.connection() as conn:

        with conn.cursor() as cur:

            # Make sure target exists.
            cur.execute(
                """
                SELECT id
                FROM users
                WHERE id = %s
                  AND is_active = TRUE;
                """,
                (target_user_id,),
            )

            target_user = cur.fetchone()


            if target_user is None:

                raise LookupError(
                    "User not found."
                )


            # Lock existing friendship row if one exists.
            cur.execute(
                """
                SELECT
                    requested_by,
                    status

                FROM friendships

                WHERE user_id_low = %s
                  AND user_id_high = %s

                FOR UPDATE;
                """,
                (
                    user_id_low,
                    user_id_high,
                ),
            )

            friendship = cur.fetchone()


            # No relationship yet.
            if friendship is None:

                cur.execute(
                    """
                    INSERT INTO friendships (
                        user_id_low,
                        user_id_high,
                        requested_by,
                        status
                    )

                    VALUES (
                        %s,
                        %s,
                        %s,
                        'pending'
                    );
                    """,
                    (
                        user_id_low,
                        user_id_high,
                        current_user_id,
                    ),
                )


            else:

                requested_by = friendship[0]
                friendship_status = friendship[1]


                if friendship_status == "accepted":

                    raise ValueError(
                        "You are already friends."
                    )


                if friendship_status == "pending":

                    if (
                        requested_by
                        == current_user_id
                    ):

                        raise ValueError(
                            "Friend request already sent."
                        )


                    raise ValueError(
                        "This user already sent you a friend request."
                    )


                # A previously rejected pair can
                # become pending again.
                if friendship_status == "rejected":

                    cur.execute(
                        """
                        UPDATE friendships

                        SET
                            requested_by = %s,
                            status = 'pending',
                            created_at = NOW(),
                            responded_at = NULL

                        WHERE user_id_low = %s
                          AND user_id_high = %s;
                        """,
                        (
                            current_user_id,
                            user_id_low,
                            user_id_high,
                        ),
                    )


    return {
        "status": "pending_sent",
        "message": "Friend request sent.",
    }


def get_friendship_status(
    current_user_id: int,
    target_user_id: int,
) -> dict:

    if current_user_id == target_user_id:

        return {
            "status": "self"
        }


    user_id_low, user_id_high = (
        normalize_pair(
            current_user_id,
            target_user_id,
        )
    )


    with pool.connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    requested_by,
                    status

                FROM friendships

                WHERE user_id_low = %s
                  AND user_id_high = %s;
                """,
                (
                    user_id_low,
                    user_id_high,
                ),
            )

            friendship = cur.fetchone()


    if friendship is None:

        return {
            "status": "none"
        }


    requested_by = friendship[0]
    friendship_status = friendship[1]


    return {
        "status": friendship_status_for_view(
            current_user_id=current_user_id,
            requested_by=requested_by,
            friendship_status=friendship_status,
        )
    }


def accept_friend_request(
    current_user_id: int,
    target_user_id: int,
) -> dict:

    return respond_to_friend_request(
        current_user_id=current_user_id,
        target_user_id=target_user_id,
        new_status="accepted",
    )


def reject_friend_request(
    current_user_id: int,
    target_user_id: int,
) -> dict:

    return respond_to_friend_request(
        current_user_id=current_user_id,
        target_user_id=target_user_id,
        new_status="rejected",
    )


def respond_to_friend_request(
    current_user_id: int,
    target_user_id: int,
    new_status: str,
) -> dict:

    if current_user_id == target_user_id:

        raise ValueError(
            "Invalid friend request."
        )


    user_id_low, user_id_high = (
        normalize_pair(
            current_user_id,
            target_user_id,
        )
    )


    with pool.connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    requested_by,
                    status

                FROM friendships

                WHERE user_id_low = %s
                  AND user_id_high = %s

                FOR UPDATE;
                """,
                (
                    user_id_low,
                    user_id_high,
                ),
            )

            friendship = cur.fetchone()


            if friendship is None:

                raise LookupError(
                    "Friend request not found."
                )


            requested_by = friendship[0]
            friendship_status = friendship[1]


            if friendship_status != "pending":

                raise ValueError(
                    "Friend request is not pending."
                )


            # Target ID must be the person
            # who originally sent the request.
            if requested_by != target_user_id:

                raise ValueError(
                    "You did not receive a friend request from this user."
                )


            cur.execute(
                """
                UPDATE friendships

                SET
                    status = %s,
                    responded_at = NOW()

                WHERE user_id_low = %s
                  AND user_id_high = %s;
                """,
                (
                    new_status,
                    user_id_low,
                    user_id_high,
                ),
            )


    if new_status == "accepted":

        return {
            "status": "accepted",
            "message": "Friend request accepted.",
        }


    return {
        "status": "rejected",
        "message": "Friend request rejected.",
    }


def get_friends(
    current_user_id: int,
) -> dict:

    with pool.connection() as conn:

        with conn.cursor() as cur:

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
                    p.relationship_status

                FROM friendships AS f

                JOIN users AS u
                    ON u.id =
                        CASE

                            WHEN f.user_id_low = %s
                                THEN f.user_id_high

                            ELSE f.user_id_low

                        END

                JOIN students AS s
                    ON s.id = u.student_id

                JOIN universities AS uni
                    ON uni.id = s.university_id

                LEFT JOIN profile AS p
                    ON p.user_id = u.id

                WHERE f.status = 'accepted'

                  AND (
                      f.user_id_low = %s
                      OR
                      f.user_id_high = %s
                  )

                  AND u.is_active = TRUE

                ORDER BY
                    u.last_name,
                    u.first_name;
                """,
                (
                    current_user_id,
                    current_user_id,
                    current_user_id,
                ),
            )

            rows = cur.fetchall()


    friends = [
        {
            "user_id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "profile_pic": row[3],
            "university_name": row[4],
            "status": row[5],
            "username": row[6],
            "looking_for": row[7],
            "relationship_status": row[8],
            "friendship_status": "accepted",
        }

        for row in rows
    ]


    return {
        "friends": friends,
        "count": len(friends),
    }


def get_friend_requests(
    current_user_id: int,
) -> dict:

    with pool.connection() as conn:

        with conn.cursor() as cur:

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
                    p.relationship_status

                FROM friendships AS f

                JOIN users AS u
                    ON u.id = f.requested_by

                JOIN students AS s
                    ON s.id = u.student_id

                JOIN universities AS uni
                    ON uni.id = s.university_id

                LEFT JOIN profile AS p
                    ON p.user_id = u.id

                WHERE f.status = 'pending'

                  AND f.requested_by <> %s

                  AND (
                      f.user_id_low = %s
                      OR
                      f.user_id_high = %s
                  )

                  AND u.is_active = TRUE

                ORDER BY
                    f.created_at DESC;
                """,
                (
                    current_user_id,
                    current_user_id,
                    current_user_id,
                ),
            )

            rows = cur.fetchall()


    requests = [
        {
            "user_id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "profile_pic": row[3],
            "university_name": row[4],
            "status": row[5],
            "username": row[6],
            "looking_for": row[7],
            "relationship_status": row[8],
            "friendship_status": "pending_received",
        }

        for row in rows
    ]


    return {
        "requests": requests,
        "count": len(requests),
    }


def get_mutual_friends(
    current_user_id: int,
    target_user_id: int,
) -> dict:

    with pool.connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                WITH current_friends AS (

                    SELECT

                        CASE

                            WHEN user_id_low = %s
                                THEN user_id_high

                            ELSE user_id_low

                        END AS friend_id

                    FROM friendships

                    WHERE status = 'accepted'

                      AND (
                          user_id_low = %s
                          OR
                          user_id_high = %s
                      )
                ),

                target_friends AS (

                    SELECT

                        CASE

                            WHEN user_id_low = %s
                                THEN user_id_high

                            ELSE user_id_low

                        END AS friend_id

                    FROM friendships

                    WHERE status = 'accepted'

                      AND (
                          user_id_low = %s
                          OR
                          user_id_high = %s
                      )
                ),

                mutual AS (

                    SELECT friend_id
                    FROM current_friends

                    INTERSECT

                    SELECT friend_id
                    FROM target_friends
                )

                SELECT
                    u.id,
                    u.first_name,
                    u.last_name,

                    p.profile_pic,

                    uni.name,

                    p.status,
                    p.username,
                    p.looking_for,
                    p.relationship_status

                FROM mutual AS m

                JOIN users AS u
                    ON u.id = m.friend_id

                JOIN students AS s
                    ON s.id = u.student_id

                JOIN universities AS uni
                    ON uni.id = s.university_id

                LEFT JOIN profile AS p
                    ON p.user_id = u.id

                WHERE u.is_active = TRUE

                ORDER BY
                    u.last_name,
                    u.first_name;
                """,
                (
                    current_user_id,
                    current_user_id,
                    current_user_id,

                    target_user_id,
                    target_user_id,
                    target_user_id,
                ),
            )

            rows = cur.fetchall()


    friends = [
        {
            "user_id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "profile_pic": row[3],
            "university_name": row[4],
            "status": row[5],
            "username": row[6],
            "looking_for": row[7],
            "relationship_status": row[8],
            "friendship_status": "accepted",
        }

        for row in rows
    ]


    return {
        "friends": friends,
        "count": len(friends),
    }


def get_friend_suggestions(
    current_user_id: int,
) -> dict:

    with pool.connection() as conn:

        with conn.cursor() as cur:

            cur.execute(
                """
                WITH me AS (

                    SELECT
                        s.university_id,
                        p.looking_for

                    FROM users AS u

                    JOIN students AS s
                        ON s.id = u.student_id

                    LEFT JOIN profile AS p
                        ON p.user_id = u.id

                    WHERE u.id = %s
                ),

                my_friends AS (

                    SELECT

                        CASE

                            WHEN f.user_id_low = %s
                                THEN f.user_id_high

                            ELSE f.user_id_low

                        END AS friend_id

                    FROM friendships AS f

                    WHERE f.status = 'accepted'

                      AND (
                          f.user_id_low = %s
                          OR
                          f.user_id_high = %s
                      )
                ),

                mutual_counts AS (

                    SELECT
                        candidate.id
                            AS candidate_id,

                        COUNT(
                            my_friends.friend_id
                        )::INT
                            AS mutual_friend_count

                    FROM users AS candidate

                    JOIN students AS candidate_student
                        ON candidate_student.id =
                            candidate.student_id

                    CROSS JOIN me

                    LEFT JOIN friendships AS candidate_friendship

                        ON candidate_friendship.status =
                            'accepted'

                        AND (
                            candidate_friendship.user_id_low =
                                candidate.id

                            OR

                            candidate_friendship.user_id_high =
                                candidate.id
                        )

                    LEFT JOIN my_friends

                        ON my_friends.friend_id =

                            CASE

                                WHEN
                                    candidate_friendship.user_id_low =
                                    candidate.id

                                    THEN
                                    candidate_friendship.user_id_high

                                ELSE
                                    candidate_friendship.user_id_low

                            END

                    WHERE candidate_student.university_id =
                        me.university_id

                      AND candidate.id <> %s

                    GROUP BY
                        candidate.id
                )

                SELECT
                    u.id,
                    u.first_name,
                    u.last_name,

                    p.profile_pic,

                    uni.name,

                    p.status,
                    p.username,

                    COALESCE(
                        mutual_counts.mutual_friend_count,
                        0
                    ),

                    p.looking_for,
                    p.relationship_status,

                    candidate_friendship.requested_by,
                    candidate_friendship.status,

                    me.looking_for

                FROM users AS u

                JOIN students AS s
                    ON s.id = u.student_id

                JOIN universities AS uni
                    ON uni.id = s.university_id

                CROSS JOIN me

                LEFT JOIN profile AS p
                    ON p.user_id = u.id

                LEFT JOIN mutual_counts
                    ON mutual_counts.candidate_id =
                        u.id

                LEFT JOIN friendships AS candidate_friendship
                    ON candidate_friendship.user_id_low =
                        LEAST(%s, u.id)

                   AND candidate_friendship.user_id_high =
                        GREATEST(%s, u.id)

                WHERE s.university_id =
                    me.university_id

                  AND u.id <> %s

                  AND u.is_active = TRUE

                  AND (
                      candidate_friendship.status IS NULL
                      OR
                      candidate_friendship.status <> 'accepted'
                  )

                ORDER BY

                    CASE

                        WHEN
                            candidate_friendship.status =
                            'pending'
                            AND
                            candidate_friendship.requested_by =
                            %s

                            THEN 1

                        WHEN
                            candidate_friendship.status =
                            'pending'

                            THEN 2

                        ELSE 0

                    END,

                    CASE

                        WHEN
                            p.looking_for IS NOT NULL
                            AND
                            me.looking_for IS NOT NULL
                            AND
                            LOWER(p.looking_for) =
                            LOWER(me.looking_for)

                            THEN 0

                        ELSE 1

                    END,

                    COALESCE(
                        mutual_counts.mutual_friend_count,
                        0
                    ) DESC,

                    u.last_name,
                    u.first_name

                LIMIT %s;
                """,
                (
                    current_user_id,

                    current_user_id,
                    current_user_id,
                    current_user_id,

                    current_user_id,

                    current_user_id,

                    current_user_id,
                    current_user_id,

                    current_user_id,

                    SUGGESTION_LIMIT,
                ),
            )

            rows = cur.fetchall()


    suggestions = []


    for row in rows:

        friendship_status = friendship_status_for_view(
            current_user_id=current_user_id,
            requested_by=row[10],
            friendship_status=row[11],
        )

        mutual_friend_count = row[7] or 0


        suggestions.append({
            "user_id": row[0],
            "first_name": row[1],
            "last_name": row[2],
            "profile_pic": row[3],
            "university_name": row[4],
            "status": row[5],
            "username": row[6],
            "mutual_friend_count": mutual_friend_count,
            "looking_for": row[8],
            "relationship_status": row[9],
            "friendship_status": friendship_status,
            "suggestion_reason": get_suggestion_reason(
                mutual_friend_count=mutual_friend_count,
                looking_for=row[8],
                current_looking_for=row[12],
                friendship_status=friendship_status,
            ),
        })


    return {
        "suggestions": suggestions,
        "count": len(suggestions),
    }
