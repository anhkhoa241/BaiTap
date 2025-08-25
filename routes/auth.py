from flask import request, jsonify
from extensions import db
from models import User
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from routes import api
from utils.decorators import role_required

# Đăng ký
@api.route("/auth/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    # Validate required fields
    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Thiếu email hoặc password"}), 400

    # Check email already exists
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email đã tồn tại"}), 400

    # Create new user
    user = User(
        email=data["email"],
        role=data.get("role", "customer")
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()

    return jsonify({
        "message": "Đăng ký thành công",
        "user": user.to_dict()
    }), 201

# Đăng nhập
@api.route("/auth/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Thiếu email hoặc password"}), 400

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"error": "Sai email hoặc password"}), 401

    access_token = create_access_token(identity=user.id)
    return jsonify({
        "message": "Đăng nhập thành công",
        "access_token": access_token,
        "user": user.to_dict()
    }), 200

# Lấy thông tin user hiện tại
@api.route("/auth/me", methods=["GET"])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user:
        return jsonify({"error": "User không tồn tại"}), 404

    return jsonify({
        "user": user.to_dict()
    })

# Test route protected (chỉ user đã login mới vào được)
@api.route("/auth/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    return jsonify({
        "message": "Bạn đã đăng nhập thành công!",
        "user_id": current_user_id
    })
