import os
from datetime import date, datetime
import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, String, Integer, Boolean, Date, DateTime, ForeignKey, Text, Float, select, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship
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

st.set_page_config(page_title=APP_NAME, page_icon="🎓", layout="wide", initial_sidebar_state="expanded")
st.markdown("""<style>
:root { color-scheme: light; }
.block-container {padding-top: 1.4rem; padding-bottom: 3rem; max-width: 1400px;}
.hero {padding:1.25rem 1.5rem; border-radius:16px; background:linear-gradient(120deg,#12345a,#167d91); color:white; margin-bottom:1rem;}
.hero h1 {color:white; margin:0;} .hero p {margin:.35rem 0 0 0; opacity:.9;}
div[data-testid="stMetric"] {border:1px solid #dce3ea; padding:14px; border-radius:12px; background:#fff;}
.small-muted {color:#637381; font-size:.9rem;}
header[data-testid="stHeader"] {background:transparent;}
[data-testid="stSidebar"] {border-right:1px solid rgba(128,128,128,.25);}
button[kind="secondary"] {border-radius:10px;}
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

def df_query(statement):
    with SessionLocal() as db:
        rows = db.execute(statement).all()
        if not rows: return pd.DataFrame()
        return pd.DataFrame([dict(r._mapping) for r in rows])

def metric_row(items):
    cols = st.columns(len(items))
    for col, (label, value) in zip(cols, items): col.metric(label, value)

def add_announcement(user, title, body, audience):
    with SessionLocal() as db:
        db.add(Announcement(title=title.strip(), body=body.strip(), audience=audience, created_by=user["id"], published=True))
        audit(db, user["id"], "announcement_created", title.strip())
        db.commit()

def login_screen():
    st.markdown(f'<div class="hero"><h1>🎓 {APP_NAME}</h1><p>Government Post Graduate College Miran Shah · North Waziristan</p></div>', unsafe_allow_html=True)
    left, right = st.columns([1.1, 1])
    with left:
        st.subheader("Welcome to the college portal")
        st.write("A centralized workspace for academic records, attendance, notices, library, fees and hostel administration.")
        st.info("Sign in using the username and password provided by the college administrator. Public self-registration is disabled.")
        st.caption("For security, do not use a shared or public computer to save your password.")
    with right:
        with st.form("login_form", clear_on_submit=False):
            st.subheader("Secure login")
            username = st.text_input("Username", autocomplete="username")
            password = st.text_input("Password", type="password", autocomplete="current-password")
            submit = st.form_submit_button("Sign in", type="primary", use_container_width=True)
        if submit:
            if login(username, password):
                st.rerun()
            else:
                st.error("Login failed. Check your username/password or contact the administrator.")

def show_announcements(user, manage=False):
    """Display announcements; authorized staff can edit or delete them."""
    st.subheader("College announcements")
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
        st.info("No announcements have been published yet.")
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
                    save = c1.form_submit_button("Save changes", type="primary", use_container_width=True)
                    delete = c2.form_submit_button("Delete announcement", use_container_width=True)
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
    st.subheader("User and role management")
    st.caption("Create accounts only for verified college members. Use unique usernames and strong temporary passwords; users should change temporary passwords when that workflow is enabled.")
    with st.form("create_user_form"):
        a,b = st.columns(2)
        username = a.text_input("Username *").strip().lower()
        full_name = b.text_input("Full name *").strip()
        email = a.text_input("Email (optional)").strip()
        role = b.selectbox("Role", ROLES, format_func=lambda r: ROLE_LABELS[r])
        department = a.text_input("Department / unit", value="Administration").strip()
        password = b.text_input("Initial password *", type="password", help="Use at least 12 characters.")
        create = st.form_submit_button("Create user", type="primary")
    if create:
        if not username or not full_name or len(password) < 12:
            st.error("Username, full name and a password of at least 12 characters are required.")
        elif role == "super_admin" and user["role"] != "super_admin":
            st.error("Only a Super Admin can create another Super Admin.")
        else:
            with SessionLocal() as db:
                if db.scalar(select(User).where(User.username == username)):
                    st.error("That username already exists.")
                else:
                    u = User(username=username, full_name=full_name, email=email, role=role, department=department, password_hash=ph.hash(password), active=True)
                    db.add(u); db.flush(); audit(db, user["id"], "user_created", f"Created {username} with role {role}"); db.commit()
                    st.success(f"Created account for {full_name} ({ROLE_LABELS[role]}).")
                    st.rerun()
    st.markdown("#### Existing accounts")
    statement = select(User.id, User.username, User.full_name, User.email, User.role, User.department, User.active, User.created_at).order_by(User.id.desc())
    if user["role"] != "super_admin": statement = statement.where(User.role != "super_admin")
    data = df_query(statement)
    if data.empty: st.info("No users yet.")
    else:
        data["role"] = data["role"].map(ROLE_LABELS).fillna(data["role"])
        st.dataframe(data, use_container_width=True, hide_index=True)
        if user["role"] == "super_admin":
            st.markdown("#### Activate / deactivate account")
            choices = {f'{r.username} — {r.full_name} (ID {r.id})': int(r.id) for r in data.itertuples() if int(r.id) != user["id"]}
            if choices:
                selected_label = st.selectbox("Choose account", list(choices))
                if st.button("Toggle active status"):
                    with SessionLocal() as db:
                        target = db.get(User, choices[selected_label])
                        target.active = not target.active
                        audit(db, user["id"], "user_status_changed", f"User {target.username} active={target.active}")
                        db.commit()
                    st.success("Account status updated."); st.rerun()

def students_module(user):
    st.subheader("Student records")
    if user["role"] in ("super_admin", "second_admin", "hod"):
        with st.expander("Add student", expanded=False):
            with st.form("add_student"):
                c1,c2 = st.columns(2)
                student_no = c1.text_input("Student / roll number *").strip()
                name = c2.text_input("Student full name *").strip()
                program = c1.text_input("Program (e.g. BS Computer Science)").strip()
                department = c2.text_input("Department").strip()
                session = c1.text_input("Academic session (e.g. 2026-27)").strip()
                status = c2.selectbox("Status", ["Active", "On Leave", "Graduated", "Withdrawn"])
                save = st.form_submit_button("Save student")
            if save:
                if not student_no or not name: st.error("Roll number and student name are required.")
                elif user["role"] == "hod" and user["department"] and department != user["department"]: st.error("HODs can only add students to their assigned department.")
                else:
                    with SessionLocal() as db:
                        if db.scalar(select(Student).where(Student.student_no == student_no)):
                            st.error("That student number already exists.")
                        else:
                            db.add(Student(student_no=student_no, full_name=name, program=program, department=department, academic_session=session, status=status))
                            audit(db, user["id"], "student_created", f"Student {student_no}"); db.commit()
                            st.success("Student saved."); st.rerun()
    with SessionLocal() as db:
        q = select(Student)
        if user["role"] == "student":
            q = q.where(Student.user_id == user["id"])
        elif user["role"] == "parent":
            q = q.where(Student.parent_user_id == user["id"])
        elif user["role"] == "hod" and user["department"]:
            q = q.where(Student.department == user["department"])
        records = db.scalars(q.order_by(Student.full_name)).all()
        rows = [{"Roll number": x.student_no, "Name": x.full_name, "Program": x.program, "Department": x.department, "Session": x.academic_session, "Status": x.status} for x in records]
    if rows: st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else: st.info("No linked student records found. An administrator can add records and link student/parent accounts as the next workflow is configured.")

def courses_module(user):
    st.subheader("Courses and teaching assignments")
    if user["role"] in ("super_admin", "second_admin", "hod"):
        with st.expander("Add course"):
            with st.form("add_course"):
                a,b = st.columns(2)
                code = a.text_input("Course code *").strip().upper()
                title = b.text_input("Course title *").strip()
                dept = a.text_input("Department", value=user["department"] if user["role"] == "hod" else "").strip()
                program = b.text_input("Program").strip()
                term = a.text_input("Semester / term").strip()
                credits = b.number_input("Credit hours", min_value=0, max_value=12, value=3)
                teacher_options = {}
                with SessionLocal() as db:
                    teachers = db.scalars(select(User).where(User.role == "teacher", User.active == True).order_by(User.full_name)).all()
                    teacher_options = {f"{t.full_name} ({t.username})": t.id for t in teachers}
                teacher_label = st.selectbox("Assigned teacher (optional)", ["Unassigned"] + list(teacher_options))
                save = st.form_submit_button("Save course")
            if save:
                if not code or not title: st.error("Course code and title are required.")
                elif user["role"] == "hod" and user["department"] and dept != user["department"]: st.error("You can only manage courses in your assigned department.")
                else:
                    with SessionLocal() as db:
                        if db.scalar(select(Course).where(Course.code == code)): st.error("Course code already exists.")
                        else:
                            db.add(Course(code=code, title=title, department=dept, program=program, term=term, credits=int(credits), teacher_user_id=teacher_options.get(teacher_label)))
                            audit(db, user["id"], "course_created", code); db.commit(); st.success("Course saved."); st.rerun()
    with SessionLocal() as db:
        q = select(Course, User.full_name).outerjoin(User, Course.teacher_user_id == User.id)
        if user["role"] == "teacher": q = q.where(Course.teacher_user_id == user["id"])
        elif user["role"] == "hod" and user["department"]: q = q.where(Course.department == user["department"])
        rows = db.execute(q.order_by(Course.code)).all()
        data = [{"Code": c.code, "Title": c.title, "Department": c.department, "Program": c.program, "Term": c.term, "Credits": c.credits, "Teacher": teacher or "Unassigned"} for c,teacher in rows]
    if data: st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else: st.info("No courses found.")

def attendance_module(user):
    st.subheader("Attendance register")
    if user["role"] in ("teacher", "super_admin", "second_admin", "hod"):
        with SessionLocal() as db:
            cq = select(Course)
            if user["role"] == "teacher": cq = cq.where(Course.teacher_user_id == user["id"])
            elif user["role"] == "hod" and user["department"]: cq = cq.where(Course.department == user["department"])
            courses = db.scalars(cq.order_by(Course.code)).all()
            students = db.scalars(select(Student).where(Student.status == "Active").order_by(Student.full_name)).all()
        if not courses or not students:
            st.info("Add courses and active student records before recording attendance.")
        else:
            course_map = {f"{c.code} — {c.title}": c.id for c in courses}
            student_map = {f"{s.student_no} — {s.full_name}": s.id for s in students}
            with st.form("attendance_form"):
                selected_course = st.selectbox("Course", list(course_map))
                selected_student = st.selectbox("Student", list(student_map))
                att_date = st.date_input("Class date", value=date.today())
                status = st.selectbox("Attendance status", ["Present", "Absent", "Late", "Excused"])
                save = st.form_submit_button("Save attendance")
            if save:
                with SessionLocal() as db:
                    exists = db.scalar(select(Attendance).where(Attendance.student_id == student_map[selected_student], Attendance.course_id == course_map[selected_course], Attendance.attendance_date == att_date))
                    if exists: st.error("Attendance already exists for this student, course and date. Edit workflow is not enabled yet.")
                    else:
                        db.add(Attendance(student_id=student_map[selected_student], course_id=course_map[selected_course], attendance_date=att_date, status=status, recorded_by=user["id"]))
                        audit(db, user["id"], "attendance_recorded", f"{selected_student}, {selected_course}, {att_date}, {status}"); db.commit(); st.success("Attendance recorded."); st.rerun()
    with SessionLocal() as db:
        q = select(Attendance.attendance_date, Student.student_no, Student.full_name, Course.code, Course.title, Attendance.status).join(Student, Attendance.student_id == Student.id).join(Course, Attendance.course_id == Course.id).order_by(Attendance.attendance_date.desc()).limit(300)
        if user["role"] == "student": q = q.where(Student.user_id == user["id"])
        elif user["role"] == "parent": q = q.where(Student.parent_user_id == user["id"])
        elif user["role"] == "teacher": q = q.where(Attendance.recorded_by == user["id"])
        rows = db.execute(q).all()
        data = [{"Date": d, "Roll number": no, "Student": name, "Course": code, "Course title": title, "Status": status} for d,no,name,code,title,status in rows]
    if data: st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else: st.info("No attendance records available for your account.")

def library_module(user):
    st.subheader("Library catalogue")
    if user["role"] in ("librarian", "super_admin", "second_admin"):
        with st.expander("Add a book"):
            with st.form("add_book"):
                a,b = st.columns(2)
                accession = a.text_input("Accession number *").strip()
                title = b.text_input("Book title *").strip()
                author = a.text_input("Author").strip()
                category = b.text_input("Category").strip()
                copies = a.number_input("Total copies", min_value=1, max_value=10000, value=1)
                save = st.form_submit_button("Add book")
            if save:
                if not accession or not title: st.error("Accession number and title are required.")
                else:
                    with SessionLocal() as db:
                        if db.scalar(select(Book).where(Book.accession_no == accession)): st.error("Accession number already exists.")
                        else:
                            db.add(Book(accession_no=accession, title=title, author=author, category=category, total_copies=int(copies), available_copies=int(copies)))
                            audit(db, user["id"], "book_created", accession); db.commit(); st.success("Book added."); st.rerun()
    with SessionLocal() as db:
        books = db.scalars(select(Book).order_by(Book.title)).all()
        data = [{"Accession": b.accession_no, "Title": b.title, "Author": b.author, "Category": b.category, "Total copies": b.total_copies, "Available": b.available_copies} for b in books]
    if data: st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else: st.info("The catalogue is empty. Librarian can add books.")
    st.caption("This phase includes catalogue inventory. Book issue/return transactions are planned for a later phase.")

def hostel_module(user):
    st.subheader("Hostel rooms and capacity")
    if user["role"] in ("hostel_warden", "super_admin", "second_admin"):
        with st.expander("Add hostel room"):
            with st.form("add_room"):
                a,b = st.columns(2)
                hostel = a.text_input("Hostel name *").strip()
                room = b.text_input("Room number *").strip()
                capacity = a.number_input("Capacity", min_value=1, max_value=100, value=2)
                occupied = b.number_input("Current occupied beds", min_value=0, max_value=100, value=0)
                save = st.form_submit_button("Save room")
            if save:
                if not hostel or not room: st.error("Hostel name and room number are required.")
                elif occupied > capacity: st.error("Occupied beds cannot exceed capacity.")
                else:
                    with SessionLocal() as db:
                        db.add(HostelRoom(hostel_name=hostel, room_no=room, capacity=int(capacity), occupied=int(occupied), status="Full" if occupied == capacity else "Available"))
                        audit(db, user["id"], "hostel_room_created", f"{hostel} / {room}"); db.commit(); st.success("Room saved."); st.rerun()
    with SessionLocal() as db:
        rooms = db.scalars(select(HostelRoom).order_by(HostelRoom.hostel_name, HostelRoom.room_no)).all()
        data = [{"Hostel": r.hostel_name, "Room": r.room_no, "Capacity": r.capacity, "Occupied": r.occupied, "Vacancies": r.capacity-r.occupied, "Status": r.status} for r in rooms]
    if data: st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else: st.info("No hostel rooms have been configured.")
    st.caption("Room inventory is included. Student room allocation and check-in/check-out workflows are planned for a later phase.")

def fees_module(user):
    st.subheader("Fee records")
    if user["role"] in ("super_admin", "second_admin"):
        with st.expander("Create fee record"):
            with SessionLocal() as db:
                students = db.scalars(select(Student).order_by(Student.full_name)).all()
            if not students: st.info("Add student records first.")
            else:
                smap = {f"{s.student_no} — {s.full_name}": s.id for s in students}
                with st.form("fee_form"):
                    student = st.selectbox("Student", list(smap))
                    desc = st.text_input("Fee description", value="College fee")
                    amount = st.number_input("Amount (PKR)", min_value=0.0, step=100.0)
                    paid = st.number_input("Paid amount (PKR)", min_value=0.0, step=100.0)
                    due = st.date_input("Due date", value=date.today())
                    save = st.form_submit_button("Save fee record")
                if save:
                    if paid > amount: st.error("Paid amount cannot exceed total amount.")
                    else:
                        status = "Paid" if paid >= amount else ("Partial" if paid > 0 else "Unpaid")
                        with SessionLocal() as db:
                            db.add(FeeRecord(student_id=smap[student], description=desc, amount=amount, paid_amount=paid, due_date=due, status=status))
                            audit(db, user["id"], "fee_record_created", f"{student}, amount={amount}, paid={paid}"); db.commit(); st.success("Fee record saved."); st.rerun()
    with SessionLocal() as db:
        q = select(FeeRecord, Student.student_no, Student.full_name).join(Student, FeeRecord.student_id == Student.id).order_by(FeeRecord.created_at.desc())
        if user["role"] == "student": q = q.where(Student.user_id == user["id"])
        elif user["role"] == "parent": q = q.where(Student.parent_user_id == user["id"])
        rows = db.execute(q).all()
        data = [{"Roll number": no, "Student": name, "Description": f.description, "Amount PKR": f.amount, "Paid PKR": f.paid_amount, "Balance PKR": f.amount-f.paid_amount, "Due date": f.due_date, "Status": f.status} for f,no,name in rows]
    if data: st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
    else: st.info("No fee records available for your account.")
    st.caption("This module records fees; it does not connect to a bank or payment gateway.")

def ai_assistant(user):
    st.subheader("GPGC AI assistant")
    st.write("Ask for general explanations, study planning or help understanding college procedures. Do not enter private student data, passwords or confidential records.")
    key = get_setting("GROQ_API_KEY")
    if not key:
        st.warning("Groq API key is not configured yet. Add GROQ_API_KEY to Streamlit Cloud → App → Settings → Secrets, or to your local .streamlit/secrets.toml file.")
        st.code('GROQ_API_KEY = "your_groq_api_key_here"\nGROQ_MODEL = "llama-3.3-70b-versatile"', language="toml")
        st.markdown("Get a key from [Groq Console](https://console.groq.com/keys). Never commit your real key to GitHub.")
        return
    prompt = st.text_area("Your question", placeholder="Explain how attendance percentage is calculated.", height=110)
    if st.button("Ask AI", type="primary"):
        if not prompt.strip(): st.error("Enter a question first.")
        else:
            try:
                from groq import Groq
                client = Groq(api_key=key)
                model = get_setting("GROQ_MODEL", "llama-3.3-70b-versatile")
                with st.spinner("Generating answer..."):
                    result = client.chat.completions.create(model=model, messages=[{"role":"system","content":"You are a helpful educational assistant for Government Post Graduate College Miran Shah, North Waziristan. Answer clearly and safely. Do not claim to access college records or official policies unless provided in the prompt."},{"role":"user","content":prompt}], temperature=0.4, max_tokens=1000)
                st.markdown(result.choices[0].message.content)
            except Exception as e:
                st.error("The AI request failed. Check the Groq key, model availability, network and API quota.")
                st.caption(str(e)[:300])

def dashboard(user):
    role = user["role"]
    st.markdown(f'<div class="hero"><h1>🎓 {ROLE_LABELS.get(role, role)} Dashboard</h1><p>Government Post Graduate College Miran Shah · North Waziristan</p></div>', unsafe_allow_html=True)
    with SessionLocal() as db:
        n_students = db.scalar(select(func.count()).select_from(Student)) or 0
        n_users = db.scalar(select(func.count()).select_from(User).where(User.active == True)) or 0
        n_courses = db.scalar(select(func.count()).select_from(Course)) or 0
        n_ann = db.scalar(select(func.count()).select_from(Announcement).where(Announcement.published == True)) or 0
        n_books = db.scalar(select(func.count()).select_from(Book)) or 0
        n_rooms = db.scalar(select(func.count()).select_from(HostelRoom)) or 0
    if role in ("super_admin", "second_admin"):
        metric_row([("Active accounts", n_users), ("Students", n_students), ("Courses", n_courses), ("Announcements", n_ann)])
    elif role in ("teacher", "hod"):
        metric_row([("Students", n_students), ("Courses", n_courses), ("Announcements", n_ann)])
    elif role == "librarian": metric_row([("Catalogue titles", n_books), ("Active users", n_users), ("Announcements", n_ann)])
    elif role == "hostel_warden": metric_row([("Hostel rooms", n_rooms), ("Students", n_students), ("Announcements", n_ann)])
    else: metric_row([("College courses", n_courses), ("Announcements", n_ann)])
    st.write(f"Welcome, **{user['full_name']}**. Your current role is **{ROLE_LABELS.get(role, role)}**.")

    allowed = {
        "super_admin": ["Overview","Students","Courses","Attendance","Fees","Library","Hostel","Announcements","User management","AI assistant (Groq)","Audit log"],
        "second_admin": ["Overview","Students","Courses","Attendance","Fees","Library","Hostel","Announcements","User management","AI assistant (Groq)"],
        "teacher": ["Overview","Students","Courses","Attendance","Announcements","AI assistant (Groq)"],
        "student": ["Overview","Students","Courses","Attendance","Fees","Library","Announcements","AI assistant (Groq)"],
        "parent": ["Overview","Students","Attendance","Fees","Announcements","AI assistant (Groq)"],
        "librarian": ["Overview","Library","Announcements","AI assistant (Groq)"],
        "employee": ["Overview","Announcements","AI assistant (Groq)"],
        "hod": ["Overview","Students","Courses","Attendance","Announcements","AI assistant (Groq)"],
        "hostel_warden": ["Overview","Hostel","Announcements","AI assistant (Groq)"]
    }
    available = allowed.get(role, ["Overview", "Announcements"])
    # Streamlit-native horizontal navigation. Each category exposes a dropdown of allowed modules.
    groups = {
        "Home": ["Overview"],
        "Academics": [x for x in ["Students", "Courses", "Attendance"] if x in available],
        "Administration": [x for x in ["Fees", "User management", "Audit log"] if x in available],
        "Services": [x for x in ["Library", "Hostel"] if x in available],
        "Communication": [x for x in ["Announcements"] if x in available],
        "AI Tools": [x for x in ["AI assistant (Groq)"] if x in available]
    }
    groups = {k:v for k,v in groups.items() if v}
    st.markdown("""<style>
    div[data-testid="stHorizontalBlock"] div[data-testid="stSelectbox"] label {font-weight:650;}
    div[data-testid="stHorizontalBlock"] div[data-testid="stSelectbox"] > div {border-radius:10px;}
    .nav-hint {font-size:.84rem;color:#7b8794;margin:.1rem 0 .65rem 0}
    </style>""", unsafe_allow_html=True)
    st.markdown('<div class="nav-hint">Use the top navigation menus to open the modules available for your role.</div>', unsafe_allow_html=True)
    nav_cols = st.columns(len(groups))
    selected_module = "Overview"
    for col, (group_name, modules) in zip(nav_cols, groups.items()):
        with col:
            chosen = st.selectbox(group_name, modules, key=f"nav_{role}_{group_name}", label_visibility="visible")
            if chosen != "Overview":
                # Later menus take priority only if they contain the currently selected non-default module.
                if st.session_state.get(f"active_module_{role}") == chosen or selected_module == "Overview":
                    selected_module = chosen
    # Preserve the last explicit selection; each dropdown is a real, keyboard-accessible control.
    non_overview = [st.session_state.get(f"nav_{role}_{g}") for g in groups if g != "Home"]
    chosen_modules = [x for x in non_overview if x and x != "Overview"]
    if chosen_modules:
        selected_module = st.session_state.get(f"active_module_{role}", chosen_modules[0])
        if selected_module not in chosen_modules:
            selected_module = chosen_modules[0]
    else:
        selected_module = "Overview"
    # Explicit module selector below the top bar avoids ambiguity when multiple dropdowns have selections.
    if len(available) > 1:
        selected_module = st.selectbox("Open module", available, index=available.index(selected_module) if selected_module in available else 0, key=f"module_route_{role}")
    st.divider()
    if selected_module == "Overview":
        st.subheader("Overview")
        st.write("Choose a module from the navigation above to manage the records available to your role.")
        st.caption("Modules are being expanded in phases. Records must be restricted by account links and department where configured.")
        show_announcements(user, manage=role in ("super_admin", "second_admin", "hod"))
    elif selected_module == "Students": students_module(user)
    elif selected_module == "Courses": courses_module(user)
    elif selected_module == "Attendance": attendance_module(user)
    elif selected_module == "Fees": fees_module(user)
    elif selected_module == "Library": library_module(user)
    elif selected_module == "Hostel": hostel_module(user)
    elif selected_module == "Announcements":
        if role in ("super_admin", "second_admin", "hod"):
            st.subheader("Create announcement")
            with st.form("announcement_form", clear_on_submit=True):
                title = st.text_input("Announcement title")
                body = st.text_area("Announcement details", height=120)
                audience = st.selectbox("Audience", ["Everyone"] + ROLES, format_func=lambda r: "Everyone" if r == "Everyone" else ROLE_LABELS[r])
                publish = st.form_submit_button("Publish announcement", type="primary")
            if publish:
                if not title.strip() or not body.strip(): st.error("Title and details are required.")
                else: add_announcement(user, title, body, audience); st.success("Announcement published."); st.rerun()
            st.caption("You can edit or delete an announcement by expanding it below.")
            show_announcements(user, manage=True)
        else:
            show_announcements(user, manage=False)
    elif selected_module == "User management": admin_users(user)
    elif selected_module == "AI assistant (Groq)": ai_assistant(user)
    elif selected_module == "Audit log":
        if role != "super_admin": st.error("You are not authorized to view the system audit log.")
        else:
            with SessionLocal() as db:
                rows = db.execute(select(AuditLog.created_at, User.username, AuditLog.action, AuditLog.details).outerjoin(User, AuditLog.user_id == User.id).order_by(AuditLog.created_at.desc()).limit(250)).all()
                data = [{"Time": t, "User": u or "system", "Action": a, "Details": d} for t,u,a,d in rows]
            if data: st.dataframe(pd.DataFrame(data), use_container_width=True, hide_index=True)
            else: st.info("No audit events yet.")

def main():
    user = current_user()
    if not user:
        login_screen()
        st.divider()
        st.caption("GPGC-CMS starter release · Never use real student records until deployment security, backups and access rules have been reviewed.")
        return
    with st.sidebar:
        st.markdown("### 🎓 GPGC-CMS")
        st.write(user["full_name"])
        st.caption(ROLE_LABELS.get(user["role"], user["role"]))
        if user["department"]: st.caption(user["department"])
        st.divider()
        if st.button("Log out", use_container_width=True):
            with SessionLocal() as db:
                audit(db, user["id"], "logout", "User logged out"); db.commit()
            st.session_state.clear(); st.rerun()
        st.markdown("---")
        st.caption("GPGC Miran Shah · North Waziristan")
    dashboard(user)

if __name__ == "__main__": main()
