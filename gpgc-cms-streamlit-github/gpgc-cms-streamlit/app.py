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
        st.subheader("Second Admin operations" if role == "second_admin" else "Overview")
        if role == "second_admin":
            st.write("Manage day-to-day college administration using the modules assigned to your role.")
            st.caption("Your access includes student records, courses, attendance, fee records, library catalogue, hostel room inventory, announcements, and operational user accounts. System-wide security settings, Super Admin accounts, and the audit-log module remain restricted to the Super Admin.")
            st.markdown("**Common tasks:** update student records, maintain course assignments, record attendance, review fee records, manage the library catalogue and hostel room inventory, and publish college announcements.")
        else:
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
