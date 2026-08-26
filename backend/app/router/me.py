from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)

from app.config.settings import pool

from app.service.get_user_id import (
    get_user_id_from_session,
)


router = APIRouter(
    prefix="/me",
    tags=["me"],
)


def require_user_id(
    request: Request,
) -> int:
    """
    Authentication dependency.

    Cookie
        ↓
    session token
        ↓
    user_id

    Missing / expired / invalid session
        ↓
    401 Unauthorized
    """

    try:
        return get_user_id_from_session(
            request
        )

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        )


@router.get("")
def get_me(
    user_id: int = Depends(
        require_user_id
    ),
):

    with pool.connection() as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT
                    u.id,
                    u.first_name,
                    u.last_name,
                    u.university_email,

                    p.profile_pic,

                    uni.name

                FROM users AS u

                JOIN students AS s
                    ON s.id = u.student_id

                JOIN universities AS uni
                    ON uni.id = s.university_id

                LEFT JOIN profile AS p
                    ON p.user_id = u.id

                WHERE u.id = %s
                  AND u.is_active = TRUE;
                """,
                (user_id,),
            )

            user = cur.fetchone()


    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )


    return {
        "user_id": user[0],

        "first_name": user[1],

        "last_name": user[2],

        "university_email": user[3],

        "profile_pic": user[4],

        "university_name": user[5],
    }