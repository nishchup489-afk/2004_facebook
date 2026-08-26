from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)

from app.service.get_user_id import (
    get_user_id_from_session,
)

from app.service.search import (
    search_users,
)


router = APIRouter(
    prefix="/search",
    tags=["search"],
)


def require_user_id(
    request: Request,
) -> int:

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
def search_users_route(
    q: str = Query(
        ...,
        min_length=1,
        max_length=150,
    ),

    school: int | None = Query(
        default=None
    ),

    profile_status: str | None = Query(
        default=None,
        alias="status",
    ),

    user_id: int = Depends(
        require_user_id
    ),
):

    # user_id is mainly here to ensure
    # the caller is authenticated.
    #
    # We don't need it for the actual
    # search query yet.

    query = q.strip()

    if not query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Search query cannot be empty.",
        )


    results = search_users(
        query=query,
        university_id=school,
        profile_status=profile_status,
    )


    return {
        "results": results,
        "count": len(results),
    }