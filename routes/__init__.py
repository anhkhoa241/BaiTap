from flask import Blueprint

api = Blueprint("api", __name__)

# Import các route để gắn vào blueprint chính
from . import customers