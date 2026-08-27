from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Request,
    status,
)

from app.schema import (
    FriendActionResponse,
    FriendRequestsResponse,
    FriendsResponse,
    FriendSuggestionsResponse,
    FriendshipStatusResponse,
    MutualFriendsResponse,
)

from app.service.get_user_id import (
    get_user_id_from_session,
)

from app.service.friends import (
    accept_friend_request,
    get_friend_requests,
    get_friend_suggestions,
    get_friends,
    get_friendship_status,
    get_mutual_friends,
    reject_friend_request,
    send_friend_request,
)


router = APIRouter(
    prefix="/friends",
    tags=["friends"],
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


# ==================================================
# STATIC ROUTES FIRST
# ==================================================


@router.get(
    "",
    response_model=FriendsResponse,
)
def get_friends_route(
    user_id: int = Depends(
        require_user_id
    ),
):

    return get_friends(
        current_user_id=user_id
    )


@router.get(
    "/requests",
    response_model=FriendRequestsResponse,
)
def get_friend_requests_route(
    user_id: int = Depends(
        require_user_id
    ),
):

    return get_friend_requests(
        current_user_id=user_id
    )


@router.get(
    "/suggestions",
    response_model=FriendSuggestionsResponse,
)
def get_friend_suggestions_route(
    user_id: int = Depends(
        require_user_id
    ),
):

    return get_friend_suggestions(
        current_user_id=user_id
    )


# ==================================================
# TARGET USER ROUTES
# ==================================================


@router.get(
    "/{target_user_id}/status",
    response_model=FriendshipStatusResponse,
)
def friendship_status_route(
    target_user_id: int,

    user_id: int = Depends(
        require_user_id
    ),
):

    return get_friendship_status(
        current_user_id=user_id,
        target_user_id=target_user_id,
    )


@router.get(
    "/{target_user_id}/mutual",
    response_model=MutualFriendsResponse,
)
def mutual_friends_route(
    target_user_id: int,

    user_id: int = Depends(
        require_user_id
    ),
):

    return get_mutual_friends(
        current_user_id=user_id,
        target_user_id=target_user_id,
    )


@router.post(
    "/{target_user_id}",
    response_model=FriendActionResponse,
)
def send_friend_request_route(
    target_user_id: int,

    user_id: int = Depends(
        require_user_id
    ),
):

    try:

        return send_friend_request(
            current_user_id=user_id,
            target_user_id=target_user_id,
        )


    except LookupError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.post(
    "/{target_user_id}/accept",
    response_model=FriendActionResponse,
)
def accept_friend_request_route(
    target_user_id: int,

    user_id: int = Depends(
        require_user_id
    ),
):

    try:

        return accept_friend_request(
            current_user_id=user_id,
            target_user_id=target_user_id,
        )


    except LookupError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.post(
    "/{target_user_id}/reject",
    response_model=FriendActionResponse,
)
def reject_friend_request_route(
    target_user_id: int,

    user_id: int = Depends(
        require_user_id
    ),
):

    try:

        return reject_friend_request(
            current_user_id=user_id,
            target_user_id=target_user_id,
        )


    except LookupError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )