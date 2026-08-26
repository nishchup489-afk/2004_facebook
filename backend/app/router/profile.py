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

from app.schema import (
    ProfileCreate,
    ProfileResponse,
)

from app.service.profile import create_profile
from app.service.get_user_id import get_user_id_from_session


router = APIRouter(
    tags=["profile"]
)


def _empty_to_none(
    value: str | None,
) -> str | None:

    if value is None:
        return None

    value = value.strip()

    return value or None


def _parse_json_list(
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


@router.post(
    "/profile",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_profile_route(

    request: Request,

    username: str = Form(...),

    gender: str = Form(""),
    status_value: str = Form("", alias="status"),
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

    profile_pic: UploadFile | None = File(None),
):

    try:

        # Cookie
        #   ↓
        # sessions table
        #   ↓
        # user_id
        user_id = get_user_id_from_session(
            request
        )


        profile = ProfileCreate(
            username=username,

            gender=_empty_to_none(gender),

            status=_empty_to_none(
                status_value
            ),

            residence=_empty_to_none(
                residence
            ),

            birth_date=_empty_to_none(
                birth_date
            ),

            home_town=_empty_to_none(
                home_town
            ),

            high_school=_empty_to_none(
                high_school
            ),

            mobile=_empty_to_none(
                mobile
            ),

            websites=_parse_json_list(
                websites
            ),

            looking_for=_empty_to_none(
                looking_for
            ),

            interested_in=_empty_to_none(
                interested_in
            ),

            relationship_status=_empty_to_none(
                relationship_status
            ),

            relationship_with=None,

            political_views=_empty_to_none(
                political_views
            ),

            interests=_parse_json_list(
                interests
            ),

            favorite_music=_parse_json_list(
                favorite_music
            ),

            favorite_movies=_parse_json_list(
                favorite_movies
            ),

            bio=_empty_to_none(
                bio
            ),
        )


        return create_profile(
            user_id=user_id,
            profile=profile,
            profile_pic=profile_pic,
        )


    except ValueError as error:

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )