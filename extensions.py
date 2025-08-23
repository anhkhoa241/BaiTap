# Import các extensions mà không cần khởi tọa lại và dùng chung
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

db = SQLAlchemy()        # ORM (thao tác với cơ sở dữ liệu)
bcrypt = Bcrypt()        # Hash password (mã hóa mật khẩu)
jwt = JWTManager()       # Quản lý JWT 


