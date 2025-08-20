from flask import Blueprint

api = Blueprint("api", __name__)

# import các blueprint con
from .tutors import tutors_bp
from .students import students_bp

# đăng ký
api.register_blueprint(tutors_bp)
api.register_blueprint(students_bp)
