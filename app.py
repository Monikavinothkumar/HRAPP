import os
import functools
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from werkzeug.utils import secure_filename

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx'}

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('RECRUITPRO_SECRET', 'recruitpro_secret_key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

db = SQLAlchemy(app)

portal_links = [
    {'name': 'LinkedIn Jobs', 'url': 'https://www.linkedin.com/jobs/'},
    {'name': 'Naukri', 'url': 'https://www.naukri.com/'},
    {'name': 'Indeed', 'url': 'https://www.indeed.com/'},
    {'name': 'Foundit', 'url': 'https://www.foundit.in/'},
    {'name': 'Shine', 'url': 'https://www.shine.com/'},
    {'name': 'Monster', 'url': 'https://www.monsterindia.com/'},
    {'name': 'TimesJobs', 'url': 'https://www.timesjobs.com/'},
    {'name': 'Freshersworld', 'url': 'https://www.freshersworld.com/'},
    {'name': 'Internshala', 'url': 'https://internshala.com/'},
]

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    mobile = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    position = db.Column(db.String(120), nullable=False)
    experience = db.Column(db.String(50), nullable=False)
    source_portal = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    resume_filename = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Interview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidate.id'), nullable=False)
    candidate = db.relationship('Candidate', backref=db.backref('interviews', lazy=True))
    interview_date = db.Column(db.String(20), nullable=False)
    interview_time = db.Column(db.String(20), nullable=False)
    interview_mode = db.Column(db.String(50), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    is_done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PortalFavorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    portal_name = db.Column(db.String(120), nullable=False, unique=True)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    is_done = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def toggle(self):
        self.is_done = not self.is_done


def create_database():
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    db.create_all()
    if not User.query.filter_by(username='admin').first():
        admin = User(username='admin', password='admin123', role='Admin')
        recruiter = User(username='recruiter', password='recruiter123', role='Recruiter')
        db.session.add_all([admin, recruiter])
        db.session.commit()

with app.app_context():
    create_database()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(route_function):
    @functools.wraps(route_function)
    def wrapper(*args, **kwargs):
        return route_function(*args, **kwargs)
    return wrapper

@app.route('/')
def home():
    return redirect(url_for('dashboard'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    return redirect(url_for('dashboard'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    total_candidates = Candidate.query.count()
    interviews_scheduled = Interview.query.count()
    selected_count = Candidate.query.filter_by(status='Selected').count()
    rejected_count = Candidate.query.filter_by(status='Rejected').count()
    pending_followups = Candidate.query.filter(Candidate.status.in_(['Applied', 'Screening', 'Interview Scheduled'])).count()

    monthly_hiring = []
    source_stats = {}
    status_stats = {}
    for c in Candidate.query.all():
        month = c.created_at.strftime('%b %Y')
        monthly_hiring.append(month)
        source_stats[c.source_portal] = source_stats.get(c.source_portal, 0) + 1
        status_stats[c.status] = status_stats.get(c.status, 0) + 1

    monthly_chart = {month: monthly_hiring.count(month) for month in sorted(set(monthly_hiring), key=lambda d: datetime.strptime(d, '%b %Y'))}
    return render_template('dashboard.html', total_candidates=total_candidates,
                           interviews_scheduled=interviews_scheduled,
                           selected_count=selected_count,
                           rejected_count=rejected_count,
                           pending_followups=pending_followups,
                           monthly_chart=monthly_chart,
                           source_stats=source_stats,
                           status_stats=status_stats,
                           portal_links=portal_links)

@app.route('/candidates', methods=['GET', 'POST'])
@login_required
def candidates():
    query = Candidate.query
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status_filter', '')
    portal_filter = request.args.get('portal_filter', '')

    if search:
        query = query.filter(
            or_(
                Candidate.name.ilike(f'%{search}%'),
                Candidate.position.ilike(f'%{search}%'),
                Candidate.email.ilike(f'%{search}%'),
                Candidate.mobile.ilike(f'%{search}%')
            )
        )
    if status_filter:
        query = query.filter_by(status=status_filter)
    if portal_filter:
        query = query.filter_by(source_portal=portal_filter)

    candidates = query.order_by(Candidate.created_at.desc()).all()
    portals = sorted({c.source_portal for c in Candidate.query.all()})
    return render_template('candidates.html', candidates=candidates, portals=portals,
                           search=search, status_filter=status_filter, portal_filter=portal_filter)

@app.route('/candidate/add', methods=['POST'])
@login_required
def add_candidate():
    name = request.form.get('name', '').strip()
    mobile = request.form.get('mobile', '').strip()
    email = request.form.get('email', '').strip()
    position = request.form.get('position', '').strip()
    experience = request.form.get('experience', '').strip()
    source_portal = request.form.get('source_portal', '').strip()
    status = request.form.get('status', '').strip()
    resume_file = request.files.get('resume_file')
    filename = None
    if resume_file and resume_file.filename != '':
        if allowed_file(resume_file.filename):
            filename = secure_filename(f"{datetime.utcnow().timestamp()}_{resume_file.filename}")
            resume_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            flash('Resume upload failed. Use PDF, DOC, or DOCX only.', 'danger')
            return redirect(url_for('candidates'))
    candidate = Candidate(name=name, mobile=mobile, email=email, position=position,
                          experience=experience, source_portal=source_portal, status=status,
                          resume_filename=filename)
    db.session.add(candidate)
    db.session.commit()
    flash('Candidate added successfully.', 'success')
    return redirect(url_for('candidates'))

@app.route('/candidate/edit/<int:candidate_id>', methods=['POST'])
@login_required
def edit_candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    candidate.name = request.form.get('name', candidate.name).strip()
    candidate.mobile = request.form.get('mobile', candidate.mobile).strip()
    candidate.email = request.form.get('email', candidate.email).strip()
    candidate.position = request.form.get('position', candidate.position).strip()
    candidate.experience = request.form.get('experience', candidate.experience).strip()
    candidate.source_portal = request.form.get('source_portal', candidate.source_portal).strip()
    candidate.status = request.form.get('status', candidate.status).strip()
    resume_file = request.files.get('resume_file')
    if resume_file and resume_file.filename != '':
        if allowed_file(resume_file.filename):
            filename = secure_filename(f"{datetime.utcnow().timestamp()}_{resume_file.filename}")
            resume_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            candidate.resume_filename = filename
        else:
            flash('Resume upload failed. Use PDF, DOC, or DOCX only.', 'danger')
            return redirect(url_for('candidates'))
    db.session.commit()
    flash('Candidate updated successfully.', 'success')
    return redirect(url_for('candidates'))

@app.route('/candidate/delete/<int:candidate_id>')
@login_required
def delete_candidate(candidate_id):
    candidate = Candidate.query.get_or_404(candidate_id)
    if candidate.resume_filename:
        resume_path = os.path.join(app.config['UPLOAD_FOLDER'], candidate.resume_filename)
        if os.path.exists(resume_path):
            try:
                os.remove(resume_path)
            except Exception:
                pass
    Interview.query.filter_by(candidate_id=candidate.id).delete()
    db.session.delete(candidate)
    db.session.commit()
    flash('Candidate deleted successfully.', 'info')
    return redirect(url_for('candidates'))

@app.route('/resume/<filename>')
@login_required
def download_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/portals')
@login_required
def portals():
    search = request.args.get('search', '').strip().lower()
    filtered = [p for p in portal_links if search in p['name'].lower()] if search else portal_links
    favorites = {fav.portal_name for fav in PortalFavorite.query.all()}
    return render_template('portals.html', portals=filtered, favorites=favorites, search=search)

@app.route('/portal/favorite', methods=['POST'])
@login_required
def portal_favorite():
    portal_name = request.form.get('portal_name')
    if not portal_name:
        return redirect(url_for('portals'))
    favorite = PortalFavorite.query.filter_by(portal_name=portal_name).first()
    if favorite:
        db.session.delete(favorite)
        flash(f'Removed {portal_name} from favorites.', 'info')
    else:
        db.session.add(PortalFavorite(portal_name=portal_name))
        flash(f'Added {portal_name} to favorites.', 'success')
    db.session.commit()
    return redirect(url_for('portals', search=request.form.get('search', '')))

@app.route('/schedule', methods=['GET', 'POST'])
@login_required
def schedule():
    if request.method == 'POST':
        candidate_id = int(request.form.get('candidate_id'))
        interview_date = request.form.get('interview_date')
        interview_time = request.form.get('interview_time')
        interview_mode = request.form.get('interview_mode')
        notes = request.form.get('notes', '')
        interview = Interview(candidate_id=candidate_id, interview_date=interview_date,
                              interview_time=interview_time, interview_mode=interview_mode,
                              notes=notes)
        db.session.add(interview)
        db.session.commit()
        flash('Interview scheduled successfully.', 'success')
        return redirect(url_for('schedule'))
    interviews = Interview.query.order_by(Interview.interview_date.desc(), Interview.interview_time.desc()).all()
    candidates = Candidate.query.order_by(Candidate.name).all()
    return render_template('schedule.html', interviews=interviews, candidates=candidates)

@app.route('/schedule/delete/<int:interview_id>')
@login_required
def delete_schedule(interview_id):
    interview = Interview.query.get_or_404(interview_id)
    db.session.delete(interview)
    db.session.commit()
    flash('Interview removed.', 'info')
    return redirect(url_for('schedule'))

@app.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    if request.method == 'POST':
        if 'task_description' in request.form:
            description = request.form.get('task_description', '').strip()
            if description:
                db.session.add(Task(description=description))
                db.session.commit()
                flash('Task added.', 'success')
        elif 'note_title' in request.form:
            title = request.form.get('note_title', '').strip()
            content = request.form.get('note_content', '').strip()
            if title and content:
                db.session.add(Note(title=title, content=content))
                db.session.commit()
                flash('Note added.', 'success')
        return redirect(url_for('notes'))
    tasks = Task.query.order_by(Task.created_at.desc()).all()
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return render_template('notes.html', tasks=tasks, notes=notes)

@app.route('/task/toggle/<int:task_id>')
@login_required
def toggle_task(task_id):
    task = Task.query.get_or_404(task_id)
    task.toggle()
    db.session.commit()
    return redirect(url_for('notes'))

@app.route('/task/delete/<int:task_id>')
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Task removed.', 'info')
    return redirect(url_for('notes'))

@app.route('/note/delete/<int:note_id>')
@login_required
def delete_note(note_id):
    note = Note.query.get_or_404(note_id)
    db.session.delete(note)
    db.session.commit()
    flash('Note removed.', 'info')
    return redirect(url_for('notes'))

@app.errorhandler(413)
def request_entity_too_large(error):
    flash('Uploaded file is too large. Limit is 16MB.', 'danger')
    return redirect(request.referrer or url_for('candidates'))

if __name__ == '__main__':
    app.run(debug=True)
