from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    Request,
    status,
)

from app.schema import (
    CourseActionResponse,
    CourseStudentsResponse,
    CoursesResponse,
)

from app.service.courses import (
    drop_course,
    enroll_in_course,
    get_course_students,
    get_my_courses,
    search_courses,
)

from app.service.get_user_id import (
    get_user_id_from_session,
)


router = APIRouter(
    prefix="/courses",
    tags=["courses"],
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


@router.get(
    "",
    response_model=CoursesResponse,
)
def search_courses_route(
    q: str | None = Query(
        default=None,
        max_length=150,
    ),

    semester: str | None = Query(
        default=None,
    ),

    academic_year: int | None = Query(
        default=None,
        ge=1900,
        le=2200,
    ),

    user_id: int = Depends(
        require_user_id
    ),
):

    return search_courses(
        current_user_id=user_id,
        query=q,
        semester=semester,
        academic_year=academic_year,
    )


@router.get(
    "/mine",
    response_model=CoursesResponse,
)
def get_my_courses_route(
    user_id: int = Depends(
        require_user_id
    ),
):

    return get_my_courses(
        current_user_id=user_id
    )


@router.get(
    "/{course_id}/students",
    response_model=CourseStudentsResponse,
)
def get_course_students_route(
    course_id: int,

    user_id: int = Depends(
        require_user_id
    ),
):

    try:

        return get_course_students(
            current_user_id=user_id,
            course_id=course_id,
        )

    except LookupError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.post(
    "/{course_id}/enroll",
    response_model=CourseActionResponse,
)
def enroll_in_course_route(
    course_id: int,

    user_id: int = Depends(
        require_user_id
    ),
):

    try:

        return enroll_in_course(
            current_user_id=user_id,
            course_id=course_id,
        )

    except LookupError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )


@router.delete(
    "/{course_id}/enroll",
    response_model=CourseActionResponse,
)
def drop_course_route(
    course_id: int,

    user_id: int = Depends(
        require_user_id
    ),
):

    try:

        return drop_course(
            current_user_id=user_id,
            course_id=course_id,
        )

    except LookupError as error:

        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        )
