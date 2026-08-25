import os
from dotenv import load_dotenv
from fastapi import (
    APIRouter,
    HTTPException,
    Request,
    Response,
    status,
)

from app.schema import (
    RegisterRequest,
    RegisterResponse,
    LoginRequest,
    LoginResponse,
)

from app.service.auth import (
    register_user,
    login_user,
    logout_user,
)


load_dotenv()

router = APIRouter(
    tags=["auth"]
)


COOKIE_NAME = os.getenv("COOKIE_NAME")

COOKIE_MAX_AGE = os.getenv("COOKIE_MAX_AGE")


def _set_session_cookie(
    response: Response,
    session_token: str,
) -> None:

    response.set_cookie(
        key=COOKIE_NAME,
        value=session_token,

        httponly=True,

        secure=False,  # True in production with HTTPS

        samesite="lax",

        max_age=COOKIE_MAX_AGE,

        path="/",
    )


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(
    credentials: RegisterRequest,
    response: Response,
):

    try:
        result, session_token = register_user(
            credentials
        )

        _set_session_cookie(
            response,
            session_token,
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        )


@router.post(
    "/login",
    response_model=LoginResponse,
)
def login(
    credentials: LoginRequest,
    response: Response,
):

    try:
        result, session_token = login_user(
            credentials
        )

        _set_session_cookie(
            response,
            session_token,
        )

        return result

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(error),
        )


@router.post("/logout")
def logout(
    request: Request,
    response: Response,
):

    session_token = request.cookies.get(
        COOKIE_NAME
    )

    if session_token:
        logout_user(
            session_token
        )

    response.delete_cookie(
        key=COOKIE_NAME,
        path="/",
    )

    return {
        "message": "Logged out successfully"
    }