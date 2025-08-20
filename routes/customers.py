from flask import request, jsonify
from routes import api
from extensions import db
from models import Customer

@api.route("/customers", methods=["GET"])
def get_customers():
    customers = Customer.query.all()
    return jsonify([{"id": c.id, "name": c.name, "email": c.email} for c in customers])

@api.route("/customers", methods=["POST"])
def create_customer():
    data = request.get_json()
    customer = Customer(
        name=data["name"],
        email=data["email"],
        phone=data["phone"]
    )
    db.session.add(customer)
    db.session.commit()
    return jsonify({"message": "Customer created!"}), 201
