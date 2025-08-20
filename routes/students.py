from flask import Blueprint, request, jsonify
from extensions import db
from models import Booking, Student, Tutor, Subject, User
from utils.decorators import role_required
from flask_jwt_extended import get_jwt_identity

# 👉 Khai báo blueprint
students_bp = Blueprint("students", __name__, url_prefix="/students")

# Tạo booking
@students_bp.post("/bookings")
@role_required("customer")  # chỉ customer mới được tạo booking
def create_booking():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)

    data = request.get_json() or {}
    student_id = data.get("student_id")
    tutor_id = data.get("tutor_id")
    subject_id = data.get("subject_id")
    start_at = data.get("start_at")  # expected ISO datetime string
    hours = data.get("hours", 1.0)

    if not (student_id and tutor_id and subject_id):
        return jsonify({"error": "student_id, tutor_id, subject_id là bắt buộc"}), 400

    bk = Booking(student_id=student_id, tutor_id=tutor_id, subject_id=subject_id,
                 start_at=start_at, hours=hours, status="pending")
    db.session.add(bk)
    db.session.commit()
    return jsonify({"message": "Đã tạo booking", "booking_id": bk.id}), 201

# Xem booking của chính mình
@students_bp.get("/bookings/me")
@role_required("customer", "tutor")
def my_bookings():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    results = []

    if user.customer_id:
        # customer -> list bookings của tất cả học sinh thuộc họ
        students = Student.query.filter_by(customer_id=user.customer_id).all()
        student_ids = [s.id for s in students]
        bks = Booking.query.filter(Booking.student_id.in_(student_ids)).all()
    elif user.tutor_id:
        # tutor -> list bookings của chính tutor đó
        bks = Booking.query.filter_by(tutor_id=user.tutor_id).all()
    else:
        bks = []

    for b in bks:
        results.append({
            "id": b.id,
            "student": b.student.full_name,
            "tutor": b.tutor.full_name,
            "subject": b.subject.name,
            "status": str(b.status),
            "start_at": b.start_at.isoformat() if b.start_at else None
        })
    return jsonify({"bookings": results})
