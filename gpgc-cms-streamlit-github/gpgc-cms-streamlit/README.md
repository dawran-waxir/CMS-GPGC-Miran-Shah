# GPGC Miran Shah College Management System (Streamlit edition)

A beginner-friendly, GitHub-ready starter for Government Post Graduate College Miran Shah, North Waziristan. It uses Streamlit, SQLAlchemy, SQLite locally or PostgreSQL online, Argon2id password hashing, and an optional Groq-powered educational assistant.

## Included in this ZIP

- Nine role dashboards: Super Admin, Second Admin, Teacher, Student, Parent, Librarian, Employee, HOD, Hostel Warden.
- Secure password hashing and administrator bootstrap from secrets.
- User/role administration, student records, courses, attendance, fee records, library catalogue, hostel room inventory, announcements and audit log.
- Optional Groq AI assistant; the app still runs without a Groq key.
- SQLite database for easy local testing; PostgreSQL supported through `DATABASE_URL` for online deployment.
- GitHub and Streamlit Community Cloud setup instructions.

> This is a functional starter/MVP, not a finished institutional ERP. Library issue/return, hostel allocations, student-parent account linking screens, result approval, password reset/MFA, formal permissions administration, payment integration, backup automation and institutional policy review are not complete. Do not enter real sensitive records until the college has reviewed and tested the system.

## 1. Requirements

- Python 3.11 or 3.12 recommended
- Git (for GitHub upload)
- A browser
- Optional: PostgreSQL database for online use
- Optional: Groq API key from https://console.groq.com/keys

## 2. Run locally on Windows with VS Code

1. Extract the ZIP.
2. Open the extracted `gpgc-cms-streamlit` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:

   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt terminal and run `.venv\Scripts\activate.bat`, or run `.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.venv\Scripts\python.exe -m streamlit run app.py`.

5. Install packages:

   ```powershell
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml`.
7. Edit `.streamlit/secrets.toml` and change `BOOTSTRAP_ADMIN_USERNAME` and `BOOTSTRAP_ADMIN_PASSWORD`. Use a unique password of at least 16 characters. The example values are placeholders and must not be used.
8. Optional: paste your Groq API key into `GROQ_API_KEY`. Keep this file private.
9. Start the app:

   ```powershell
   streamlit run app.py
   ```

10. Open the local URL printed in the terminal, normally http://localhost:8501.
11. Sign in using the bootstrap username and password you set in secrets.

The app creates the database tables automatically. Local data is stored in `gpgc_cms.db`.

## 3. Upload to GitHub

1. Create a new **private** GitHub repository first if you plan to continue development with college data.
2. Make sure `.streamlit/secrets.toml` is not selected for upload. `.gitignore` already excludes it.
3. In the VS Code terminal, run:

   ```bash
   git init
   git add .
   git status
   ```

4. Carefully inspect `git status`. Confirm `.streamlit/secrets.toml`, database files and API keys are NOT listed.
5. Commit and push:

   ```bash
   git commit -m "Initial GPGC CMS Streamlit application"
   git branch -M main
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
   git push -u origin main
   ```

Replace the repository URL with your own. If Git is not installed, upload the extracted source files using GitHub's web interface, but never upload secrets or database files.

## 4. Deploy on Streamlit Community Cloud

1. Push the code to GitHub.
2. Open https://share.streamlit.io/ and sign in with GitHub.
3. Select **Create app**, choose your repository and branch, and set the main file path to `app.py`.
4. Open **App settings → Secrets** and add secrets in TOML format, for example:

   ```toml
   DATABASE_URL = "postgresql://DB_USER:DB_PASSWORD@DB_HOST:5432/DB_NAME?sslmode=require"
   BOOTSTRAP_ADMIN_USERNAME = "your-unique-admin-username"
   BOOTSTRAP_ADMIN_PASSWORD = "a-long-random-password-of-at-least-16-characters"
   GROQ_API_KEY = "your-groq-api-key"
   GROQ_MODEL = "llama-3.3-70b-versatile"
   ```

5. Replace the database URL with a real PostgreSQL connection URL from your managed PostgreSQL provider. Do not paste the sample values unchanged. Use the provider's SSL/TLS connection instructions. Keep all credentials in Streamlit Secrets, never in Python files or GitHub.
6. Deploy the app. The first launch creates tables and creates the initial Super Admin if the configured username does not already exist.
7. Test login, each role, data creation, and database persistence. Check the deployment logs for errors.

**Important persistence note:** SQLite is good for local learning, but the local file on a hosted app may be ephemeral and is not suitable for reliable multi-user production use. Use managed PostgreSQL for online deployment. Do not expose a database port publicly unless the provider's secure networking setup requires it.

## 5. Groq free API key

1. Open https://console.groq.com/keys and sign in.
2. Create an API key according to Groq's current console instructions.
3. Add it as `GROQ_API_KEY` in Streamlit Cloud Secrets, or local `.streamlit/secrets.toml`.
4. Restart/redeploy the app if needed, then open **AI assistant (Groq)** from a role dashboard.
5. If the model is unavailable or your account's free quota changes, select a model currently available to your Groq account and update `GROQ_MODEL` in Secrets.

Groq availability, model names, limits and free-tier terms can change. A key is not included in this ZIP; you must create your own. Never share your key or place it in a public repository. Do not send private student records to the AI assistant.

## 6. Create users and roles

Sign in as Super Admin. Open **User management**, fill in a unique username, full name, role and a strong initial password. The account will be created with a hashed password. Public registration is disabled.

For testing, create one test account per role. Use fake sample data only. Student and parent records can be added, but account-linking screens are not implemented in this release, so student/parent-specific views may be empty until those links are added directly by an authorized developer/admin workflow.

## 7. Main database tables

- `users` — accounts, role, department, password hash and active status
- `students` — student identifiers, programs, sessions, optional user/parent links
- `courses` — courses and optional teacher assignment
- `attendance` — student/course/date attendance records
- `announcements` — notices and audience targeting
- `books` — library catalogue inventory
- `hostel_rooms` — room capacity and occupancy
- `fee_records` — student fee amount, payments and balance
- `audit_logs` — basic account and administrative event trail

Tables are created from SQLAlchemy models in `app.py`. Back up PostgreSQL before making schema changes. For a production deployment, use reviewed migrations such as Alembic rather than relying only on automatic table creation.

## 8. Role access and security notes

The UI presents role-specific modules and several queries scope data to the logged-in user or department. However, this MVP does not yet implement a complete granular permission engine. Some workflows (especially account linking, staff records, result approval, library lending and hostel allocation) need further authorization checks before real-world use. Have a qualified developer conduct security review, test access across all nine roles, configure backups, and establish incident/recovery procedures before using actual college data.

## 9. Troubleshooting

- **`streamlit` not recognized:** activate `.venv` or run `python -m streamlit run app.py`.
- **Package install fails:** confirm Python 3.11/3.12, internet access and that `pip install -r requirements.txt` completed.
- **Admin cannot log in:** verify the username/password in secrets. If a user already exists, changing bootstrap secrets will not reset that user's password; do not delete production data casually.
- **PostgreSQL connection error:** verify `DATABASE_URL`, username/password, host, database name, network access and SSL options supplied by the provider.
- **Groq request fails:** confirm key is valid, the chosen model is available to your account, and quota has not been exhausted.
- **Deployment doesn't see changed secrets:** save the Secrets settings and restart/redeploy the app.

## 10. Recommended next development phase

1. Add secure student/parent linking and profile editing.
2. Add result entry, approval and publication workflows.
3. Add library issue/return transactions and hostel resident allocation.
4. Add password reset, MFA, login throttling across distributed deployments and a proper permission matrix.
5. Add Alembic migrations, automated tests, backup/restore tests, and privacy/security review.
