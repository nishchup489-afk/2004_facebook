from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    field_validator,
) 


class RegisterRequest(BaseModel):
    university_email: EmailStr

    password: str = Field(
        min_length=8,
        max_length=128,
    )

    first_name: str = Field(
        min_length=1,
        max_length=150,
    )

    last_name: str = Field(
        min_length=1,
        max_length=150,
    )

    registration_code: str = Field(
        min_length=19,
        max_length=19,
    )

    @field_validator("university_email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()

    @field_validator(
        "first_name",
        "last_name",
    )
    @classmethod
    def normalize_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("registration_code")
    @classmethod
    def normalize_registration_code(
        cls,
        value: str,
    ) -> str:
        return value.strip().upper()

class RegisterResponse(BaseModel):
    user_id: int

    first_name: str
    last_name: str

    university_email: EmailStr

    message: str = "Registration successful"


class LoginRequest(BaseModel):
    university_email: EmailStr

    password: str = Field(
        min_length=1,
        max_length=128,
    )

    @field_validator("university_email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return str(value).strip().lower()


class LoginResponse(BaseModel):
    user_id: int

    first_name: str
    last_name: str

    university_email: EmailStr

    message: str = "Login successful"