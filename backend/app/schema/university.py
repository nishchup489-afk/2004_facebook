from pydantic import BaseModel, Field, field_validator


class UniversityAdmissionRequest(BaseModel):
    university: str = Field(min_length=1, max_length=150)
    first_name: str = Field(min_length=1, max_length=150)
    last_name: str = Field(min_length=1, max_length=150)

    @field_validator("university", "first_name", "last_name")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Field cannot be empty")

        return value


class UniversityAdmissionResponse(BaseModel):
    student_id: int
    university: str
    first_name: str
    last_name: str
    university_email: str
    registration_number: str
    registration_code: str