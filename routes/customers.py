from flask import request, jsonify
from extensions import db
from models import Customer
from routes import api

@api.route("/customers", methods=["GET"])
def get_customers():
    customers = Customer.query.all()
    print("Fetching all customers:", customers)
    return jsonify([
        {
            "id": c.id,
            "full_name": c.full_name,
            "email": c.email,
            "phone": c.phone       
        } for c in customers
    ])

@api.route("/customers", methods=["POST"])
def create_customer():
    data = request.get_json() or {}
    if not all(k in data for k in ("full_name", "email")):
        return jsonify({"error": "full_name, email là bắt buộc"}), 400
    customer = Customer(
        full_name=data["full_name"],
        email=data["email"],
        phone=data.get("phone")
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify({
        "id": customer.id,
        "full_name": customer.full_name,
        "email": customer.email,
        "phone": customer.phone
    }), 201