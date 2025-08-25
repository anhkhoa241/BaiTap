# API endpoints cho Tutors
from flask import request, jsonify
from extensions import db
from models import Tutor, Subject, TutorSubject
from routes import api

# GET /api/tutors - Lấy danh sách tất cả gia sư
@api.route("/tutors", methods=["GET"])
def get_tutors():
    """Lấy danh sách gia sư với filter tùy chọn"""
    # Lấy query parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    city = request.args.get('city', '')
    subject = request.args.get('subject', '')
    
    # Build query
    query = Tutor.query
    
    # Filter theo city
    if city:
        query = query.filter(Tutor.city.ilike(f'%{city}%'))
    
    # Filter theo subject (join với TutorSubject và Subject)
    if subject:
        query = query.join(TutorSubject).join(Subject).filter(
            Subject.name.ilike(f'%{subject}%')
        )
    
    # Pagination
    tutors_paginated = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Serialize data
    tutors_data = []
    for tutor in tutors_paginated.items:
        tutors_data.append({
            "id": tutor.id,
            "full_name": tutor.full_name,
            "email": tutor.email,
            "phone": tutor.phone,
            "years_experience": tutor.years_experience,
            "hourly_rate": tutor.hourly_rate,
            "bio": tutor.bio,
            "city": tutor.city,
            "rating_avg": tutor.rating_avg,
            "rating_count": tutor.rating_count,
            "created_at": tutor.created_at.isoformat() if tutor.created_at else None
        })
    
    return jsonify({
        "tutors": tutors_data,
        "pagination": {
            "page": tutors_paginated.page,
            "pages": tutors_paginated.pages,
            "per_page": tutors_paginated.per_page,
            "total": tutors_paginated.total
        }
    })

# GET /api/tutors/<id> - Lấy chi tiết 1 gia sư
@api.route("/tutors/<int:tutor_id>", methods=["GET"])
def get_tutor(tutor_id):
    """Lấy thông tin chi tiết của 1 gia sư"""
    tutor = Tutor.query.get_or_404(tutor_id)
    
    # Lấy danh sách môn dạy
    subjects = db.session.query(Subject).join(TutorSubject).filter(
        TutorSubject.tutor_id == tutor_id
    ).all()
    
    return jsonify({
        "id": tutor.id,
        "full_name": tutor.full_name,
        "email": tutor.email,
        "phone": tutor.phone,
        "years_experience": tutor.years_experience,
        "hourly_rate": tutor.hourly_rate,
        "bio": tutor.bio,
        "city": tutor.city,
        "rating_avg": tutor.rating_avg,
        "rating_count": tutor.rating_count,
        "subjects": [{"id": s.id, "name": s.name, "code": s.code} for s in subjects],
        "created_at": tutor.created_at.isoformat() if tutor.created_at else None
    })

# POST /api/tutors - Tạo gia sư mới
@api.route("/tutors", methods=["POST"])
def create_tutor():
    """Tạo gia sư mới"""
    data = request.get_json() or {}
    
    # Validate required fields
    required_fields = ["full_name", "email", "years_experience", "city"]
    if not all(field in data for field in required_fields):
        return jsonify({
            "error": f"Các trường bắt buộc: {', '.join(required_fields)}"
        }), 400
    
    # Check email unique
    if Tutor.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email đã được sử dụng"}), 400
    
    # Create tutor
    tutor = Tutor(
        full_name=data["full_name"],
        email=data["email"],
        phone=data.get("phone"),
        years_experience=data["years_experience"],
        hourly_rate=data.get("hourly_rate", 0),
        bio=data.get("bio"),
        city=data["city"]
    )
    
    db.session.add(tutor)
    db.session.commit()
    
    return jsonify({
        "message": "Tạo gia sư thành công",
        "tutor": {
            "id": tutor.id,
            "full_name": tutor.full_name,
            "email": tutor.email,
            "city": tutor.city
        }
    }), 201

# PUT /api/tutors/<id> - Cập nhật gia sư
@api.route("/tutors/<int:tutor_id>", methods=["PUT"])
def update_tutor(tutor_id):
    """Cập nhật thông tin gia sư"""
    tutor = Tutor.query.get_or_404(tutor_id)
    data = request.get_json() or {}
    
    # Update fields
    updatable_fields = ["full_name", "phone", "years_experience", "hourly_rate", "bio", "city"]
    for field in updatable_fields:
        if field in data:
            setattr(tutor, field, data[field])
    
    # Check email unique (nếu có thay đổi email)
    if "email" in data and data["email"] != tutor.email:
        if Tutor.query.filter_by(email=data["email"]).first():
            return jsonify({"error": "Email đã được sử dụng"}), 400
        tutor.email = data["email"]
    
    db.session.commit()
    
    return jsonify({
        "message": "Cập nhật gia sư thành công",
        "tutor": {
            "id": tutor.id,
            "full_name": tutor.full_name,
            "email": tutor.email,
            "city": tutor.city
        }
    })

# DELETE /api/tutors/<id> - Xóa gia sư
@api.route("/tutors/<int:tutor_id>", methods=["DELETE"])
def delete_tutor(tutor_id):
    """Xóa gia sư"""
    tutor = Tutor.query.get_or_404(tutor_id)
    
    db.session.delete(tutor)
    db.session.commit()
    
    return jsonify({"message": "Xóa gia sư thành công"})

# POST /api/tutors/<id>/subjects - Thêm môn dạy cho gia sư
@api.route("/tutors/<int:tutor_id>/subjects", methods=["POST"])
def add_tutor_subject(tutor_id):
    """Thêm môn dạy cho gia sư"""
    tutor = Tutor.query.get_or_404(tutor_id)
    data = request.get_json() or {}
    
    if "subject_id" not in data:
        return jsonify({"error": "subject_id là bắt buộc"}), 400
    
    subject_id = data["subject_id"]
    subject = Subject.query.get_or_404(subject_id)
    
    # Check if already exists
    existing = TutorSubject.query.filter_by(
        tutor_id=tutor_id, subject_id=subject_id
    ).first()
    
    if existing:
        return jsonify({"error": "Gia sư đã dạy môn này"}), 400
    
    # Add subject
    tutor_subject = TutorSubject(tutor_id=tutor_id, subject_id=subject_id)
    db.session.add(tutor_subject)
    db.session.commit()
    
    return jsonify({
        "message": f"Đã thêm môn {subject.name} cho gia sư {tutor.full_name}"
    }), 201
