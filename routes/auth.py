# routes/auth.py
from flask import request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity, get_jwt
from extensions import db
from models import User, Customer, Tutor
from routes import api
import datetime

@api.post("/auth/register")
def register():
    """
    Body JSON: { "email": "...", "password": "...", "role": "customer"|"tutor", "name": "Tên" }
    - Nếu role == customer -> tạo Customer profile + User
    - Nếu role == tutor -> tạo Tutor profile + User
    """
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    role = (data.get("role") or "customer").strip().lower()
    name = data.get("name") or ""

    # Validate cơ bản
    if not (email and password and name):
        return jsonify({"error": "email, password, name là bắt buộc"}), 400
    if role not in ("customer", "tutor", "admin"):
        return jsonify({"error": "role không hợp lệ"}), 400

    # Email đã tồn tại
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email đã tồn tại"}), 409

    # Tạo profile theo role và gắn vào User
    user = User(email=email, role=role)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()  # để user.id sẵn cho việc gán profile

    if role == "customer":
        # tạo Customer row (giả sử models.Customer tồn tại)
        cust = Customer(full_name=name, email=email)
        db.session.add(cust)
        db.session.flush()
        user.customer_id = cust.id
    elif role == "tutor":
        tutor = Tutor(full_name=name, email=email)
        db.session.add(tutor)
        db.session.flush()
        user.tutor_id = tutor.id
    # nếu admin: có thể tạo khác, ở đây bỏ qua

    db.session.commit()

    # Tạo token
    claims = {"role": user.role}
    access_token = create_access_token(identity=user.id, additional_claims=claims)

    return jsonify({"message": "Đăng ký thành công", "access_token": access_token, "user": user.to_dict()}), 201


@api.post("/auth/login")
def login():
    """
    Body JSON: { "email": "...", "password": "..." }
    """
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not (email and password):
        return jsonify({"error": "email và password là bắt buộc"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Email hoặc mật khẩu không đúng"}), 401

    claims = {"role": user.role}
    access_token = create_access_token(identity=user.id, additional_claims=claims)

    return jsonify({"access_token": access_token, "user": user.to_dict()})
