from pydantic import BaseModel


class CourseSummary(BaseModel):

    course_id: int

    course_code: str

    course_name: str

    university_name: str

    academic_year: int

    semester: str

    enrollment_count: int

    is_enrolled: bool


class CourseStudentSummary(BaseModel):

    user_id: int

    first_name: str

    last_name: str

    profile_pic: str | None

    university_name: str

    status: str | None

    username: str | None

    looking_for: str | None = None

    relationship_status: str | None = None

    friendship_status: str = "none"


class CoursesResponse(BaseModel):

    courses: list[CourseSummary]

    count: int


class CourseStudentsResponse(BaseModel):

    course: CourseSummary

    students: list[CourseStudentSummary]

    count: int


class CourseActionResponse(BaseModel):

    status: str

    message: str
