# API cho Customers
from flask import request, jsonify
from extensions import db
from models import Customer, User
from routes import api

# Lấy danh sách customers
@api.route("/customers", methods=["GET"])
def get_customers():
    """Lấy tất cả customers"""
    customers = Customer.query.all()
    
    # Chuyển thành list để trả về JSON
    result = []
    for customer in customers:
        result.append({
            "id": customer.id,
            "full_name": customer.full_name,
            "email": customer.email,
            "phone": customer.phone,
            "address": customer.address
        })
    
    return jsonify(result)

# Tạo customer mới
@api.route("/customers", methods=["POST"])
def create_customer():
    """Tạo customer mới"""
    # Lấy dữ liệu từ request
    data = request.get_json()
    
    # Kiểm tra dữ liệu bắt buộc
    if not data.get("full_name"):
        return jsonify({"error": "Thiếu tên khách hàng"}), 400
    
    if not data.get("email"):
        return jsonify({"error": "Thiếu email"}), 400
    
    # Kiểm tra email đã tồn tại chưa
    existing_customer = Customer.query.filter_by(email=data["email"]).first()
    if existing_customer:
        return jsonify({"error": "Email đã được sử dụng"}), 400
    
    # Tạo customer mới
    customer = Customer(
        full_name=data["full_name"],
        email=data["email"],
        phone=data.get("phone", ""),  # Không bắt buộc
        address=data.get("address", "")  # Không bắt buộc
    )
    
    # Lưu vào database
    db.session.add(customer)
    db.session.commit()
    
    return jsonify({
        "message": "Tạo khách hàng thành công",
        "customer": {
            "id": customer.id,
            "full_name": customer.full_name,
            "email": customer.email
        }
    }), 201

# Lấy thông tin 1 customer
@api.route("/customers/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    """Lấy thông tin chi tiết 1 customer"""
    customer = Customer.query.get(customer_id)
    
    # Kiểm tra customer có tồn tại không
    if not customer:
        return jsonify({"error": "Không tìm thấy khách hàng"}), 404
    
    return jsonify({
        "id": customer.id,
        "full_name": customer.full_name,
        "email": customer.email,
        "phone": customer.phone,
        "address": customer.address,
        "created_at": customer.created_at.strftime("%Y-%m-%d %H:%M:%S") if customer.created_at else None
    })
