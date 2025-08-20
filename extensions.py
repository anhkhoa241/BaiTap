# from flask_sqlalchemy import SQLAlchemy

# db = SQLAlchemy()


# extensions.py
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

# Khởi tạo các extension ở trạng thái *chưa* bind vào app.
# Sau này gọi db.init_app(app), bcrypt.init_app(app), jwt.init_app(app)
db = SQLAlchemy()        # ORM
bcrypt = Bcrypt()        # Hash password
jwt = JWTManager()       # Quản lý JWT
