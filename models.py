# Định nghĩa các bảng trong database.
# Mỗi class là một bảng, mỗi thuộc tính là một cột.
from datetime import datetime, time
import enum
from extensions import db, bcrypt  # bcrypt từ extensions

# =========================
#  ENUMS (kiểu liệt kê)
# =========================

class Gender(enum.Enum):
    male = "male"
    female = "female"
    other = "other"

class BookingStatus(enum.Enum):
    pending = "pending"       # khách/hs vừa đặt, chờ gia sư nhận
    accepted = "accepted"     # gia sư nhận
    rejected = "rejected"     # gia sư từ chối
    canceled = "canceled"     # hủy (khách/hs hoặc hệ thống)
    completed = "completed"   # buổi học xong

# =========================
#  Mixin chung
# =========================

class TimestampMixin:
    # thời điểm tạo
    created_at = db.Column(db.DateTime, server_default=db.func.now(), nullable=False)
    # thời điểm cập nhật
    updated_at = db.Column(
        db.DateTime,
        server_default=db.func.now(),
        onupdate=db.func.now(),
        nullable=False,
    )

# =========================
#  KHÁCH (người đặt dịch vụ, thường là phụ huynh)
# =========================

class Customer(TimestampMixin, db.Model):
    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)                       # PK
    full_name = db.Column(db.String(120), nullable=False)              # tên hiển thị
    email = db.Column(db.String(120), unique=True, nullable=False)     # email duy nhất
    phone = db.Column(db.String(20), unique=True, nullable=True)       # sđt (có thể trùng null)
    address = db.Column(db.String(255), nullable=True)                 # địa chỉ

    # 1 khách có nhiều học viên
    students = db.relationship("Student", back_populates="customer", cascade="all, delete-orphan")

     # Thêm quan hệ tới User
    user = db.relationship("User", back_populates="customer", uselist=False)  

    def __repr__(self):
        return f"<Customer {self.full_name}>"

# =========================
#  HỌC VIÊN (profile của con)
# =========================

class Student(TimestampMixin, db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    birth_year = db.Column(db.Integer, nullable=True)                  # năm sinh
    grade = db.Column(db.String(20), nullable=True)                    # khối/lớp (VD: "Lớp 8")
    gender = db.Column(db.Enum(Gender, native_enum=False), nullable=True)  # Enum lưu text

    # quan hệ ngược: 1 khách -> N học viên
    customer = db.relationship("Customer", back_populates="students")

    # 1 học viên có nhiều booking
    bookings = db.relationship("Booking", back_populates="student", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Student {self.full_name}>"

# =========================
#  MÔN HỌC
# =========================

class Subject(TimestampMixin, db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)       # mã ngắn (VD: MATH)
    name = db.Column(db.String(120), unique=True, nullable=False)      # tên môn (VD: Toán)

    # N-N với Tutor qua bảng phụ
    tutors = db.relationship("Tutor", secondary="tutor_subjects", back_populates="subjects")

    def __repr__(self):
        return f"<Subject {self.code}>"

# =========================
#  GIA SƯ
# =========================

class Tutor(TimestampMixin, db.Model):
    __tablename__ = "tutors"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), unique=True, nullable=True)

    years_experience = db.Column(db.Integer, default=0, nullable=False)   # số năm kinh nghiệm
    hourly_rate = db.Column(db.Integer, nullable=True)                     # đơn giá/giờ (đồng)
    bio = db.Column(db.Text, nullable=True)                                # mô tả bản thân

    rating_avg = db.Column(db.Float, default=0, nullable=False)            # điểm TB
    rating_count = db.Column(db.Integer, default=0, nullable=False)        # số lượt đánh giá

    city = db.Column(db.String(100), nullable=True)                        # khu vực dạy

    # N-N môn học
    subjects = db.relationship("Subject", secondary="tutor_subjects", back_populates="tutors")

    # 1-N slot rảnh
    availability_slots = db.relationship("AvailabilitySlot", back_populates="tutor", cascade="all, delete-orphan")

    # 1-N booking
    bookings = db.relationship("Booking", back_populates="tutor")

    # Thêm quan hệ tới User
    user = db.relationship("User", back_populates="tutor", uselist=False)

    def __repr__(self):
        return f"<Tutor {self.full_name}>"

# =========================
#  BẢNG PHỤ: TUTOR - SUBJECT (N-N)
# =========================

class TutorSubject(db.Model):
    __tablename__ = "tutor_subjects"

    tutor_id = db.Column(db.Integer, db.ForeignKey("tutors.id", ondelete="CASCADE"), primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id", ondelete="CASCADE"), primary_key=True)

    # composite unique là PK luôn rồi, không cần thêm UniqueConstraint nữa

# =========================
#  LỊCH RẢNH CỦA GIA SƯ
# =========================

class AvailabilitySlot(TimestampMixin, db.Model):
    __tablename__ = "availability_slots"

    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey("tutors.id", ondelete="CASCADE"), nullable=False)

    # thứ trong tuần: 0=Mon ... 6=Sun (int nhỏ gọn)
    weekday = db.Column(db.SmallInteger, nullable=False)

    # giờ bắt đầu/kết thúc trong ngày (HH:MM:SS)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)

    tutor = db.relationship("Tutor", back_populates="availability_slots")

    # tránh trùng slot cùng thứ+giờ cho 1 tutor
    __table_args__ = (
        db.UniqueConstraint("tutor_id", "weekday", "start_time", name="uq_tutor_day_start"),
        db.CheckConstraint("weekday BETWEEN 0 AND 6", name="ck_weekday_range"),
        db.CheckConstraint("start_time < end_time", name="ck_time_order"),
        db.Index("ix_availability_tutor_weekday", "tutor_id", "weekday"),
    )

# =========================
#  BOOKING / ĐĂNG KÝ (Student đặt gia sư)
# =========================

class Booking(TimestampMixin, db.Model):
    __tablename__ = "bookings"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(db.Integer, db.ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey("tutors.id", ondelete="CASCADE"), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey("subjects.id", ondelete="RESTRICT"), nullable=False)

    # thời điểm dự kiến buổi học đầu tiên (hoặc duy nhất)
    start_at = db.Column(db.DateTime, nullable=True)

    # số giờ đặt (VD: 1.5 giờ)
    hours = db.Column(db.Numeric(3, 1), nullable=True)

    # tổng tiền (đồng) cho booking này (hours * hourly_rate, có thể thay đổi do khuyến mãi)
    total_price = db.Column(db.Integer, nullable=True)

    # trạng thái
    status = db.Column(db.Enum(BookingStatus, native_enum=False), default=BookingStatus.pending, nullable=False)

    note = db.Column(db.String(500), nullable=True)

    # quan hệ
    student = db.relationship("Student", back_populates="bookings")
    tutor = db.relationship("Tutor", back_populates="bookings")
    subject = db.relationship("Subject")

    feedback = db.relationship("Feedback", back_populates="booking", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        db.Index("ix_booking_status", "status"),
    )

# =========================
#  ĐÁNH GIÁ SAU KHI HỌC
# =========================

class Feedback(TimestampMixin, db.Model):
    __tablename__ = "feedbacks"

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey("bookings.id", ondelete="CASCADE"), unique=True, nullable=False)

    rating = db.Column(db.Integer, nullable=False)    # 1..5
    comment = db.Column(db.String(1000), nullable=True)

    booking = db.relationship("Booking", back_populates="feedback")

    __table_args__ = (
        db.CheckConstraint("rating BETWEEN 1 AND 5", name="ck_rating_1_5"),
        db.Index("ix_feedback_rating", "rating"),
    )



# Mới thêm vào
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)  # email dùng để login
    password_hash = db.Column(db.String(128), nullable=False)       # hash mật khẩu
    
    # role: xác định quyền hạn của user
    role = db.Column(
        db.String(20), 
        nullable=False, 
        default="customer"
    )  # customer|tutor|admin

    # Nếu muốn gắn vào customer/tutor profile (nếu đã có bảng customers/tutors)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id", ondelete="SET NULL"), nullable=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey("tutors.id", ondelete="SET NULL"), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

     # Quan hệ ngược để dễ query
    customer = db.relationship("Customer", back_populates="user", uselist=False)
    tutor = db.relationship("Tutor", back_populates="user", uselist=False)


    # helper methods
    def set_password(self, raw_password: str) -> None:
        """Hash và lưu password (dùng bcrypt)."""
        # bcrypt.generate_password_hash trả bytes, nên decode -> str lưu vào DB
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        """So sánh mật khẩu raw với hash lưu DB."""
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    def to_dict(self):
        return {"id": self.id, "email": self.email, "role": self.role, "customer_id": self.customer_id, "tutor_id": self.tutor_id}

