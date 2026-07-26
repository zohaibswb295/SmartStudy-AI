import os
import random
from datetime import date, datetime

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash


MYSQL_USER = "root"
MYSQL_PASSWORD = ""


OPENAI_API_KEY = "PASTE-YOUR-OPENAI-API-KEY-HERE"



MYSQL_HOST = "localhost"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = ""            # XAMPP mein default khali hota hai
MYSQL_DATABASE = "smartstudy"


app = Flask(__name__)
app.config['SECRET_KEY'] = 'smartstudy-secret-key-change-me'
app.config['SQLALCHEMY_DATABASE_URI'] = (
    f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

MOTIVATION_QUOTES = [
    "Success is the sum of small efforts repeated day in and day out.",
    "The expert in anything was once a beginner.",
    "Don't watch the clock; do what it does. Keep going.",
    "Study while others are sleeping; work while others are loafing.",
    "It always seems impossible until it's done.",
    "Small daily improvements are the key to staggering long-term results.",
    "Push yourself, because no one else is going to do it for you.",
    "The future depends on what you do today.",
    "Discipline is choosing between what you want now and what you want most.",
    "You don't have to be great to start, but you have to start to be great.",
]


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    subjects = db.relationship('Subject', backref='owner', cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='owner', cascade='all, delete-orphan')
    tasks = db.relationship('Task', backref='owner', cascade='all, delete-orphan')
    plans = db.relationship('StudyPlan', backref='owner', cascade='all, delete-orphan')


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    
    confidence = db.Column(db.Integer, default=3)

    tasks = db.relationship('Task', backref='subject', cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='subject', cascade='all, delete-orphan')


class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    is_done = db.Column(db.Boolean, default=False)
    is_goal = db.Column(db.Boolean, default=False)  # simple flag: task vs goal
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class StudyPlan(db.Model):
    """One row per planned study slot for the daily planner."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    plan_date = db.Column(db.Date, nullable=False, default=date.today)
    subject_name = db.Column(db.String(100), nullable=False)
    start_time = db.Column(db.String(20), nullable=False)
    duration_minutes = db.Column(db.Integer, default=30)
    is_done = db.Column(db.Boolean, default=False)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def login_required(view):
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return view(*args, **kwargs)
    wrapped.__name__ = view.__name__
    return wrapped


def current_user():
    uid = session.get('user_id')
    return User.query.get(uid) if uid else None


def compute_weak_subjects(user):
    """
    Very simple analytics: for each subject, look at completion rate of
    tasks + the student's self-rated confidence. Lower combined score
    = weaker subject.
    """
    results = []
    for subj in user.subjects:
        total = len(subj.tasks)
        done = len([t for t in subj.tasks if t.is_done])
        completion_rate = (done / total * 100) if total else 0
        # score out of 100: 60% from completion, 40% from confidence
        score = completion_rate * 0.6 + (subj.confidence / 5 * 100) * 0.4
        results.append({
            'subject': subj,
            'completion_rate': round(completion_rate, 1),
            'confidence': subj.confidence,
            'score': round(score, 1),
        })
    results.sort(key=lambda r: r['score'])
    return results


def ai_reply(message, weak_subjects):
    """
    Calls OpenAI if a key is configured, otherwise returns a rule-based
    fallback answer so the assistant still works without any API key.
    """
    if OPENAI_API_KEY and not OPENAI_API_KEY.startswith("PASTE-"):
        try:
            from openai import OpenAI
            client = OpenAI(api_key=OPENAI_API_KEY)
            weak_names = ", ".join(w['subject'].name for w in weak_subjects[:3]) or "none yet"
            system_prompt = (
                "You are SmartStudy AI, a friendly study assistant for a student. "
                f"The student's current weakest subjects are: {weak_names}. "
                "Give short, practical, encouraging study advice."
            )
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message},
                ],
                max_tokens=300,
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"(AI service error, showing fallback answer) {fallback_ai_reply(message, weak_subjects)}"
    return fallback_ai_reply(message, weak_subjects)


def fallback_ai_reply(message, weak_subjects):
    if weak_subjects:
        top = weak_subjects[0]['subject'].name
        return (
            f"Based on your progress, '{top}' needs the most attention right now. "
            "Try the Pomodoro technique: 25 minutes focused study + 5 minute break, "
            "repeated 4 times, focusing on that subject today. Break the topic into "
            "small tasks and add them to your Task list so you can track progress."
        )
    return (
        "Add a few subjects and tasks first, then I can tell you exactly where to "
        "focus. In general: study your hardest subject when your energy is highest, "
        "usually earlier in the day."
    )


# ---------------------------------------------------------
# Auth routes
# ---------------------------------------------------------
@app.route('/')
def index():
    if current_user():
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if not name or not email or not password:
            flash('Please fill in all fields.', 'error')
            return redirect(url_for('signup'))

        if User.query.filter_by(email=email).first():
            flash('An account with this email already exists.', 'error')
            return redirect(url_for('signup'))

        user = User(name=name, email=email, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        flash('Account created! Welcome to SmartStudy AI.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            return redirect(url_for('dashboard'))

        flash('Invalid email or password.', 'error')
        return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))


# ---------------------------------------------------------
# Dashboard
# ---------------------------------------------------------
@app.route('/dashboard')
@login_required
def dashboard():
    user = current_user()
    today = date.today()

    tasks_today = Task.query.filter_by(user_id=user.id, due_date=today).all()
    pending_tasks = Task.query.filter_by(user_id=user.id, is_done=False).count()
    total_tasks = Task.query.filter_by(user_id=user.id).count()
    goals = Task.query.filter_by(user_id=user.id, is_goal=True).all()
    weak_subjects = compute_weak_subjects(user)
    quote = random.choice(MOTIVATION_QUOTES)
    plan_today = StudyPlan.query.filter_by(user_id=user.id, plan_date=today).order_by(StudyPlan.start_time).all()

    progress = round((total_tasks - pending_tasks) / total_tasks * 100, 1) if total_tasks else 0

    return render_template(
        'dashboard.html',
        user=user,
        tasks_today=tasks_today,
        pending_tasks=pending_tasks,
        total_tasks=total_tasks,
        progress=progress,
        goals=goals,
        weak_subjects=weak_subjects[:3],
        quote=quote,
        plan_today=plan_today,
    )


# ---------------------------------------------------------
# Subjects
# ---------------------------------------------------------
@app.route('/subjects', methods=['GET', 'POST'])
@login_required
def subjects():
    user = current_user()
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        confidence = int(request.form.get('confidence', 3))
        if name:
            db.session.add(Subject(user_id=user.id, name=name, confidence=confidence))
            db.session.commit()
        return redirect(url_for('subjects'))

    return render_template('subjects.html', user=user, subjects=user.subjects)


@app.route('/subjects/<int:subject_id>/delete', methods=['POST'])
@login_required
def delete_subject(subject_id):
    subj = Subject.query.filter_by(id=subject_id, user_id=session['user_id']).first_or_404()
    db.session.delete(subj)
    db.session.commit()
    return redirect(url_for('subjects'))


# ---------------------------------------------------------
# Notes
# ---------------------------------------------------------
@app.route('/notes', methods=['GET', 'POST'])
@login_required
def notes():
    user = current_user()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        subject_id = request.form.get('subject_id') or None
        if title and content:
            db.session.add(Note(user_id=user.id, subject_id=subject_id, title=title, content=content))
            db.session.commit()
        return redirect(url_for('notes'))

    all_notes = Note.query.filter_by(user_id=user.id).order_by(Note.created_at.desc()).all()
    return render_template('notes.html', user=user, notes=all_notes, subjects=user.subjects)


@app.route('/notes/<int:note_id>/delete', methods=['POST'])
@login_required
def delete_note(note_id):
    note = Note.query.filter_by(id=note_id, user_id=session['user_id']).first_or_404()
    db.session.delete(note)
    db.session.commit()
    return redirect(url_for('notes'))


# ---------------------------------------------------------
# Tasks & Goals
# ---------------------------------------------------------
@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    user = current_user()
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        due_date = request.form.get('due_date') or None
        subject_id = request.form.get('subject_id') or None
        is_goal = bool(request.form.get('is_goal'))
        if title:
            db.session.add(Task(
                user_id=user.id,
                title=title,
                subject_id=subject_id,
                is_goal=is_goal,
                due_date=datetime.strptime(due_date, '%Y-%m-%d').date() if due_date else None,
            ))
            db.session.commit()
        return redirect(url_for('tasks'))

    all_tasks = Task.query.filter_by(user_id=user.id).order_by(Task.due_date.asc().nulls_last()).all()
    return render_template('tasks.html', user=user, tasks=all_tasks, subjects=user.subjects)


@app.route('/tasks/<int:task_id>/toggle', methods=['POST'])
@login_required
def toggle_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first_or_404()
    task.is_done = not task.is_done
    db.session.commit()
    return redirect(request.referrer or url_for('tasks'))


@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.filter_by(id=task_id, user_id=session['user_id']).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return redirect(request.referrer or url_for('tasks'))


# ---------------------------------------------------------
# Daily Study Planner
# ---------------------------------------------------------
@app.route('/planner', methods=['GET', 'POST'])
@login_required
def planner():
    user = current_user()
    selected_date = request.args.get('date') or date.today().isoformat()

    if request.method == 'POST':
        subject_name = request.form.get('subject_name', '').strip()
        start_time = request.form.get('start_time', '').strip()
        duration = int(request.form.get('duration_minutes', 30))
        plan_date = request.form.get('plan_date') or date.today().isoformat()
        if subject_name and start_time:
            db.session.add(StudyPlan(
                user_id=user.id,
                plan_date=datetime.strptime(plan_date, '%Y-%m-%d').date(),
                subject_name=subject_name,
                start_time=start_time,
                duration_minutes=duration,
            ))
            db.session.commit()
        return redirect(url_for('planner', date=plan_date))

    day = datetime.strptime(selected_date, '%Y-%m-%d').date()
    plans = StudyPlan.query.filter_by(user_id=user.id, plan_date=day).order_by(StudyPlan.start_time).all()
    return render_template('planner.html', user=user, plans=plans, selected_date=selected_date)


@app.route('/planner/<int:plan_id>/toggle', methods=['POST'])
@login_required
def toggle_plan(plan_id):
    plan = StudyPlan.query.filter_by(id=plan_id, user_id=session['user_id']).first_or_404()
    plan.is_done = not plan.is_done
    db.session.commit()
    return redirect(request.referrer or url_for('planner'))


@app.route('/planner/<int:plan_id>/delete', methods=['POST'])
@login_required
def delete_plan(plan_id):
    plan = StudyPlan.query.filter_by(id=plan_id, user_id=session['user_id']).first_or_404()
    db.session.delete(plan)
    db.session.commit()
    return redirect(request.referrer or url_for('planner'))


# ---------------------------------------------------------
# Progress Analytics
# ---------------------------------------------------------
@app.route('/analytics')
@login_required
def analytics():
    user = current_user()
    weak_subjects = compute_weak_subjects(user)

    total_tasks = Task.query.filter_by(user_id=user.id).count()
    done_tasks = Task.query.filter_by(user_id=user.id, is_done=True).count()
    overall_progress = round(done_tasks / total_tasks * 100, 1) if total_tasks else 0

    return render_template(
        'analytics.html',
        user=user,
        weak_subjects=weak_subjects,
        overall_progress=overall_progress,
        total_tasks=total_tasks,
        done_tasks=done_tasks,
    )


# ---------------------------------------------------------
# AI Study Assistant
# ---------------------------------------------------------
@app.route('/ai-assistant', methods=['GET', 'POST'])
@login_required
def ai_assistant():
    user = current_user()
    weak_subjects = compute_weak_subjects(user)
    reply = None
    question = None

    if request.method == 'POST':
        question = request.form.get('question', '').strip()
        if question:
            reply = ai_reply(question, weak_subjects)

    return render_template(
        'ai_assistant.html',
        user=user,
        reply=reply,
        question=question,
        weak_subjects=weak_subjects[:3],
        ai_enabled=bool(OPENAI_API_KEY) and not OPENAI_API_KEY.startswith("PASTE-"),
    )


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
