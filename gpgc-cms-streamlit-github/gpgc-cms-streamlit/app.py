import os
import base64
from datetime import date, datetime
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, String, Integer, Boolean, Date, DateTime, ForeignKey, Text, Float, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, InvalidHashError

APP_NAME = "GPGC Miran Shah College Management System"
ROLES = ["super_admin", "second_admin", "teacher", "student", "parent", "librarian", "employee", "hod", "hostel_warden"]
ROLE_LABELS = {
    "super_admin": "Super Admin", "second_admin": "Second Admin", "teacher": "Teacher",
    "student": "Student", "parent": "Parent", "librarian": "Librarian",
    "employee": "Employee", "hod": "Head of Department", "hostel_warden": "Hostel Warden"
}
ph = PasswordHasher()

GITHUB_LOGO_URL = "https://raw.githubusercontent.com/dawran-waxir/CMS-GPGC-Miran-Shah/main/gpgc-cms-streamlit-github/gpgc-cms-streamlit/logo.jpg"

st.set_page_config(page_title=APP_NAME, page_icon="🎓", layout="wide", initial_sidebar_state="expanded")

def get_logo_html(width="65px"):
    for local_file in ["logo.jpg", "logo.png"]:
        if os.path.exists(local_file):
            try:
                with open(local_file, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                ext = "jpeg" if local_file.endswith(".jpg") else "png"
                return f'<img src="data:image/{ext};base64,{b64}" style="width:{width}; height:auto; border-radius:50%; border:2px solid #d4af37; box-shadow:0 4px 12px rgba(0,0,0,0.22); display:inline-block; vertical-align:middle;">'
            except Exception:
                pass
    return f'<img src="{GITHUB_LOGO_URL}" style="width:{width}; height:auto; border-radius:50%; border:2px solid #d4af37; box-shadow:0 4px 12px rgba(0,0,0,0.22); display:inline-block; vertical-align:middle;">'

# UI/UX Executive Styling with Enhanced Button Hover Dynamics
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"], .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important;
    background-color: #f8fafc !important;
    color: #0f172a !important;
}

.block-container {
    padding-top: 1.2rem;
    padding-bottom: 3.5rem;
    max-width: 1380px;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}
[data-testid="stSidebar"] * {
    color: #1e293b !important;
}
[data-testid="stSidebar"] .stCaption {
    color: #64748b !important;
}

/* Hero Section */
.hero-card {
    background: linear-gradient(135deg, #4a0e11 0%, #6b1519 55%, #8c1c22 100%);
    border-radius: 20px;
    padding: 1.8rem 2.2rem;
    color: #ffffff !important;
    border-bottom: 4px solid #d4af37;
    box-shadow: 0 14px 30px rgba(107, 21, 25, 0.22);
    margin-bottom: 1.8rem;
    display: flex;
    align-items: center;
    gap: 1.5rem;
}
.hero-card h1 {
    color: #ffffff !important;
    margin: 0 !important;
    font-size: 2.1rem !important;
    font-weight: 800 !important;
    letter-spacing: -0.02em;
}
.hero-card p {
    color: #f3e8c8 !important;
    margin: 0.4rem 0 0 0 !important;
    font-size: 1rem !important;
    font-weight: 500;
}

/* Metric Cards */
div[data-testid="stMetric"] {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 16px !important;
    padding: 18px 22px !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.03) !important;
    border-top: 4px solid #6b1519 !important;
}
div[data-testid="stMetric"] label {
    color: #475569 !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {
    color: #0f172a !important;
    font-weight: 800 !important;
    font-size: 2rem !important;
}

/* Segmented Control Pills Navigation with High-Contrast Hover State */
div[data-testid="stPills"] {
    background: #ffffff !important;
    padding: 0.6rem 0.8rem !important;
    border-radius: 16px !important;
    border: 1px solid #cbd5e1 !important;
    box-shadow: 0 4px 14px rgba(0,0,0,0.03) !important;
}
div[data-testid="stPills"] button {
    border-radius: 12px !important;
    font-weight: 700 !important;
    font-size: 0.9rem !important;
    padding: 0.5rem 1.2rem !important;
    color: #1e293b !important;
    background-color: #f1f5f9 !important;
    border: 1px solid #cbd5e1 !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* Pill Hover State - Rich Crimson Tint with Gold Highlight */
div[data-testid="stPills"] button:hover {
    background-color: #fce8e9 !important;
    color: #6b1519 !important;
    border-color: #d4af37 !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 4px 12px rgba(107, 21, 25, 0.12) !important;
}

/* Selected Pill State */
div[data-testid="stPills"] button[aria-selected="true"] {
    background: linear-gradient(135deg, #4a0e11, #6b1519) !important;
    color: #ffffff !important;
    border: 1px solid #d4af37 !important;
    box-shadow: 0 4px 14px rgba(107, 21, 25, 0.3) !important;
}

/* Primary Button Styling & Hover State */
button[kind="primary"] {
    background: linear-gradient(135deg, #640505, #640505) !important;
    border: 1px solid #d4af37 !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    color: #ffffff !important;
    transition: all 0.25s ease !important;
}
button[kind="primary"]:hover {
    background: linear-gradient(135deg, #6b1519, #8c1c22) !important;
    box-shadow: 0 6px 16px rgba(107, 21, 25, 0.35) !important;
    border-color: #f3e8c8 !important;
    transform: translateY(-1px) !important;
}

/* Secondary Button Styling & Hover State */
button[kind="secondary"] {
    background-color: #ffffff !important;
    color: #1e293b !important;
    border: 1px solid #cbd5e1 !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    transition: all 0.25s ease !important;
}
button[kind="secondary"]:hover {
    background-color: #fce8e9 !important;
    color: #6b1519 !important;
    border-color: #6b1519 !important;
}

.stTextInput input, .stSelectbox select, .stTextArea textarea {
    background-color: #ffffff !important;
    color: #0f172a !important;
    border-radius: 10px !important;
    border: 1px solid #cbd5e1 !important;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 1.2rem;
    padding-bottom: 0.85rem;
    border-bottom: 2px solid #e2e8f0;
    margin-bottom: 1.5rem;
}
.section-header h2 {
    color: #6b1519 !important;
    margin: 0 !important;
    font-weight: 800 !important;
}
</style>""", unsafe_allow_html=True)

class Base(DeclarativeBase): pass

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

def df_query(statement):
    with SessionLocal() as db:
        rows = db.execute(statement).all()
        if not rows: return pd.DataFrame()
        return pd.DataFrame([dict(r._mapping) for r in rows])

def metric_row(items):
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items):
        col.metric(label, value)

def render_section_header(title, subtitle=""):
    logo_html = get_logo_html("55px")
    st.markdown(f'''
    <div class="section-header">
        <div>{logo_html}</div>
        <div>
            <h2>{title}</h2>
            {"<p style='margin:0; color:#64748b; font-weight:500; font-size:0.95rem;'>" + subtitle + "</p>" if subtitle else ""}
        </div>
    </div>
    ''', unsafe_allow_html=True)

def login_screen():
    logo_html = get_logo_html("80px")
    st.markdown(f'''
    <div class="hero-card">
        <div>{logo_html}</div>
        <div>
            <h1>{APP_NAME}</h1>
            <p>Government Post Graduate College Miran Shah · North Waziristan</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)
    
    left, right = st.columns([1.1, 1])
    with left:
        st.subheader("Academic Management Portal")
        st.write("A centralized system for academic management, student enrollment, course registration, attendance registers, library access, fees, and hostel management.")
        st.info("Sign in using credentials issued by the college administration.")
    with right:
        with st.form("login_form", clear_on_submit=False):
            st.subheader("Account Sign In")
            username = st.text_input("Username", autocomplete="username")
            password = st.text_input("Password", type="password", autocomplete="current-password")
            submit = st.form_submit_button("Sign In to Portal", type="primary", use_container_width=True)
        if submit:
            if login(username, password):
                st.rerun()
            else:
                st.error("Authentication failed. Check your username and password.")

def show_announcements(user, manage=False):
    can_manage = manage and user["role"] in ("super_admin", "second_admin", "hod")
    with SessionLocal() as db:
        stmt = select(Announcement).order_by(Announcement.created_at.desc()).limit(100)
        if not can_manage:
            stmt = select(Announcement).where(Announcement.published == True).order_by(Announcement.created_at.desc()).limit(30)
        all_rows = db.scalars(stmt).all()
        rows = [r for r in all_rows if r.audience.lower() in ("everyone", user["role"], ROLE_LABELS.get(user["role"], "").lower())]
        records = [{"id": r.id, "title": r.title, "body": r.body, "audience": r.audience,
                    "created_at": r.created_at, "published": r.published} for r in rows]
    if not records:
        st.info("No notices or announcements posted yet.")
        return
    for item in records:
        with st.expander(f"{'📌 ' if item['published'] else '📝 Draft · '}{item['title']} · {item['created_at']:%d %b %Y}"):
            st.write(item["body"])
            st.caption(f"Audience: {item['audience']} · Status: {'Published' if item['published'] else 'Draft'}")
            if can_manage:
                with st.form(f"edit_announcement_{item['id']}"):
                    new_title = st.text_input("Title", value=item["title"], key=f"ann_title_{item['id']}")
                    new_body = st.text_area("Details", value=item["body"], height=110, key=f"ann_body_{item['id']}")
                    audience_options = ["Everyone"] + ROLES
                    current_audience = item["audience"] if item["audience"] in audience_options else "Everyone"
                    new_audience = st.selectbox("Audience", audience_options,
                        index=audience_options.index(current_audience),
                        format_func=lambda r: "Everyone" if r == "Everyone" else ROLE_LABELS[r],
                        key=f"ann_audience_{item['id']}")
                    new_published = st.checkbox("Published", value=item["published"], key=f"ann_pub_{item['id']}")
                    c1, c2 = st.columns(2)
                    save = c1.form_submit_button("Save Changes", type="primary", use_container_width=True)
                    delete = c2.form_submit_button("Delete Notice", use_container_width=True)
                if save:
                    if not new_title.strip() or not new_body.strip():
                        st.error("Title and details are required.")
                    else:
                        with SessionLocal() as db:
                            row = db.get(Announcement, item["id"])
                            if row:
                                row.title = new_title.strip(); row.body = new_body.strip()
                                row.audience = new_audience; row.published = new_published
                                audit(db, user["id"], "announcement_updated", f"Announcement #{row.id}: {row.title}")
                                db.commit()
                        st.success("Announcement updated."); st.rerun()
                if delete:
                    with SessionLocal() as db:
                        row = db.get(Announcement, item["id"])
                        if row:
                            audit(db, user["id"], "announcement_deleted", f"Announcement #{row.id}: {row.title}")
                            db.delete(row); db.commit()
                    st.success("Announcement deleted."); st.rerun()

def admin_users(user):
    render_section_header("User & Role Management", "Create and manage system user credentials and role authorizations")
    with st.form("create_user_form"):
        a,b = st.columns(2)
        username = a.text_input("Username *").strip().lower()
        full_name = b.text_input("Full Name *").strip()
        email = a.text_input("Email Address").strip()
        role = b.selectbox("Role", ROLES, format_func=lambda r: ROLE_LABELS[r])
        department = a.text_input("Department / Unit", value="Administration").strip()
        password = b.text_input("Initial Password *", type="password", help="Minimum 12 characters.")
        create = st.form_submit_button("Create Account", type="primary")
    if create:
        if not username or not full_name or len(password) < 12:
            st.error("Username, full name, and minimum 12-character password are required.")
        elif role == "super_admin" and user["role"] != "super_admin":
            st.error("Only a Super Admin can create another Super Admin.")
        else:
            with SessionLocal() as db:
                if db.scalar(select(User).where(User.username == username)):
                    st.error("Username already exists.")
                else:
                    u = User(username=username, full_name=full_name, email=email, role=role, department=department, password_hash=ph.hash(password), active=True)
                    db.add(u); db.flush(); audit(db, user["id"], "user_created", f"Created {username} with role {role}"); db.commit()
                    st.success(f"Account for {full_name} ({ROLE_LABELS[role]}) created successfully.")
                    st.rerun()
    st.markdown("#### User Accounts Directory")
    statement = select(User.id, User.username, User.full_name, User.email, User.role, User.department, User.active, User.created_at).order_by(User.id.desc())
    if user["role"] != "super_admin": statement = statement.where(User.role != "super_admin")
    data = df_query(statement)
    if not data.empty:
        data["role"] = data["role"].map(ROLE_LABELS).fillna(data["role"])
        st.dataframe(data, use_container_width=True, hide_index=True)

def students_module(user):
    render_section_header("Student Directory", "Manage enrollment profiles and academic standing")
    if user["role"] in ("super_admin", "second_admin", "hod"):
        with st.expander("Register New Student Profile", expanded=False):
            with st.form("add_student"):
                c1,c2 = st.columns(2)
                student_no = c1.text_input("Student Roll No *").strip()
                name = c2.text_input("Full Name *").strip()
                program = c1.text_input("Program (e.g. BS Computer Science)").strip()
                department = c2.text_input("Department").strip()
                session = c1.text_input("Academic Session (e.g. 2026-2028)").strip()
                status = c2.selectbox("Status", ["Active", "On Leave", "Graduated", "Withdrawn"])
                save = st.form_submit_button("Save Student", type="primary")
            if save:
                if not student_no or not name: st.error("Roll number and student name required.")
                else:
                    with SessionLocal() as db:
                        if db.scalar(select(Student).where(Student.student_no == student_no)):
                            st.error("Roll number already exists.")
                        else:
                            db.add(Student(student_no=student_no, full_name=name, program=program, department=department, academic_session=session, status=status))
                            audit(db, user["id"], "student_created", f"Student {student_no}"); db.commit()
                            st.success("Student profile registered."); st.rerun()
    with SessionLocal() as db:
        q = select(Student)
        if user["role"] == "student": q = q.where(Student.user_id == user["id"])
        elif user["role"] == "parent": q = q.where(Student.parent_user_id == user["id"])
        elif user["role"] == "hod" and user["department"]: q = q.where(Student.department == user["department"])
        records = db.scalars(q.order_by(Student.full_name)).all()
        rows = [{"Roll No": x.student_no, "Name": x.full_name, "Program": x.program, "Department": x.department, "Session": x.academic_session, "Status": x.status} for x in records]
    if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else: st.info("No student records found.")

def courses_module(user):
    render_section_header("Courses & Teaching Assignments", "Academic curriculum and faculty course scheduling")
    if user["role"] in ("super_admin", "second_admin", "hod"):
        with st.expander("Create Course Entry"):
            with st.form("add_course"):
                a,b = st.columns(2)
                code = a.text_input("Course Code *").strip().upper()
                title = b.text_input("Course Title *").strip()
                dept = a.text_input("Department", value=user["department"] if user["role"] == "hod" else "").strip()
                program = b.text_input("Program").strip()
                term = a.text_input("Semester / Term").strip()
                credits = b.number_input("Credits", min_value=0, max_value=12, value=3)
                teacher_options = {}
                with SessionLocal() as db:
                    teachers = db.scalars(select(User).where(User.role == "teacher", User.active == True).order_by(User.full_name)).all()
                    teacher_options = {f"{t.full_name} ({t.username})": t.id for t in teachers}
                teacher_label = st.selectbox("Assigned Instructor", ["Unassigned"] + list(teacher_options))
                save = st.form_submit_button("Save Course", type="primary")
            if save:
                if not code or not title: st.error("Course code and title are required.")
                else:
                    with SessionLocal() as db:
                        if db.scalar(select(Course).where(Course.code == code)): st.error("Course code already exists.")
                        else:
                            db.add(Course(code=code, title=title, department=dept, program=program, term=term, credits=int(credits), teacher_user_id=teacher_options.get(teacher_label)))
                            audit(db, user["id"], "course_created", code); db.commit(); st.success("Course entry saved."); st.rerun()
    with SessionLocal() as db:
        q = select(Course, User.full_name).outerjoin(User, Course.teacher_user_id == User.id)
        if user["role"] == "teacher": q = q.where(Course.teacher_user_id == user["id"])
        rows = db.execute(q.order_by(Course.code)).all()
        data = [{"Code": c.code, "Title": c.title, "Department": c.department, "Program": c.program, "Term": c.term, "Credits": c.credits, "Instructor": teacher or "Unassigned"} for c,teacher in rows]
    if data: st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

def attendance_module(user):
    render_section_header("Attendance Register", "Class attendance tracking and status logs")
    if user["role"] in ("teacher", "super_admin", "second_admin", "hod"):
        with SessionLocal() as db:
            cq = select(Course)
            if user["role"] == "teacher": cq = cq.where(Course.teacher_user_id == user["id"])
            courses = db.scalars(cq.order_by(Course.code)).all()
            students = db.scalars(select(Student).where(Student.status == "Active").order_by(Student.full_name)).all()
        if courses and students:
            course_map = {f"{c.code} — {c.title}": c.id for c in courses}
            student_map = {f"{s.student_no} — {s.full_name}": s.id for s in students}
            with st.form("attendance_form"):
                selected_course = st.selectbox("Course", list(course_map))
                selected_student = st.selectbox("Student", list(student_map))
                att_date = st.date_input("Date", value=date.today())
                status = st.selectbox("Status", ["Present", "Absent", "Late", "Excused"])
                save = st.form_submit_button("Record Attendance", type="primary")
            if save:
                with SessionLocal() as db:
                    db.add(Attendance(student_id=student_map[selected_student], course_id=course_map[selected_course], attendance_date=att_date, status=status, recorded_by=user["id"]))
                    audit(db, user["id"], "attendance_recorded", f"{selected_student}, {att_date}"); db.commit(); st.success("Attendance entry saved."); st.rerun()
    with SessionLocal() as db:
        q = select(Attendance.attendance_date, Student.student_no, Student.full_name, Course.code, Course.title, Attendance.status).join(Student, Attendance.student_id == Student.id).join(Course, Attendance.course_id == Course.id).order_by(Attendance.attendance_date.desc()).limit(300)
        rows = db.execute(q).all()
        data = [{"Date": d, "Roll No": no, "Student": name, "Course": code, "Title": title, "Status": status} for d,no,name,code,title,status in rows]
    if data: st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

def library_module(user):
    render_section_header("Library Catalogue", "Book inventory and availability catalog")
    if user["role"] in ("librarian", "super_admin", "second_admin"):
        with st.expander("Add Catalogue Entry"):
            with st.form("add_book"):
                a,b = st.columns(2)
                accession = a.text_input("Accession No *").strip()
                title = b.text_input("Title *").strip()
                author = a.text_input("Author").strip()
                category = b.text_input("Category").strip()
                copies = a.number_input("Copies", min_value=1, value=1)
                save = st.form_submit_button("Add Entry", type="primary")
            if save:
                if not accession or not title: st.error("Accession number and title are required.")
                else:
                    with SessionLocal() as db:
                        db.add(Book(accession_no=accession, title=title, author=author, category=category, total_copies=int(copies), available_copies=int(copies)))
                        audit(db, user["id"], "book_created", accession); db.commit(); st.success("Book added to catalog."); st.rerun()
    with SessionLocal() as db:
        books = db.scalars(select(Book).order_by(Book.title)).all()
        data = [{"Accession": b.accession_no, "Title": b.title, "Author": b.author, "Category": b.category, "Total": b.total_copies, "Available": b.available_copies} for b in books]
    if data: st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

def hostel_module(user):
    render_section_header("Hostel Facilities", "Room allocations and occupancy tracking")
    if user["role"] in ("hostel_warden", "super_admin", "second_admin"):
        with st.expander("Add Hostel Room"):
            with st.form("add_room"):
                a,b = st.columns(2)
                hostel = a.text_input("Hostel Name *").strip()
                room = b.text_input("Room No *").strip()
                capacity = a.number_input("Capacity", min_value=1, value=2)
                occupied = b.number_input("Occupied Beds", min_value=0, value=0)
                save = st.form_submit_button("Save Room", type="primary")
            if save:
                if not hostel or not room: st.error("Hostel name and room number required.")
                else:
                    with SessionLocal() as db:
                        db.add(HostelRoom(hostel_name=hostel, room_no=room, capacity=int(capacity), occupied=int(occupied)))
                        audit(db, user["id"], "hostel_room_created", f"{hostel}/{room}"); db.commit(); st.success("Room registered."); st.rerun()
    with SessionLocal() as db:
        rooms = db.scalars(select(HostelRoom).order_by(HostelRoom.hostel_name)).all()
        data = [{"Hostel": r.hostel_name, "Room": r.room_no, "Capacity": r.capacity, "Occupied": r.occupied, "Vacancies": r.capacity-r.occupied, "Status": r.status} for r in rooms]
    if data: st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

def fees_module(user):
    render_section_header("Fee Records", "Student tuition ledgers and fee status")
    if user["role"] in ("super_admin", "second_admin"):
        with st.expander("Issue Fee Record"):
            with SessionLocal() as db:
                students = db.scalars(select(Student).order_by(Student.full_name)).all()
            if students:
                smap = {f"{s.student_no} — {s.full_name}": s.id for s in students}
                with st.form("fee_form"):
                    student = st.selectbox("Student", list(smap))
                    desc = st.text_input("Description", value="Semester Tuition Fee")
                    amount = st.number_input("Total Amount (PKR)", min_value=0.0)
                    paid = st.number_input("Paid Amount (PKR)", min_value=0.0)
                    due = st.date_input("Due Date", value=date.today())
                    save = st.form_submit_button("Record Fee", type="primary")
                if save:
                    status = "Paid" if paid >= amount else ("Partial" if paid > 0 else "Unpaid")
                    with SessionLocal() as db:
                        db.add(FeeRecord(student_id=smap[student], description=desc, amount=amount, paid_amount=paid, due_date=due, status=status))
                        audit(db, user["id"], "fee_record_created", f"{student}"); db.commit(); st.success("Record saved."); st.rerun()
    with SessionLocal() as db:
        q = select(FeeRecord, Student.student_no, Student.full_name).join(Student, FeeRecord.student_id == Student.id).order_by(FeeRecord.created_at.desc())
        rows = db.execute(q).all()
        data = [{"Roll No": no, "Student": name, "Description": f.description, "Amount": f.amount, "Paid": f.paid_amount, "Balance": f.amount-f.paid_amount, "Status": f.status} for f,no,name in rows]
    if data: st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

def ai_assistant(user):
    render_section_header("AI Academic Assistant", "Powered by Groq LLM integration")
    key = get_setting("GROQ_API_KEY")
    if not key:
        st.warning("Configure `GROQ_API_KEY` in Streamlit secrets to activate AI query capabilities.")
        return
    prompt = st.text_area("Your Query", placeholder="Ask any study, procedural, or academic question...", height=110)
    if st.button("Ask AI Assistant", type="primary"):
        if not prompt.strip(): st.error("Please enter a question.")
        else:
            try:
                from groq import Groq
                client = Groq(api_key=key)
                model = get_setting("GROQ_MODEL", "llama-3.3-70b-versatile")
                with st.spinner("Analyzing request..."):
                    result = client.chat.completions.create(model=model, messages=[{"role":"system","content":"You are a helpful educational assistant for Government Post Graduate College Miran Shah."},{"role":"user","content":prompt}], temperature=0.4, max_tokens=1000)
                st.markdown(result.choices[0].message.content)
            except Exception as e:
                st.error(f"Error: {str(e)[:200]}")

def dashboard(user):
    role = user["role"]
    logo_html = get_logo_html("72px")
    
    st.markdown(f'''
    <div class="hero-card">
        <div>{logo_html}</div>
        <div>
            <h1>Government Post Graduate College Miran Shah</h1>
            <p>North Waziristan · Academic Management Portal ({ROLE_LABELS.get(role, role)})</p>
        </div>
    </div>
    ''', unsafe_allow_html=True)

    with SessionLocal() as db:
        n_students = db.scalar(select(func.count()).select_from(Student)) or 0
        n_users = db.scalar(select(func.count()).select_from(User).where(User.active == True)) or 0
        n_courses = db.scalar(select(func.count()).select_from(Course)) or 0
        n_ann = db.scalar(select(func.count()).select_from(Announcement).where(Announcement.published == True)) or 0

    metric_row([("Active Accounts", n_users), ("Total Students", n_students), ("Courses Offered", n_courses), ("Active Notices", n_ann)])
    st.write("")

    allowed = {
        "super_admin": ["Overview", "Students", "Courses", "Attendance", "Fees", "Library", "Hostel", "Announcements", "User Management", "AI Assistant", "Audit Log"],
        "second_admin": ["Overview", "Students", "Courses", "Attendance", "Fees", "Library", "Hostel", "Announcements", "User Management", "AI Assistant"],
        "teacher": ["Overview", "Students", "Courses", "Attendance", "Announcements", "AI Assistant"],
        "student": ["Overview", "Students", "Courses", "Attendance", "Fees", "Library", "Announcements", "AI Assistant"],
        "parent": ["Overview", "Students", "Attendance", "Fees", "Announcements", "AI Assistant"],
        "librarian": ["Overview", "Library", "Announcements", "AI Assistant"],
        "employee": ["Overview", "Announcements", "AI Assistant"],
        "hod": ["Overview", "Students", "Courses", "Attendance", "Announcements", "AI Assistant"],
        "hostel_warden": ["Overview", "Hostel", "Announcements", "AI Assistant"]
    }
    available = allowed.get(role, ["Overview", "Announcements"])

    state_key = f"active_module_{role}"
    if state_key not in st.session_state or st.session_state[state_key] not in available:
        st.session_state[state_key] = "Overview"

    selected_module = st.pills(
        label="Portal Navigation",
        options=available,
        default=st.session_state[state_key],
        key=f"pills_nav_{role}",
        label_visibility="collapsed"
    )
    if selected_module:
        st.session_state[state_key] = selected_module

    st.markdown("<hr style='margin-top:0.6rem; margin-bottom:1.5rem; border-color:#cbd5e1;'>", unsafe_allow_html=True)

    if selected_module == "Overview":
        render_section_header("Overview & Notices", f"Welcome back, {user['full_name']}")
        show_announcements(user, manage=role in ("super_admin", "second_admin", "hod"))
    elif selected_module == "Students": students_module(user)
    elif selected_module == "Courses": courses_module(user)
    elif selected_module == "Attendance": attendance_module(user)
    elif selected_module == "Fees": fees_module(user)
    elif selected_module == "Library": library_module(user)
    elif selected_module == "Hostel": hostel_module(user)
    elif selected_module == "Announcements": show_announcements(user, manage=role in ("super_admin", "second_admin", "hod"))
    elif selected_module == "User Management": admin_users(user)
    elif selected_module == "AI Assistant": ai_assistant(user)
    elif selected_module == "Audit Log":
        render_section_header("System Audit Log", "Security events and user system logs")
        if role != "super_admin": st.error("Unauthorized.")
        else:
            with SessionLocal() as db:
                rows = db.execute(select(AuditLog.created_at, User.username, AuditLog.action, AuditLog.details).outerjoin(User, AuditLog.user_id == User.id).order_by(AuditLog.created_at.desc()).limit(250)).all()
                data = [{"Time": t, "User": u or "system", "Action": a, "Details": d} for t,u,a,d in rows]
            st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)

def main():
    user = current_user()
    if not user:
        login_screen()
        return
    with st.sidebar:
        logo_html = get_logo_html("85px")
        st.markdown(f'<div style="text-align:center; margin-bottom:0.75rem;">{logo_html}</div>', unsafe_allow_html=True)
        st.markdown(f"<h3 style='margin:0; text-align:center; color:#6b1519; font-weight:800;'>{user['full_name']}</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center; color:#475569; font-size:0.88rem; font-weight:700;'>{ROLE_LABELS.get(user['role'], user['role'])}</p>", unsafe_allow_html=True)
        if user["department"]:
            st.markdown(f"<p style='text-align:center; color:#64748b; font-size:0.82rem;'>{user['department']}</p>", unsafe_allow_html=True)
        st.divider()
        if st.button("Sign Out", use_container_width=True):
            with SessionLocal() as db:
                audit(db, user["id"], "logout", "User logged out"); db.commit()
            st.session_state.clear(); st.rerun()
        st.markdown("---")
        st.caption("GPGC Miran Shah · North Waziristan")
    dashboard(user)

if __name__ == "__main__":
    main()
