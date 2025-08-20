from flask import Blueprint, request, jsonify
from extensions import db
from models import Tutor, Subject, TutorSubject, User
from utils.decorators import role_required
from flask_jwt_extended import get_jwt_identity, get_jwt

# 👉 Khai báo blueprint trước
tutors_bp = Blueprint("tutors", __name__, url_prefix="/tutors")

# Public: list tutors
@tutors_bp.get("/")
def list_tutors():
    q = (request.args.get("q") or "").strip()
    subject = (request.args.get("subject") or "").strip()
    city = (request.args.get("city") or "").strip()

    query = Tutor.query
    if subject:
        query = query.join(TutorSubject).join(Subject).filter(Subject.name.ilike(f"%{subject}%"))
    if city:
        query = query.filter(Tutor.city.ilike(f"%{city}%"))

    tutors = query.limit(100).all()
    data = []
    for t in tutors:
        data.append({
            "id": t.id,
            "name": t.full_name,
            "city": t.city,
            "hourly_rate": t.hourly_rate,
            "subjects": [s.name for s in t.subjects],
            "rating_avg": t.rating_avg,
        })
    return jsonify({"tutors": data})

# Tutor cập nhật profile
@tutors_bp.post("/profile")
@role_required("tutor")
def update_tutor_profile():
    user_id = get_jwt_identity()
    user = User.query.get_or_404(user_id)
    if not user.tutor_id:
        return jsonify({"error": "User chưa có tutor profile"}), 404

    t = Tutor.query.get_or_404(user.tutor_id)
    data = request.get_json() or {}
    t.full_name = data.get("full_name", t.full_name)
    t.bio = data.get("bio", t.bio)
    if data.get("hourly_rate") is not None:
        t.hourly_rate = int(data["hourly_rate"])

    subjects_in = data.get("subjects")
    if isinstance(subjects_in, list):
        t.subjects.clear()
        for name in subjects_in:
            name = (name or "").strip()
            if not name:
                continue
            subj = Subject.query.filter(Subject.name.ilike(name)).first()
            if not subj:
                subj = Subject(code=name.upper()[:6], name=name)
                db.session.add(subj)
            t.subjects.append(subj)

    db.session.commit()
    return jsonify({"message": "Cập nhật profile thành công"})
