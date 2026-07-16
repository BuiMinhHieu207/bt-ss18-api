from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Student, Course, Enrollment
from schemas import EnrollmentCreate


def create_enrollment(
    db: Session,
    enrollment_data: EnrollmentCreate
):
    student = (
        db.query(Student)
        .filter(Student.id == enrollment_data.student_id)
        .first()
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Sinh viên không tồn tại"
        )

    course = (
        db.query(Course)
        .filter(Course.id == enrollment_data.course_id)
        .first()
    )

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Khóa học không tồn tại"
        )

    if student.status != "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail="Sinh viên không còn hoạt động"
        )

    if course.status != "OPEN":
        raise HTTPException(
            status_code=400,
            detail="Khóa học đã đóng"
        )

    existing_enrollment = (
        db.query(Enrollment)
        .filter(
            Enrollment.student_id
            == enrollment_data.student_id,
            Enrollment.course_id
            == enrollment_data.course_id
        )
        .first()
    )

    if existing_enrollment:
        raise HTTPException(
            status_code=400,
            detail="Sinh viên đã đăng ký khóa học này"
        )

    current_students = (
        db.query(Enrollment)
        .filter(
            Enrollment.course_id
            == enrollment_data.course_id
        )
        .count()
    )

    if current_students >= course.max_students:
        raise HTTPException(
            status_code=400,
            detail="Khóa học đã đủ số lượng sinh viên"
        )

    new_enrollment = Enrollment(
        student_id=enrollment_data.student_id,
        course_id=enrollment_data.course_id
    )

    try:
        db.add(new_enrollment)
        db.commit()
        db.refresh(new_enrollment)

        return new_enrollment

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Không thể đăng ký khóa học"
        )


def get_student_courses(
    db: Session,
    student_id: int
):
    student = (
        db.query(Student)
        .filter(Student.id == student_id)
        .first()
    )

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Sinh viên không tồn tại"
        )

    courses = [
        enrollment.course
        for enrollment in student.enrollments
    ]

    return {
        "student_id": student.id,
        "full_name": student.full_name,
        "courses": courses
    }