from flask import Flask, Blueprint, request, jsonify
from dotenv import load_dotenv
from extensions import db, bcrypt, jwt
from flask_migrate import Migrate
from models import Customer, Tutor
import os

# 1. Nạp biến môi trường
load_dotenv()

# 2. Khởi tạo Flask app
app = Flask(__name__)

# 3. Config DB
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")

# 4. Init extensions
db.init_app(app)
bcrypt.init_app(app)
jwt.init_app(app)
migrate = Migrate(app, db)

# 5. Register blueprint
from routes import api as api_bp
app.register_blueprint(api_bp, url_prefix="/api")
# app.register_blueprint(api_bp)

# 6. Import models (sau khi db đã init)
import models

# Route test
@app.route("/")
def home():
    return "Flask app đang chạy ngon lành 🚀"



if __name__ == "__main__":
    app.run(debug=True)
