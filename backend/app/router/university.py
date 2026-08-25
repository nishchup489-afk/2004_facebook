from fastapi import APIRouter, HTTPException

from app.schema import (
    UniversityAdmissionRequest,
    UniversityAdmissionResponse,
)

from app.service.university import admit_to_university


router = APIRouter(
    prefix="/university",
    tags=["university"]
)


@router.post(
    "",
    response_model=UniversityAdmissionResponse
)
def admit_student(
    credentials: UniversityAdmissionRequest
):
    try:
        return admit_to_university(credentials)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )