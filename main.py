from fastapi import (
    FastAPI,
    Depends,
    status
)
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from schema import (
    EnrollmentDTO,
    EnrollmentResponse,
    StudentCourseResponse
)
import service


Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.post(
    "/enrollments",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED
)
def create_enrollment(
    enrollment: EnrollmentDTO,
    db: Session = Depends(get_db)
):
    return service.create_enrollment(
        db,
        enrollment
    )


@app.get(
    "/students/{student_id}/courses",
    response_model=StudentCourseResponse
)
def get_student_courses(
    student_id: int,
    db: Session = Depends(get_db)
):
    return service.get_student_courses(
        db,
        student_id
    )