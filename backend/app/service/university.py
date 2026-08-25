from app.schema import UniversityAdmissionResponse , UniversityAdmissionRequest
from app.config.settings import pool 


async def admit_to_university(credentials : UniversityAdmissionRequest) -> UniversityAdmissionResponse:
    pass