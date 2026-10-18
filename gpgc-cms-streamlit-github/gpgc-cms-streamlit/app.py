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
