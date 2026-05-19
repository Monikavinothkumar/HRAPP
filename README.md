# RecruitPro – HR Recruitment Dashboard

## Overview
RecruitPro is a Flask-based internal HR recruitment dashboard that centralizes candidate management, interview scheduling, job portal access, resume uploads, notes, and analytics.

## Project Structure

RecruitPro/
│── app.py
│── requirements.txt
│── README.md
│── database.db (created automatically)
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── candidates.html
│   ├── schedule.html
│   ├── portals.html
│   └── notes.html
│
├── static/
│   ├── css/style.css
│   ├── js/script.js
│   ├── uploads/
│   └── images/

## Database Schema

- `User`:
  - id
  - username
  - password
  - role

- `Candidate`:
  - id
  - name
  - mobile
  - email
  - position
  - experience
  - source_portal
  - status
  - resume_filename
  - created_at

- `Interview`:
  - id
  - candidate_id
  - interview_date
  - interview_time
  - interview_mode
  - notes
  - created_at

- `Note`:
  - id
  - title
  - content
  - is_done
  - created_at

- `Task`:
  - id
  - description
  - is_done
  - created_at

- `PortalFavorite`:
  - id
  - portal_name

## Setup Instructions

1. Open a terminal in the `c:\Users\Admin\Documents\HRAPP` folder.
2. Create a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run the app:
   ```bash
   python app.py
   ```
5. Open `http://127.0.0.1:5000` in your browser.

## Default Users

- Admin: `admin` / `admin123`
- Recruiter: `recruiter` / `recruiter123`

## Notes

- Resumes are stored in `static/uploads`.
- The app automatically creates `database.db` and seeded users on first launch.
- Use the dark/light toggle in the top navbar for theme switching.
# HRAPP
