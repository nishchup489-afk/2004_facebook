from datetime import date, datetime

from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
)


class ProfileCreate(BaseModel):

    username: str = Field(
        min_length=1,
        max_length=50,
    )

    gender: str | None = Field(
        default=None,
        max_length=30,
    )

    status: str | None = Field(
        default=None,
        max_length=50,
    )

    residence: str | None = None

    birth_date: date | None = None

    home_town: str | None = Field(
        default=None,
        max_length=200,
    )

    high_school: str | None = Field(
        default=None,
        max_length=250,
    )

    mobile: str | None = Field(
        default=None,
        max_length=30,
    )

    websites: list[str] = Field(
        default_factory=list
    )

    looking_for: str | None = Field(
        default=None,
        max_length=100,
    )

    interested_in: str | None = Field(
        default=None,
        max_length=100,
    )

    relationship_status: str | None = Field(
        default=None,
        max_length=50,
    )

    relationship_with: int | None = None

    political_views: str | None = Field(
        default=None,
        max_length=100,
    )

    interests: list[str] = Field(
        default_factory=list
    )

    favorite_music: list[str] = Field(
        default_factory=list
    )

    favorite_movies: list[str] = Field(
        default_factory=list
    )

    bio: str | None = None


    @field_validator("username")
    @classmethod
    def clean_username(
        cls,
        value: str,
    ) -> str:

        value = value.strip()

        if not value:
            raise ValueError(
                "Username cannot be empty."
            )

        return value


    @field_validator(
        "gender",
        "status",
        "residence",
        "home_town",
        "high_school",
        "mobile",
        "looking_for",
        "interested_in",
        "relationship_status",
        "political_views",
        "bio",
    )
    @classmethod
    def strip_text(
        cls,
        value: str | None,
    ) -> str | None:

        if value is None:
            return None

        value = value.strip()

        return value or None


    @field_validator(
        "websites",
        "interests",
        "favorite_music",
        "favorite_movies",
    )
    @classmethod
    def clean_lists(
        cls,
        values: list[str],
    ) -> list[str]:

        return [
            value.strip()
            for value in values
            if value.strip()
        ]


class ProfileResponse(BaseModel):

    user_id: int

    profile_pic: str | None

    username: str

    gender: str | None

    status: str | None

    residence: str | None

    birth_date: date | None

    home_town: str | None

    high_school: str | None

    mobile: str | None

    websites: list[str]

    looking_for: str | None

    interested_in: str | None

    relationship_status: str | None

    relationship_with: int | None

    political_views: str | None

    interests: list[str]

    favorite_music: list[str]

    favorite_movies: list[str]

    bio: str | None

    created_at: datetime

    updated_at: datetime


class ProfileViewResponse(BaseModel):

    user_id: int

    is_self: bool

    first_name: str

    last_name: str

    university_email: EmailStr

    university_name: str

    profile_pic: str | None

    username: str

    gender: str | None

    status: str | None

    residence: str | None

    birth_date: date | None

    home_town: str | None

    high_school: str | None

    mobile: str | None

    websites: list[str]

    looking_for: str | None

    interested_in: str | None

    relationship_status: str | None

    political_views: str | None

    interests: list[str]

    favorite_music: list[str]

    favorite_movies: list[str]

    bio: str | None

    created_at: datetime

    updated_at: datetime