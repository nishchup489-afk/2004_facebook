import json

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)

from pydantic import ValidationError

from app.schema import (
    ProfileCreate,
    ProfileResponse,
    ProfileViewResponse,
)

from app.service.get_user_id import (
    get_user_id_from_session,
)

from app.service.profile import (
    get_profile,
    save_profile,
)


router = APIRouter(
    prefix="/profile",
    tags=["profile"],
)


def empty_to_none(
    value: str | None,
) -> str | None:

    if value is None:
        return None

    value = value.strip()

    return value or None


def parse_json_list(
    value: str,
) -> list[str]:

    try:
        result = json.loads(value)

    except json.JSONDecodeError:
        raise ValueError(
            "Invalid list data."
        )

    if not isinstance(result, list):
        raise ValueError(
            "Expected a list."
        )

    return result


def current_user_id(
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


@router.post(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def save_profile_route(

    request: Request,

    username: str = Form(...),

    gender: str = Form(""),

    profile_status: str = Form(
        "",
        alias="status",
    ),

    residence: str = Form(""),

    birth_date: str = Form(""),

    home_town: str = Form(""),

    high_school: str = Form(""),

    mobile: str = Form(""),

    websites: str = Form("[]"),

    looking_for: str = Form(""),

    interested_in: str = Form(""),

    relationship_status: str = Form(""),

    political_views: str = Form(""),

    interests: str = Form("[]"),

    favorite_music: str = Form("[]"),

    favorite_movies: str = Form("[]"),

    bio: str = Form(""),

    profile_pic: UploadFile | None = File(
        None
    ),
):

    user_id = current_user_id(
        request
    )

    try:

        profile = ProfileCreate(

            username=username,

            gender=empty_to_none(
                gender
            ),

            status=empty_to_none(
                profile_status
            ),

            residence=empty_to_none(
                residence
            ),

            birth_date=empty_to_none(
                birth_date
            ),

            home_town=empty_to_none(
                home_town
            ),

            high_school=empty_to_none(
                high_school
            ),

            mobile=empty_to_none(
                mobile
            ),

            websites=parse_json_list(
                websites
            ),

            looking_for=empty_to_none(
                looking_for
            ),

            interested_in=empty_to_none(
                interested_in
            ),

            relationship_status=(
                empty_to_none(
                    relationship_status
                )
            ),

            relationship_with=None,

            political_views=empty_to_none(
                political_views
            ),

            interests=parse_json_list(
                interests
            ),

            favorite_music=parse_json_list(
                favorite_music
            ),

            favorite_movies=parse_json_list(
                favorite_movies
            ),

            bio=empty_to_none(
                bio
            ),
        )


        return save_profile(
            user_id=user_id,
            profile=profile,
            profile_pic=profile_pic,
        )


    except ValidationError as error:

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error.errors(),
        )


    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.get(
    "/{user_id}",
    response_model=ProfileViewResponse,
)
def get_profile_route(
    user_id: int,
    request: Request,
):

    viewer_user_id = current_user_id(
        request
    )


    try:

        return get_profile(
            current_user_id=viewer_user_id,
            target_user_id=user_id,
        )


    except LookupError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )