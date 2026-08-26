import cloudinary.uploader

from psycopg.types.json import Jsonb

from app.config import media
from app.config.settings import pool
from app.schema import (
    ProfileCreate,
    ProfileResponse,
)


def create_profile(
    user_id: int,
    profile: ProfileCreate,
    profile_pic=None,
) -> ProfileResponse:

    profile_pic_url = None


    # Upload a new picture only if one was supplied
    if profile_pic is not None:

        if (
            profile_pic.content_type is None
            or not profile_pic.content_type.startswith("image/")
        ):
            raise ValueError(
                "Profile picture must be an image."
            )


        upload_result = cloudinary.uploader.upload(
            profile_pic.file,

            folder="thefacebook/profile_pictures",

            public_id=f"user_{user_id}",

            overwrite=True,

            resource_type="image",
        )


        profile_pic_url = upload_result[
            "secure_url"
        ]


    with pool.connection() as conn:

        with conn.cursor() as cursor:

            cursor.execute(
                """
                INSERT INTO profile (
                    user_id,
                    profile_pic,
                    gender,
                    status,
                    residence,
                    birth_date,
                    home_town,
                    high_school,
                    username,
                    mobile,
                    websites,
                    looking_for,
                    interested_in,
                    relationship_status,
                    relationship_with,
                    political_views,
                    interests,
                    favorite_music,
                    favorite_movies,
                    bio
                )

                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s
                )

                ON CONFLICT (user_id)

                DO UPDATE SET
                    profile_pic =
                        COALESCE(
                            EXCLUDED.profile_pic,
                            profile.profile_pic
                        ),

                    gender =
                        EXCLUDED.gender,

                    status =
                        EXCLUDED.status,

                    residence =
                        EXCLUDED.residence,

                    birth_date =
                        EXCLUDED.birth_date,

                    home_town =
                        EXCLUDED.home_town,

                    high_school =
                        EXCLUDED.high_school,

                    username =
                        EXCLUDED.username,

                    mobile =
                        EXCLUDED.mobile,

                    websites =
                        EXCLUDED.websites,

                    looking_for =
                        EXCLUDED.looking_for,

                    interested_in =
                        EXCLUDED.interested_in,

                    relationship_status =
                        EXCLUDED.relationship_status,

                    relationship_with =
                        EXCLUDED.relationship_with,

                    political_views =
                        EXCLUDED.political_views,

                    interests =
                        EXCLUDED.interests,

                    favorite_music =
                        EXCLUDED.favorite_music,

                    favorite_movies =
                        EXCLUDED.favorite_movies,

                    bio =
                        EXCLUDED.bio

                RETURNING
                    user_id,
                    profile_pic,
                    username,
                    gender,
                    status,
                    residence,
                    birth_date,
                    home_town,
                    high_school,
                    mobile,
                    websites,
                    looking_for,
                    interested_in,
                    relationship_status,
                    relationship_with,
                    political_views,
                    interests,
                    favorite_music,
                    favorite_movies,
                    bio,
                    created_at,
                    updated_at;
                """,

                (
                    user_id,
                    profile_pic_url,

                    profile.gender,
                    profile.status,
                    profile.residence,
                    profile.birth_date,
                    profile.home_town,
                    profile.high_school,

                    profile.username,
                    profile.mobile,

                    Jsonb(profile.websites),

                    profile.looking_for,
                    profile.interested_in,
                    profile.relationship_status,
                    profile.relationship_with,
                    profile.political_views,

                    Jsonb(profile.interests),
                    Jsonb(profile.favorite_music),
                    Jsonb(profile.favorite_movies),

                    profile.bio,
                ),
            )


            result = cursor.fetchone()


    return ProfileResponse(
        user_id=result[0],
        profile_pic=result[1],
        username=result[2],
        gender=result[3],
        status=result[4],
        residence=result[5],
        birth_date=result[6],
        home_town=result[7],
        high_school=result[8],
        mobile=result[9],
        websites=result[10] or [],
        looking_for=result[11],
        interested_in=result[12],
        relationship_status=result[13],
        relationship_with=result[14],
        political_views=result[15],
        interests=result[16] or [],
        favorite_music=result[17] or [],
        favorite_movies=result[18] or [],
        bio=result[19],
        created_at=result[20],
        updated_at=result[21],
    )