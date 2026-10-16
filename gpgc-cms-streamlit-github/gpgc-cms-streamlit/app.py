class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(160))
    email: Mapped[str] = mapped_column(String(180), default="")
    role: Mapped[str] = mapped_column(String(30), index=True)
    department: Mapped[str] = mapped_column(String(120), default="")
    password_hash: Mapped[str] = mapped_column(String(255))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Student(Base):
    __tablename__ = "students"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_no: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(160))
    program: Mapped[str] = mapped_column(String(120), default="")
    department: Mapped[str] = mapped_column(String(120), default="")
    academic_session: Mapped[str] = mapped_column(String(60), default="")
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    parent_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="Active")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Course(Base):
    __tablename__ = "courses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    code: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(180))
    department: Mapped[str] = mapped_column(String(120), default="")
    program: Mapped[str] = mapped_column(String(120), default="")
    teacher_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    term: Mapped[str] = mapped_column(String(60), default="")
    credits: Mapped[int] = mapped_column(Integer, default=3)

class Attendance(Base):
    __tablename__ = "attendance"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    course_id: Mapped[int] = mapped_column(ForeignKey("courses.id"), index=True)
    attendance_date: Mapped[date] = mapped_column(Date, default=date.today)
    status: Mapped[str] = mapped_column(String(20), default="Present")
    recorded_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Announcement(Base):
    __tablename__ = "announcements"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(180))
    body: Mapped[str] = mapped_column(Text)
    audience: Mapped[str] = mapped_column(String(40), default="Everyone")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    published: Mapped[bool] = mapped_column(Boolean, default=True)

class Book(Base):
    __tablename__ = "books"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    accession_no: Mapped[str] = mapped_column(String(60), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(200))
    author: Mapped[str] = mapped_column(String(160), default="")
    category: Mapped[str] = mapped_column(String(100), default="")
    total_copies: Mapped[int] = mapped_column(Integer, default=1)
    available_copies: Mapped[int] = mapped_column(Integer, default=1)

class HostelRoom(Base):
    __tablename__ = "hostel_rooms"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hostel_name: Mapped[str] = mapped_column(String(120))
    room_no: Mapped[str] = mapped_column(String(40))
    capacity: Mapped[int] = mapped_column(Integer, default=1)
    occupied: Mapped[int] = mapped_column(Integer, default=0)
    status: Mapped[str] = mapped_column(String(30), default="Available")

class FeeRecord(Base):
    __tablename__ = "fee_records"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), index=True)
    description: Mapped[str] = mapped_column(String(160))
    amount: Mapped[float] = mapped_column(Float, default=0)
    paid_amount: Mapped[float] = mapped_column(Float, default=0)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="Unpaid")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(120))
    details: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


def get_setting(key, default=None):
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except Exception:
        return os.getenv(key, default)

@st.cache_resource
def database_resources():
    url = get_setting("DATABASE_URL", "sqlite:///gpgc_cms.db")
    # Most managed PostgreSQL providers provide postgres://; SQLAlchemy expects postgresql://.
    if url.startswith("postgres://"):
        url = "postgresql+psycopg://" + url[len("postgres://"):]
    elif url.startswith("postgresql://") and "+psycopg" not in url:
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    kwargs = {"pool_pre_ping": True}
    if url.startswith("sqlite"):
        kwargs["connect_args"] = {"check_same_thread": False}
    engine = create_engine(url, **kwargs)
    Base.metadata.create_all(engine)
    return engine, sessionmaker(bind=engine, expire_on_commit=False)

engine, SessionLocal = database_resources()

def audit(db, user_id, action, details=""):
    db.add(AuditLog(user_id=user_id, action=action, details=details[:4000]))

def bootstrap_admin():
    username = get_setting("BOOTSTRAP_ADMIN_USERNAME")
    password = get_setting("BOOTSTRAP_ADMIN_PASSWORD")
    if not username or not password:
        return
    with SessionLocal() as db:
        existing = db.scalar(select(User).where(User.username == username.strip().lower()))
        if not existing:
            user = User(username=username.strip().lower(), full_name="System Super Administrator", email="", role="super_admin", department="Administration", password_hash=ph.hash(password), active=True)
            db.add(user); db.flush(); audit(db, user.id, "bootstrap_admin_created", "Initial administrator created from deployment secrets")
            db.commit()

bootstrap_admin()

def current_user():
    uid = st.session_state.get("user_id")
    if not uid: return None
    with SessionLocal() as db:
        user = db.get(User, uid)
        if not user or not user.active:
            st.session_state.clear(); return None
        return {"id": user.id, "username": user.username, "full_name": user.full_name, "role": user.role, "department": user.department, "email": user.email}

def login(username, password):
    with SessionLocal() as db:
        user = db.scalar(select(User).where(User.username == username.strip().lower()))
        if not user or not user.active:
            return False
        try:
            valid = ph.verify(user.password_hash, password)
        except (VerifyMismatchError, InvalidHashError):
            valid = False
        if not valid: return False
        if ph.check_needs_rehash(user.password_hash): user.password_hash = ph.hash(password)
        audit(db, user.id, "login", "Successful login")
        db.commit()
        st.session_state.user_id = user.id
        return True
