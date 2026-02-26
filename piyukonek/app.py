import pymysql
import resend
pymysql.install_as_MySQLdb()
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, send_from_directory, send_file, Response
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta, datetime
from werkzeug.utils import secure_filename
import os
import random
import re
import time
import secrets

# Load environment variables from .env file (create from .env.example)
try:
    from dotenv import load_dotenv
    from pathlib import Path
    # Load from project root (parent of piyukonek) and current dir
    _root = Path(__file__).resolve().parent.parent
    load_dotenv(_root / '.env')
    load_dotenv()  # Also try CWD
except ImportError:
    pass  # python-dotenv not installed, use system env vars only
from functools import wraps
from sqlalchemy import or_, and_, func
import openai  # Add this import for OpenAI integration
import requests  # Add this import for Hugging Face API
from io import StringIO
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from io import BytesIO
import textwrap
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
import io
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle

from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib.pagesizes import landscape, letter
import tempfile
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature

app = Flask(__name__, template_folder='templates', static_folder='static')

# -------------------- CONFIGURATION --------------------
# Use environment variables - NEVER hardcode secrets. Copy .env.example to .env
def _get_secret_key():
    key = os.environ.get('SECRET_KEY')
    if key and len(key) >= 32:
        return key
    if os.environ.get('FLASK_ENV') == 'production':
        raise ValueError('SECRET_KEY must be set (32+ chars) in production. Add to .env')
    return secrets.token_hex(32)  # Auto-generate for local dev only

app.config['SECRET_KEY'] = _get_secret_key()
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'mysql+pymysql://root:@localhost/piyukonek'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.permanent_session_lifetime = timedelta(minutes=30)

# Session configuration - SESSION_COOKIE_SECURE=True when using HTTPS
_app_env = os.environ.get('FLASK_ENV', 'development')
_https_enabled = os.environ.get('HTTPS_ENABLED', 'false').lower() == 'true'
app.config['SESSION_COOKIE_SECURE'] = _https_enabled or (_app_env == 'production')
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Email Configuration (from env vars; fallback for local dev when .env not set)
# Email Configuration - Gamit ang Resend API
resend.api_key = os.environ.get('RESEND_API_KEY')
MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'onboarding@resend.dev')

# API Keys (from env vars - never commit real keys)
app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY', '')
app.config['HF_API_TOKEN'] = os.environ.get('HF_API_TOKEN', '')

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# -------------------- INITIALIZATIONS --------------------
db = SQLAlchemy(app)


serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

# -------------------- TEMPLATE FILTERS --------------------
@app.template_filter('philippines_time')
def philippines_time_filter(utc_datetime):
    """Convert UTC datetime to Philippines time (UTC+8)"""
    if not utc_datetime:
        return None
    # Add 8 hours to UTC time for Philippines timezone
    ph_time = utc_datetime + timedelta(hours=8)
    return ph_time

@app.template_filter('filesizeformat')
def filesizeformat_filter(bytes_value):
    """Convert bytes to human readable format"""
    if bytes_value is None:
        return 'Unknown size'
    
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_value < 1024.0:
            return f"{bytes_value:.1f} {unit}"
        bytes_value /= 1024.0
    return f"{bytes_value:.1f} TB"

# -------------------- MODELS --------------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(120), nullable=False)
    user_type = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    student_id_number = db.Column(db.String(20), nullable=False)
    email_address = db.Column(db.String(30), unique=True, nullable=False)
    course = db.Column(db.String(50), nullable=False)
    college_dept = db.Column(db.String(70), nullable=False)
    year_lvl = db.Column(db.String(20), nullable=False)
    cert_of_registration = db.Column(db.String(100), nullable=False)
    student_id = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(10), default='active')
    profile_image = db.Column(db.String(255), nullable=True)
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())


class SSC(db.Model):
    __tablename__ = 'ssc'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email_address = db.Column(db.String(50), unique=True, nullable=False)
    position = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    is_online = db.Column(db.Boolean, default=False)
    last_seen = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(10), default='active')

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    fullname = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email_address = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    profile_image = db.Column(db.String(255), nullable=True)

class Department(db.Model):
    __tablename__ = 'departments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    code = db.Column(db.String(20), nullable=False, unique=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='active')  # active, archived
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False, default=1)
    
    # Relationship with courses
    courses = db.relationship('Course', backref='department', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Department {self.name}>'

class Course(db.Model):
    __tablename__ = 'courses'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False)
    description = db.Column(db.Text, nullable=True)
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=False)
    status = db.Column(db.String(20), default='active')  # active, archived
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=False, default=1)
    
    # Unique constraint for course code within department
    __table_args__ = (db.UniqueConstraint('code', 'department_id', name='unique_course_per_dept'),)
    
    def __repr__(self):
        return f'<Course {self.name}>'

class Concern(db.Model):
    __tablename__ = 'concerns'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    concern_type = db.Column(db.String(50), nullable=False)  # academic, financial, administrative, personal, other
    priority_level = db.Column(db.String(20), nullable=False)  # low, medium, high, urgent
    docs = db.Column(db.String(255), nullable=True)  # File attachment for concern (legacy)
    status = db.Column(db.String(20), default='pending')  # pending, processing, resolved, closed
    submitted_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    resolved_at = db.Column(db.DateTime, nullable=True)
    resolved_by = db.Column(db.Integer, db.ForeignKey('ssc.id'), nullable=True)
    resolution_notes = db.Column(db.Text, nullable=True)
    response_attachment = db.Column(db.String(255), nullable=True)
    
    # Admin response fields
    response_notes = db.Column(db.Text, nullable=True)
    responded_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    responded_at = db.Column(db.DateTime, nullable=True)
    
    # Rejection fields
    rejection_reason = db.Column(db.Text, nullable=True)
    rejected_by = db.Column(db.Integer, db.ForeignKey('admin.id'), nullable=True)
    rejected_at = db.Column(db.DateTime, nullable=True)
    
    # Additional fields for bulk operations
    assigned_to = db.Column(db.Integer, db.ForeignKey('ssc.id'), nullable=True)  # SSC staff assigned to handle
    processing_at = db.Column(db.DateTime, nullable=True)  # When processing started
    processed_by = db.Column(db.Integer, db.ForeignKey('ssc.id'), nullable=True)  # Who started processing
    closed_at = db.Column(db.DateTime, nullable=True)  # When closed
    closed_by = db.Column(db.Integer, db.ForeignKey('ssc.id'), nullable=True)

    # Student feedback on guidance response
    rating = db.Column(db.Integer, nullable=True)  # 1-5
    feedback = db.Column(db.Text, nullable=True)
    feedback_submitted_at = db.Column(db.DateTime, nullable=True)
    is_feedback_submitted = db.Column(db.Boolean, default=False)
    
    # Deadline field for 3-day resolution requirement
    deadline = db.Column(db.DateTime, nullable=True)  # 3 days from submission
    
    # Relationship with Student
    student = db.relationship('Student', backref=db.backref('concerns', lazy=True))
    
    # Relationships with SSC staff (multiple foreign keys to same table)
    # SSC staff who resolved the concern
    resolver = db.relationship('SSC', foreign_keys=[resolved_by], backref=db.backref('concerns_resolved', lazy=True))
    # SSC staff assigned to handle the concern
    assigned_staff = db.relationship('SSC', foreign_keys=[assigned_to], backref=db.backref('concerns_assigned', lazy=True))
    # SSC staff who started processing the concern
    processor = db.relationship('SSC', foreign_keys=[processed_by], backref=db.backref('concerns_processing', lazy=True))
    # SSC staff who closed the concern
    closer = db.relationship('SSC', foreign_keys=[closed_by], backref=db.backref('concerns_closed', lazy=True))
    
    # Relationships with Admin staff
    # Admin who responded to the concern
    admin_responder = db.relationship('Admin', foreign_keys=[responded_by], backref=db.backref('concerns_responded', lazy=True))
    # Admin who rejected the concern
    admin_rejecter = db.relationship('Admin', foreign_keys=[rejected_by], backref=db.backref('concerns_rejected', lazy=True))

# Add ConcernAttachment model for multiple file support
class ConcernAttachment(db.Model):
    __tablename__ = 'concern_attachments'
    id = db.Column(db.Integer, primary_key=True)
    concern_id = db.Column(db.Integer, db.ForeignKey('concerns.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)  # Size in bytes
    file_type = db.Column(db.String(50), nullable=True)  # File extension
    uploaded_at = db.Column(db.DateTime, server_default=db.func.now())
    
    # Relationship with Concern
    concern = db.relationship('Concern', backref=db.backref('attachments', lazy=True, cascade='all, delete-orphan'))

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # Can be student_id, ssc_id, or admin_id
    user_type = db.Column(db.String(20), nullable=False)  # student, ssc, admin
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50), nullable=False)  # concern_update, system, general, reminder_3_days, reminder_5_days
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    concern_id = db.Column(db.Integer, db.ForeignKey('concerns.id'), nullable=True)
    
    # Relationship with Concern (optional)
    concern = db.relationship('Concern', backref=db.backref('notifications', lazy=True))

# Concern type master list managed by Guidance (SSC)
class ConcernType(db.Model):
    __tablename__ = 'concern_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    is_archived = db.Column(db.Boolean, default=False)
    created_by = db.Column(db.Integer, db.ForeignKey('ssc.id'), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    archived_at = db.Column(db.DateTime, nullable=True)

class Message(db.Model):
    __tablename__ = 'messages'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, nullable=False)
    sender_type = db.Column(db.String(20), nullable=False)  # student, admin, ssc
    recipient_id = db.Column(db.Integer, nullable=False)
    recipient_type = db.Column(db.String(20), nullable=False)  # student, admin, ssc
    content = db.Column(db.Text, nullable=False)
    attachment_path = db.Column(db.String(255), nullable=True)  # Path to uploaded file
    attachment_name = db.Column(db.String(255), nullable=True)  # Original filename
    attachment_type = db.Column(db.String(50), nullable=True)  # File type (pdf, doc, etc.)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    concern_id = db.Column(db.Integer, db.ForeignKey('concerns.id'), nullable=True)  # Link to specific concern

# Add ConcernHistory model (also used as Audit Trail / Activity Log)
class ConcernHistory(db.Model):
    __tablename__ = 'concern_history'
    id = db.Column(db.Integer, primary_key=True)
    concern_id = db.Column(db.Integer, db.ForeignKey('concerns.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now())
    # Audit trail: who did the action (for transparency & accountability)
    actor_type = db.Column(db.String(20), nullable=True)   # student, ssc, admin
    actor_id = db.Column(db.Integer, nullable=True)        # id in students/ssc/admin
    actor_name = db.Column(db.String(100), nullable=True) # fullname at time of action
    old_value = db.Column(db.String(100), nullable=True)   # e.g. old priority
    new_value = db.Column(db.String(100), nullable=True)   # e.g. new priority
    concern = db.relationship('Concern', backref=db.backref('history', lazy=True))





# -------------------- DEADLINE MANAGEMENT --------------------
def check_overdue_concerns():
    """Check for overdue concerns and create notifications"""
    from datetime import datetime
    
    try:
        now = datetime.utcnow()
        overdue_concerns = Concern.query.filter(
            Concern.deadline < now,
            Concern.status != 'resolved'
        ).all()
    except Exception as e:
        # If deadline column doesn't exist, skip overdue checking
        print(f"Deadline column not found, skipping overdue check: {e}")
        return jsonify({'success': True, 'message': f'Successfully assigned {updated_count} concerns to {assigned_staff.fullname}', 'updated_count': updated_count})
    
    for concern in overdue_concerns:
        # Check if notification already exists for this concern
        existing_notification = Notification.query.filter_by(
            concern_id=concern.id,
            notification_type='overdue_concern'
        ).first()
        
        if not existing_notification:
            # Notify all SSC staff about overdue concern
            ssc_staff = SSC.query.all()
            for ssc in ssc_staff:
                notification = Notification(
                    user_id=ssc.id,
                    user_type='ssc',
                    title=f'Overdue Concern: {concern.title}',
                    message=f'Concern #{concern.id} is overdue and needs immediate attention.',
                    notification_type='overdue_concern',
                    concern_id=concern.id
                )
                db.session.add(notification)
            
            # Notify all admins
            admins = Admin.query.all()
            for admin in admins:
                notification = Notification(
                    user_id=admin.id,
                    user_type='admin',
                    title=f'Overdue Concern: {concern.title}',
                    message=f'Concern #{concern.id} is overdue and needs immediate attention.',
                    notification_type='overdue_concern',
                    concern_id=concern.id
                )
                db.session.add(notification)
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating overdue notifications: {e}")

# -------------------- SESSION MANAGEMENT --------------------
def check_session_timeout():
    """Check if user session has timed out"""
    if 'last_activity' in session:
        last_activity = datetime.fromisoformat(session['last_activity'])
        if datetime.now() - last_activity > timedelta(minutes=30):
            session.clear()
            return True
    return False

def update_session_activity():
    """Update the last activity timestamp"""
    session['last_activity'] = datetime.now().isoformat()

# -------------------- DECORATORS --------------------
def login_required(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if user is logged in
            if 'user_id' not in session or 'user_type' not in session:
                flash('Please log in to access this page.', 'error')
                return redirect(url_for('login'))
            
            # Check session timeout
            if check_session_timeout():
                flash('Your session has expired. Please log in again.', 'error')
                return redirect(url_for('login'))
            
            # Check user type permission
            if session['user_type'] != role:
                flash(f'You do not have permission to access this page. Required role: {role}', 'error')
                return redirect(url_for('login'))
            
            # Update session activity
            update_session_activity()
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# -------------------- ROUTES --------------------

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        print(f"[DEBUG] Login attempt for username: {username}")
        print(f"[DEBUG] Password length: {len(password)}")

        # Check Student table first
        student = Student.query.filter_by(username=username).first()
        print(f"[DEBUG] Student found: {student is not None}")
        
        if student:
            print(f"[DEBUG] Student ID: {student.id}")
            print(f"[DEBUG] Stored password hash: {student.password}")
            password_check = check_password_hash(student.password, password)
            print(f"[DEBUG] Password check result: {password_check}")
            
            if password_check:
                if student.status != 'active':
                    flash('Your account is pending approval by admin.', 'warning')
                    return redirect(url_for('login'))
                # Set student as online
                student.is_online = True
                student.last_seen = datetime.utcnow()
                db.session.commit()
                
                session.permanent = True
                session['user_id'] = student.id
                session['user_type'] = 'student'
                session['last_activity'] = datetime.now().isoformat()
                print(f"[DEBUG] Session set - user_id: {session['user_id']}, user_type: {session['user_type']}")
                flash('Login successful!', 'success')
                return redirect(url_for('student_dashboard'))

        # Check SSC table (for SSC staff)
        ssc = SSC.query.filter_by(username=username).first()
        print(f"[DEBUG] SSC found: {ssc is not None}")
        if ssc:
            print(f"[DEBUG] SSC ID: {ssc.id}")
            print(f"[DEBUG] Stored password hash: {ssc.password}")
            password_check = check_password_hash(ssc.password, password)
            print(f"[DEBUG] SSC password check result: {password_check}")
            if password_check:
                if ssc.status != 'active':
                    flash('Your account is pending approval by admin.', 'warning')
                    return redirect(url_for('login'))
                session.permanent = True
                session['user_id'] = ssc.id
                session['user_type'] = 'ssc'
                session['last_activity'] = datetime.now().isoformat()
                print(f"[DEBUG] Session set - user_id: {session['user_id']}, user_type: {session['user_type']}")
                flash('Login successful!', 'success')
                return redirect(url_for('ssc_dashboard'))

        # Check Admin table
        admin = Admin.query.filter_by(username=username).first()
        print(f"[DEBUG] Admin found: {admin is not None}")
        if admin:
            print(f"[DEBUG] Admin ID: {admin.id}")
            print(f"[DEBUG] Stored password hash: {admin.password}")
            password_check = check_password_hash(admin.password, password)
            print(f"[DEBUG] Admin password check result: {password_check}")
            if password_check:
                session.permanent = True
                session['user_id'] = admin.id
                session['user_type'] = 'admin'
                session['last_activity'] = datetime.now().isoformat()
                print(f"[DEBUG] Session set - user_id: {session['user_id']}, user_type: {session['user_type']}")
                flash('Login successful!', 'success')
                return redirect(url_for('admin_dashboard'))

        # Check User table (legacy)
        user = User.query.filter_by(username=username).first()
        print(f"[DEBUG] User found: {user is not None}")
        
        if user:
            password_check = check_password_hash(user.password, password)
            print(f"[DEBUG] User password check result: {password_check}")
            
            if password_check:
                session.permanent = True
                session['user_id'] = user.id
                session['user_type'] = user.user_type
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))

        # If neither student, ssc, admin, nor user found, or password is wrong
        print(f"[DEBUG] Login failed - no valid credentials found")
        flash('Invalid username or password', 'error')
    return render_template('accounts/login.html')

@app.route('/account_type')
def account_type():
    return render_template('accounts/account_type.html')

# -------------------- STUDENT SIGNUP WITH OTP --------------------

@app.route('/student_signup', methods=['GET', 'POST'])
def student_signup():
    # Load active departments and courses to populate signup form dynamically
    active_departments = Department.query.filter_by(status='active').order_by(Department.name.asc()).all()
    active_courses = Course.query.filter_by(status='active').all()

    # Build mapping from department code to list of course names
    department_id_to_code = {dept.id: dept.code for dept in active_departments}
    dept_code_to_courses = {}
    for dept in active_departments:
        dept_code_to_courses[dept.code] = []
    for course in active_courses:
        dept_code = department_id_to_code.get(course.department_id)
        if dept_code is not None:
            dept_code_to_courses[dept_code].append(course.name)

    return render_template(
        'accounts/student_signup.html',
        departments=active_departments,
        dept_courses=dept_code_to_courses
    )

@app.route('/register_student', methods=['POST'])
def register_student():
    firstname = request.form['firstname']
    lastname = request.form['lastname']
    fullname = f"{firstname} {lastname}"  # Combine first and last name
    username = request.form['username']
    student_id_number = request.form['student_id']
    email = request.form['email']
    course = request.form['course']
    college_dept = request.form['department']
    year_lvl = request.form['year']
    password = request.form['password']

    # Student ID validation
    import re
    student_id_pattern = r'^\d{4}-\d{4}$'
    if not re.match(student_id_pattern, student_id_number):
        flash("Student ID must be in format XXXX-XXXX (e.g., 0123-0321).", "error")
        return redirect(url_for('student_signup'))

    # Email validation
    if '@' not in email:
        flash("Email address must contain @ symbol.", "error")
        return redirect(url_for('student_signup'))
    
    email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
    if not re.match(email_pattern, email):
        flash("Please enter a valid email address (e.g., user@example.com).", "error")
        return redirect(url_for('student_signup'))

    # Password validation
    if len(password) < 8:
        flash("Password must be at least 8 characters long.", "error")
        return redirect(url_for('student_signup'))
    
    if not password.isalnum():
        flash("Password must contain only letters and numbers (alphanumeric).", "error")
        return redirect(url_for('student_signup'))

    # Duplicate check
    if Student.query.filter_by(username=username).first():
        flash("Username already exists. Please choose another one.", "error")
        return redirect(url_for('student_signup'))

    if Student.query.filter_by(email_address=email).first():
        flash("Email already registered. Please use a different email.", "error")
        return redirect(url_for('student_signup'))

    if email_exists_in_other_roles(email, current_role='student'):
        flash("Email is already used by another account type. Please use a different email.", "error")
        return redirect(url_for('student_signup'))

    if Student.query.filter_by(student_id_number=student_id_number).first():
        flash("Student ID already registered. Please check your Student ID number.", "error")
        return redirect(url_for('student_signup'))

    cor_file = request.files['cor']
    id_card_file = request.files['student_id_card']
    profile_image_file = request.files.get('profile_image')  # New: get profile image (optional)
    profile_image_filename = None
    if profile_image_file and profile_image_file.filename:
        profile_image_filename = f"profile_{username}_{secure_filename(profile_image_file.filename)}"
        profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_image_filename)
        profile_image_file.save(profile_image_path)

    if cor_file and id_card_file:
        cor_filename = f"cor_{username}_{secure_filename(cor_file.filename)}"
        id_card_filename = f"idcard_{username}_{secure_filename(id_card_file.filename)}"

        cor_path = os.path.join(app.config['UPLOAD_FOLDER'], cor_filename)
        id_card_path = os.path.join(app.config['UPLOAD_FOLDER'], id_card_filename)

        cor_file.save(cor_path)
        id_card_file.save(id_card_path)

        otp = str(random.randint(100000, 999999))

        session['student_data'] = {
            'fullname': fullname,
            'username': username,
            'student_id_number': student_id_number,
            'email_address': email,
            'course': course,
            'college_dept': college_dept,
            'year_lvl': year_lvl,
            'cert_of_registration': cor_filename,
            'student_id': id_card_filename,
            'password': password,
            'profile_image': profile_image_filename  # New: store profile image filename in session
        }
        session['otp'] = otp

        try:
            resend.Emails.send({
                "from": MAIL_DEFAULT_SENDER,
                "to": email,
                "subject": "Piyukonek OTP Verification Code",
                "html": f"""
                <div style="font-family: Arial, sans-serif; padding: 20px;">
                    <h2>Hello {fullname},</h2>
                    <p>Your OTP code is: <strong style="font-size: 20px;">{otp}</strong></p>
                    <p>Thank you for registering!</p>
                </div>
                """
            })
            flash("OTP has been sent to your email address.", "info")
        except Exception as e:
            print(f"RESEND ERROR: {e}")
            flash("Failed to send OTP. Please try again later.", "danger")

        return render_template('accounts/students_otp.html')

    flash('Please upload both COR and ID.', 'error')
    return redirect(url_for('student_signup'))

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    entered_otp = request.form['otp']
    actual_otp = session.get('otp')
    student_data = session.get('student_data')

    if entered_otp == actual_otp and student_data:
        # Check for duplicate email address
        existing_email = Student.query.filter_by(email_address=student_data['email_address']).first()
        if existing_email:
            session.pop('otp', None)
            session.pop('student_data', None)
            flash("Email address is already registered. Please use a different email.", "danger")
            return redirect(url_for('student_signup'))

        if email_exists_in_other_roles(student_data['email_address'], current_role='student'):
            session.pop('otp', None)
            session.pop('student_data', None)
            flash("Email address is already used by another account type. Please use a different email.", "danger")
            return redirect(url_for('student_signup'))
        
        # Check for duplicate student ID number
        existing_student_id = Student.query.filter_by(student_id_number=student_data['student_id_number']).first()
        if existing_student_id:
            session.pop('otp', None)
            session.pop('student_data', None)
            flash("Student ID number is already registered. Please check your Student ID number.", "danger")
            return redirect(url_for('student_signup'))
        
        # Check for duplicate username
        existing_username = Student.query.filter_by(username=student_data['username']).first()
        if existing_username:
            session.pop('otp', None)
            session.pop('student_data', None)
            flash("Username already exists. Please choose another username.", "danger")
            return redirect(url_for('student_signup'))
        
        try:
            new_student = Student(
                fullname=student_data['fullname'],
                username=student_data['username'],
                student_id_number=student_data['student_id_number'],
                email_address=student_data['email_address'],
                course=student_data['course'],
                college_dept=student_data['college_dept'],
                year_lvl=student_data['year_lvl'],
                cert_of_registration=student_data['cert_of_registration'],
                student_id=student_data['student_id'],
                password=generate_password_hash(student_data['password']),
                profile_image=student_data.get('profile_image'),
                status='pending'  # Set to pending for approval
            )
            db.session.add(new_student)
            db.session.commit()

            session.pop('otp', None)
            session.pop('student_data', None)
            flash("OTP verified! Your registration is pending admin approval.", "info")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            session.pop('otp', None)
            session.pop('student_data', None)
            # Check if it's a duplicate entry error
            if 'Duplicate entry' in str(e) or 'UNIQUE constraint' in str(e):
                flash("Email address or Student ID number is already registered. Please use different credentials.", "danger")
            else:
                flash("An error occurred during registration. Please try again.", "danger")
            return redirect(url_for('student_signup'))
    else:
        flash("Your OTP was incorrect or expired.", "danger")
        return render_template('accounts/students_otp.html')

@app.route('/resend_otp')
def resend_otp():
    if 'student_data' in session:
        new_otp = str(random.randint(100000, 999999))
        session['otp'] = new_otp
        email = session['student_data']['email_address']
        fullname = session['student_data']['fullname']
        try:
            if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
                flash("Email not configured. Add MAIL_USERNAME and MAIL_PASSWORD to .env", "danger")
            else:
                msg = MailMessage('Your New OTP Code', recipients=[email])
                msg.body = f"Hello {fullname},\n\nYour new OTP code is: {new_otp}"
                mail.send(msg)
                flash("New OTP has been sent to your email.", "info")
        except Exception as e:
            print(f"[MAIL ERROR] {e}")
            flash("Failed to send OTP. Check MAIL_USERNAME, MAIL_PASSWORD in .env (Gmail App Password).", "danger")
        return render_template('accounts/students_otp.html')
    return redirect(url_for('student_signup'))

# -------------------- SSC & ADMIN SIGNUP --------------------

def register_user(username, password, email, user_type, redirect_route):
    if User.query.filter_by(username=username).first():
        flash('Username already exists. Please choose another.', 'error')
        return redirect(url_for(redirect_route))

    if User.query.filter_by(email=email).first():
        flash('Email already registered. Please use a different email.', 'error')
        return redirect(url_for(redirect_route))

    hashed_password = generate_password_hash(password)
    new_user = User(username=username, password=hashed_password, email=email, user_type=user_type)
    db.session.add(new_user)
    db.session.commit()
    flash('Registration successful! Please login.', 'success')
    return redirect(url_for('login'))


def email_exists_in_other_roles(email, current_role=None):
    """Check if an email already exists in a different user role (student, ssc, admin)."""
    if not email:
        return False

    normalized_email = email.strip().lower()

    if current_role != 'student':
        student_exists = Student.query.filter(func.lower(Student.email_address) == normalized_email).first()
        if student_exists:
            return True

    if current_role != 'ssc':
        ssc_exists = SSC.query.filter(func.lower(SSC.email_address) == normalized_email).first()
        if ssc_exists:
            return True

    if current_role != 'admin':
        admin_exists = Admin.query.filter(func.lower(Admin.email_address) == normalized_email).first()
        if admin_exists:
            return True

    return False

@app.route('/ssc_signup', methods=['GET', 'POST'])
def ssc_signup():
    if request.method == 'POST':
        print("[DEBUG] SSC signup form submitted")
        # Gracefully handle missing fullname field by reconstructing it
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        fullname = request.form.get('fullname', '').strip()
        if not fullname:
            fullname = ' '.join(filter(None, [first_name, last_name])).strip()
        if not fullname:
            flash("Please provide your first and last name.", "error")
            return redirect(url_for('ssc_signup'))

        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        position = request.form.get('position', '').strip()
        password = request.form.get('password', '')

        # Password validation (optional, can add more rules)
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for('ssc_signup'))
        if not password.isalnum():
            flash("Password must contain only letters and numbers (alphanumeric).", "error")
            return redirect(url_for('ssc_signup'))

        # Duplicate check
        if SSC.query.filter_by(username=username).first():
            flash("Username already exists. Please choose another one.", "error")
            return redirect(url_for('ssc_signup'))
        if SSC.query.filter_by(email_address=email).first():
            flash("Email already registered. Please use a different email.", "error")
            return redirect(url_for('ssc_signup'))

        if email_exists_in_other_roles(email, current_role='ssc'):
            flash("Email is already used by another account type. Please use a different email.", "error")
            return redirect(url_for('ssc_signup'))

        # Handle profile image upload (optional)
        profile_image_file = request.files.get('profile_image')
        profile_image_filename = None
        if profile_image_file and profile_image_file.filename:
            print(f"[DEBUG] Profile image file received: {profile_image_file.filename}")
            profile_image_filename = f"ssc_profile_{username}_{secure_filename(profile_image_file.filename)}"
            profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_image_filename)
            profile_image_file.save(profile_image_path)
            print(f"[DEBUG] Profile image saved as: {profile_image_filename}")
        otp = str(random.randint(100000, 999999))
        session['ssc_data'] = {
            'fullname': fullname,
            'username': username,
            'email_address': email,
            'position': position,
            'password': password,
            'profile_image': profile_image_filename
        }
        session['ssc_otp'] = otp
        try:
            print(f"[DEBUG] Attempting to send OTP email to: {email}")
            msg = MailMessage('Your Guidance OTP Verification Code', recipients=[email])
            msg.body = f"Hello {fullname},\n\nYour OTP code is: {otp}\n\nThank you for registering as Guidance staff."
            mail.send(msg)
            print("[DEBUG] OTP email sent successfully")
            flash("OTP has been sent to your email address.", "info")
        except Exception as e:
            print(f"[MAIL ERROR] {e}")
            flash("Failed to send OTP. Please check email configuration.", "danger")
        return render_template('accounts/ssc_otp.html')
    return render_template('accounts/ssc_signup.html')

@app.route('/verify_ssc_otp', methods=['POST'])
def verify_ssc_otp():
    entered_otp = request.form['otp']
    actual_otp = session.get('ssc_otp')
    ssc_data = session.get('ssc_data')

    if entered_otp == actual_otp and ssc_data:
        # Check for duplicate email address
        existing_email = SSC.query.filter_by(email_address=ssc_data['email_address']).first()
        if existing_email:
            session.pop('ssc_otp', None)
            session.pop('ssc_data', None)
            flash("Email address is already registered. Please use a different email.", "danger")
            return redirect(url_for('ssc_signup'))

        if email_exists_in_other_roles(ssc_data['email_address'], current_role='ssc'):
            session.pop('ssc_otp', None)
            session.pop('ssc_data', None)
            flash("Email address is already used by another account type. Please use a different email.", "danger")
            return redirect(url_for('ssc_signup'))
        
        # Check for duplicate username
        existing_username = SSC.query.filter_by(username=ssc_data['username']).first()
        if existing_username:
            session.pop('ssc_otp', None)
            session.pop('ssc_data', None)
            flash("Username already exists. Please choose another username.", "danger")
            return redirect(url_for('ssc_signup'))
        
        try:
            new_ssc = SSC(
                fullname=ssc_data['fullname'],
                username=ssc_data['username'],
                email_address=ssc_data['email_address'],
                position=ssc_data['position'],
                password=generate_password_hash(ssc_data['password']),
                profile_image=ssc_data.get('profile_image'),
                status='pending'  # Set to pending for approval
            )
            db.session.add(new_ssc)
            db.session.commit()
            session.pop('ssc_otp', None)
            session.pop('ssc_data', None)
            flash("OTP verified! Your registration is pending admin approval.", "info")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            session.pop('ssc_otp', None)
            session.pop('ssc_data', None)
            # Check if it's a duplicate entry error
            if 'Duplicate entry' in str(e) or 'UNIQUE constraint' in str(e):
                flash("Email address is already registered. Please use a different email.", "danger")
            else:
                flash("An error occurred during registration. Please try again.", "danger")
            return redirect(url_for('ssc_signup'))
    else:
        flash("Your OTP was incorrect or expired.", "danger")
        return render_template('accounts/ssc_otp.html')

@app.route('/resend_ssc_otp')
def resend_ssc_otp():
    if 'ssc_data' in session:
        new_otp = str(random.randint(100000, 999999))
        session['ssc_otp'] = new_otp
        email = session['ssc_data']['email_address']
        fullname = session['ssc_data']['fullname']
        try:
            msg = MailMessage('Your New SSC OTP Code', recipients=[email])
            msg.body = f"Hello {fullname},\n\nYour new OTP code is: {new_otp}"
            mail.send(msg)
            flash("New OTP has been sent to your email.", "info")
        except Exception as e:
            print(f"[MAIL ERROR] {e}")
            flash("Failed to send new OTP email.", "danger")
        return render_template('accounts/ssc_otp.html')
    return redirect(url_for('ssc_signup'))

@app.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        # Gracefully handle missing fullname field by reconstructing it
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        fullname = request.form.get('fullname', '').strip()
        if not fullname:
            fullname = ' '.join(filter(None, [first_name, last_name])).strip()
        if not fullname:
            flash("Please provide your first and last name.", "error")
            return redirect(url_for('admin_signup'))

        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        # Password validation
        if len(password) < 8:
            flash("Password must be at least 8 characters long.", "error")
            return redirect(url_for('admin_signup'))
        if not password.isalnum():
            flash("Password must contain only letters and numbers (alphanumeric).", "error")
            return redirect(url_for('admin_signup'))

        # Duplicate check
        if Admin.query.filter_by(username=username).first():
            flash("Username already exists. Please choose another one.", "error")
            return redirect(url_for('admin_signup'))
        if Admin.query.filter_by(email_address=email).first():
            flash("Email already registered. Please use a different email.", "error")
            return redirect(url_for('admin_signup'))

        if email_exists_in_other_roles(email, current_role='admin'):
            flash("Email is already used by another account type. Please use a different email.", "error")
            return redirect(url_for('admin_signup'))

        # Handle profile image upload
        profile_image_file = request.files.get('profile_image')
        profile_image_filename = None
        if profile_image_file and profile_image_file.filename:
            profile_image_filename = f"admin_profile_{username}_{secure_filename(profile_image_file.filename)}"
            profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_image_filename)
            profile_image_file.save(profile_image_path)

        otp = str(random.randint(100000, 999999))
        session['admin_data'] = {
            'fullname': fullname,
            'username': username,
            'email_address': email,
            'password': password,
            'profile_image': profile_image_filename
        }
        session['admin_otp'] = otp

        try:
            msg = MailMessage('Your Admin OTP Verification Code', recipients=[email])
            msg.body = f"Hello {fullname},\n\nYour OTP code is: {otp}\n\nThank you for registering as Admin."
            mail.send(msg)
            flash("OTP has been sent to your email address.", "info")
        except Exception as e:
            print(f"[MAIL ERROR] {e}")
            flash("Failed to send OTP. Please check email configuration.", "danger")

        # Notify all admins (except the new one) about new admin registration
        new_admin = Admin.query.filter_by(username=username).first()
        for admin in Admin.query.all():
            if admin.id != (new_admin.id if new_admin else None):
                notif = Notification(
                    user_id=admin.id,
                    user_type='admin',
                    title='New Admin Registration',
                    message=f'{fullname} has registered as a new administrator.',
                    notification_type='user',
                    created_at=datetime.utcnow()
                )
                db.session.add(notif)
        db.session.commit()

        return render_template('accounts/admin_otp.html')
    return render_template('accounts/admin_signup.html')

@app.route('/verify_admin_otp', methods=['POST'])
def verify_admin_otp():
    entered_otp = request.form['otp']
    actual_otp = session.get('admin_otp')
    admin_data = session.get('admin_data')

    if entered_otp == actual_otp and admin_data:
        # Check for duplicate email address
        existing_email = Admin.query.filter_by(email_address=admin_data['email_address']).first()
        if existing_email:
            session.pop('admin_otp', None)
            session.pop('admin_data', None)
            flash("Email address is already registered. Please use a different email.", "danger")
            return redirect(url_for('admin_signup'))

        if email_exists_in_other_roles(admin_data['email_address'], current_role='admin'):
            session.pop('admin_otp', None)
            session.pop('admin_data', None)
            flash("Email address is already used by another account type. Please use a different email.", "danger")
            return redirect(url_for('admin_signup'))
        
        # Check for duplicate username
        existing_username = Admin.query.filter_by(username=admin_data['username']).first()
        if existing_username:
            session.pop('admin_otp', None)
            session.pop('admin_data', None)
            flash("Username already exists. Please choose another username.", "danger")
            return redirect(url_for('admin_signup'))
        
        try:
            new_admin = Admin(
                fullname=admin_data['fullname'],
                username=admin_data['username'],
                email_address=admin_data['email_address'],
                password=generate_password_hash(admin_data['password']),
                profile_image=admin_data.get('profile_image')
            )
            db.session.add(new_admin)
            db.session.commit()
            session.pop('admin_otp', None)
            session.pop('admin_data', None)
            # Notify all admins
            for admin in Admin.query.all():
                if admin.id != new_admin.id:
                    notif = Notification(
                        user_id=admin.id,
                        user_type='admin',
                        title='New Admin Registration',
                        message=f'{new_admin.fullname} has registered as a new administrator.',
                        notification_type='user',
                        created_at=datetime.utcnow()
                    )
                    db.session.add(notif)
            db.session.commit()
            flash("OTP verified and Admin registration completed!", "success")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            session.pop('admin_otp', None)
            session.pop('admin_data', None)
            # Check if it's a duplicate entry error
            if 'Duplicate entry' in str(e) or 'UNIQUE constraint' in str(e):
                flash("Email address is already registered. Please use a different email.", "danger")
            else:
                flash("An error occurred during registration. Please try again.", "danger")
            return redirect(url_for('admin_signup'))
    else:
        flash("Your OTP was incorrect or expired.", "danger")
        return render_template('accounts/admin_otp.html')

@app.route('/resend_admin_otp')
def resend_admin_otp():
    if 'admin_data' in session:
        new_otp = str(random.randint(100000, 999999))
        session['admin_otp'] = new_otp
        email = session['admin_data']['email_address']
        fullname = session['admin_data']['fullname']
        try:
            msg = MailMessage('Your New Admin OTP Code', recipients=[email])
            msg.body = f"Hello {fullname},\n\nYour new OTP code is: {new_otp}"
            mail.send(msg)
            flash("New OTP has been sent to your email.", "info")
        except Exception as e:
            print(f"[MAIL ERROR] {e}")
            flash("Failed to send new OTP email.", "danger")
        return render_template('accounts/admin_otp.html')
    return redirect(url_for('admin_signup'))

# -------------------- DASHBOARDS --------------------

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_type = session.get('user_type')
    if user_type == 'student':
        return redirect(url_for('student_dashboard'))
    elif user_type == 'ssc':
        return redirect(url_for('ssc_dashboard'))
    elif user_type == 'admin':
        return redirect(url_for('admin_dashboard'))
    else:
        flash("Invalid user type.", "error")
        return redirect(url_for('login'))

@app.route('/student_dashboard')
@login_required('student')
def student_dashboard():
    student_id = session['user_id']
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('login'))
    
    # Check if student is active
    if student.status != 'active':
        flash('Your account is not active. Please contact support.', 'error')
        return redirect(url_for('login'))
    
    # Get concern statistics
    total_concerns = Concern.query.filter_by(student_id=student_id).count()
    resolved_concerns = Concern.query.filter_by(student_id=student_id, status='resolved').count()
    pending_concerns = Concern.query.filter_by(student_id=student_id, status='pending').count()
    processing_concerns = Concern.query.filter_by(student_id=student_id, status='processing').count()
    
    # Sorting for recent concerns
    sort_order = request.args.get('sort', 'desc')  # 'desc' for newest first, 'asc' for oldest first
    if sort_order == 'asc':
        order_by = Concern.submitted_at.asc()
    else:
        order_by = Concern.submitted_at.desc()
    # Get recent concerns (last 5)
    recent_concerns = Concern.query.filter_by(student_id=student_id)\
        .order_by(order_by)\
        .limit(5)\
        .all()
    
    # Load active concern types for the form
    try:
        concern_types = ConcernType.query.filter_by(is_archived=False).order_by(ConcernType.name.asc()).all()
    except Exception:
        concern_types = []

    return render_template('students/student_dashboard.html', 
                         student=student,
                         total_concerns=total_concerns,
                         resolved_concerns=resolved_concerns,
                         pending_concerns=pending_concerns,
                         processing_concerns=processing_concerns,
                         recent_concerns=recent_concerns,
                         sort_order=sort_order,
                         concern_types=concern_types)

@app.route('/concern')
@login_required('student')
def concern():
    student_id = session['user_id']
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('login'))
    
    # Check if student is active
    if student.status != 'active':
        flash('Your account is not active. Please contact support.', 'error')
        return redirect(url_for('login'))
    
    # Get pending concerns count for limit check
    pending_concerns = Concern.query.filter_by(
        student_id=student_id, 
        status='pending'
    ).count()
    
    # Sorting for concerns list
    sort_order = request.args.get('sort', 'desc')  # 'desc' for newest first, 'asc' for oldest first
    if sort_order == 'asc':
        order_by = Concern.submitted_at.asc()
    else:
        order_by = Concern.submitted_at.desc()
    concerns = Concern.query.filter_by(student_id=student_id)\
        .order_by(order_by)\
        .all()

    # Load active concern types as well (for any dropdowns on this page in the future)
    try:
        concern_types = ConcernType.query.filter_by(is_archived=False).order_by(ConcernType.name.asc()).all()
    except Exception:
        concern_types = []

    return render_template('students/concern.html', 
                         student=student, 
                         concerns=concerns, 
                         sort_order=sort_order,
                         pending_concerns=pending_concerns,
                         concern_types=concern_types)

@app.route('/concern/<int:concern_id>/rate', methods=['POST'])
@login_required('student')
def rate_concern(concern_id):
    """Submit a rating and optional feedback for a guidance response."""
    concern = Concern.query.get_or_404(concern_id)
    # Ensure the concern belongs to the logged-in student
    if concern.student_id != session.get('user_id'):
        flash('Unauthorized action.', 'error')
        return redirect(request.referrer or url_for('student_dashboard'))

    try:
        rating_raw = request.form.get('rating')
        feedback = request.form.get('feedback', '').strip() or None
        rating_val = int(rating_raw) if rating_raw is not None else None

        if rating_val is None or rating_val < 1 or rating_val > 5:
            flash('Please select a rating between 1 and 5.', 'error')
            return redirect(request.referrer or url_for('student_dashboard'))

        concern.rating = rating_val
        concern.feedback = feedback
        concern.feedback_submitted_at = datetime.utcnow()
        concern.is_feedback_submitted = True
        db.session.commit()
        flash('Thank you for your feedback!', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Error submitting rating: {e}")
        flash('Error submitting feedback. Please try again.', 'error')

    return redirect(request.referrer or url_for('student_dashboard'))

@app.route('/concern_attachments/<int:concern_id>')
@login_required('student')
def view_concern_attachments(concern_id):
    """View all attachments for a specific concern"""
    student_id = session['user_id']
    
    # Get the concern and verify ownership
    concern = Concern.query.filter_by(id=concern_id, student_id=student_id).first()
    if not concern:
        flash('Concern not found or access denied.', 'error')
        return redirect(url_for('concern'))
    
    # Get all attachments for this concern
    attachments = ConcernAttachment.query.filter_by(concern_id=concern_id).all()
    
    return render_template('students/concern_attachments.html', 
                         concern=concern, 
                         attachments=attachments,
                         student=Student.query.get(student_id))

@app.route('/remove_attachment/<int:attachment_id>', methods=['POST'])
@login_required('student')
def remove_attachment(attachment_id):
    """Remove a specific attachment"""
    student_id = session['user_id']
    
    # Get the attachment and verify ownership
    attachment = ConcernAttachment.query.get(attachment_id)
    if not attachment:
        return jsonify({'success': False, 'message': 'Attachment not found'})
    
    # Verify the concern belongs to the student
    concern = Concern.query.filter_by(id=attachment.concern_id, student_id=student_id).first()
    if not concern:
        return jsonify({'success': False, 'message': 'Access denied'})
    
    # Only allow removal if concern is still pending
    if concern.status != 'pending':
        return jsonify({'success': False, 'message': 'Cannot remove attachments from processed concerns'})
    
    try:
        # Delete the physical file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], attachment.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete from database
        db.session.delete(attachment)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Attachment removed successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': f'Error removing attachment: {str(e)}'})

@app.route('/download_attachment/<int:attachment_id>')
@login_required('student')
def download_attachment(attachment_id):
    """Download a specific attachment"""
    student_id = session['user_id']
    
    # Get the attachment and verify ownership
    attachment = ConcernAttachment.query.get(attachment_id)
    if not attachment:
        flash('Attachment not found.', 'error')
        return redirect(url_for('concern'))
    
    # Verify the concern belongs to the student
    concern = Concern.query.filter_by(id=attachment.concern_id, student_id=student_id).first()
    if not concern:
        flash('Access denied.', 'error')
        return redirect(url_for('concern'))
    
    # Check if file exists
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], attachment.filename)
    if not os.path.exists(file_path):
        flash('File not found.', 'error')
        return redirect(url_for('concern'))
    
    return send_file(file_path, 
                    as_attachment=True, 
                    download_name=attachment.original_filename)

@app.route('/submit_concern', methods=['POST'])
@login_required('student')
def submit_concern():
    student_id = session['user_id']
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('concern'))
    
    # Check if student is active
    if student.status != 'active':
        flash('Your account is not active. Please contact support.', 'error')
        return redirect(url_for('concern'))
    
    # Check concern limit (1-2 pending concerns maximum)
    pending_concerns = Concern.query.filter_by(
        student_id=student_id, 
        status='pending'
    ).count()
    
    if pending_concerns >= 2:
        flash('You have reached the maximum limit of 2 pending concerns. Please wait for your existing concerns to be resolved before submitting a new one.', 'error')
        return redirect(url_for('concern'))
    
    # Get form data
    concern_type = request.form.get('concern-type')
    title = request.form.get('concern-title')
    description = request.form.get('concern-details')
    priority_level = request.form.get('concern-priority') or 'medium'  # SSC sets priority; default for new concerns
    
    # Handle multiple file uploads (up to 3 files)
    uploaded_files = []
    allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'}
    max_files = 3
    max_file_size = 10 * 1024 * 1024  # 10MB
    
    # Get all uploaded files
    files = request.files.getlist('docs')
    
    # Validate number of files
    if len(files) > max_files:
        flash(f'You can upload a maximum of {max_files} files.', 'error')
        return redirect(url_for('concern'))
    
    # Process each file
    for i, file in enumerate(files):
        if file and file.filename:
            # Validate file size
            if file.content_length and file.content_length > max_file_size:
                flash(f'File "{file.filename}" is too large. Maximum size is 10MB.', 'error')
                return redirect(url_for('concern'))
            
            # Validate file type
            file_ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
            if file_ext not in allowed_extensions:
                flash(f'File "{file.filename}" has an invalid type. Allowed: PDF, DOC, DOCX, JPG, PNG, TXT', 'error')
                return redirect(url_for('concern'))
            
            # Generate unique filename
            filename = f"concern_{student_id}_{i+1}_{secure_filename(file.filename)}"
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            
            # Save file
            file.save(upload_path)
            
            # Store file info
            uploaded_files.append({
                'filename': filename,
                'original_filename': file.filename,
                'file_size': file.content_length,
                'file_type': file_ext
            })
    
    # Validate required fields
    if not all([concern_type, title, description]):
        flash('All fields are required.', 'error')
        return redirect(url_for('concern'))
    
    # Create new concern
    # Calculate deadline (3 days from now)
    from datetime import datetime, timedelta
    deadline = datetime.utcnow() + timedelta(days=3)
    
    # Create concern with deadline (handle case where column doesn't exist yet)
    concern_data = {
        'student_id': student_id,
        'title': title,
        'description': description,
        'concern_type': concern_type,
        'priority_level': priority_level,
        'status': 'pending',
        'docs': None  # Legacy field, we'll use attachments instead
    }
    
    # Try to add deadline, but don't fail if column doesn't exist
    try:
        concern_data['deadline'] = deadline
    except Exception as e:
        print(f"Could not set deadline (column may not exist): {e}")
    
    new_concern = Concern(**concern_data)
    
    try:
        db.session.add(new_concern)
        db.session.flush()  # Get the concern ID
        
        # Add attachments to database
        for file_info in uploaded_files:
            attachment = ConcernAttachment(
                concern_id=new_concern.id,
                filename=file_info['filename'],
                original_filename=file_info['original_filename'],
                file_size=file_info['file_size'],
                file_type=file_info['file_type']
            )
            db.session.add(attachment)
        
        db.session.commit()
        
        # Add to concern history (audit: who submitted, when)
        history = ConcernHistory(
            concern_id=new_concern.id,
            status='pending',
            action='Concern submitted by student',
            timestamp=datetime.utcnow(),
            actor_type='student',
            actor_id=student_id,
            actor_name=student.fullname
        )
        db.session.add(history)
        # Create notifications for Guidance leads (Coordinator/Supervisor)
        ssc_staff = SSC.query.all()
        leads = []
        for s in ssc_staff:
            pos_norm = ' '.join(((s.position or '').replace('_',' ').replace('-',' ').lower()).split())
            if ('guidance coordinator' in pos_norm) or ('guidance supervisor' in pos_norm):
                leads.append(s)
        # Fallback: if no leads configured, notify all SSC
        recipients = leads if leads else ssc_staff
        for s in recipients:
            notification = Notification(
                user_id=s.id,
                user_type='ssc',
                title='New Concern Submitted',
                message=f'New concern #{new_concern.id}: "{title}" ({priority_level.title()}) by {student.fullname}.',
                notification_type='concern_update',
                concern_id=new_concern.id,
                created_at=datetime.utcnow()
            )
            db.session.add(notification)
        # Notify all admins
        for admin in Admin.query.all():
            notif = Notification(
                user_id=admin.id,
                user_type='admin',
                title='New Concern Submitted',
                message=f'A new concern regarding {concern_type} was submitted by {Student.query.get(student_id).fullname}.',
                notification_type='concern_update',
                concern_id=new_concern.id,
                created_at=datetime.utcnow()
            )
            db.session.add(notif)
        db.session.commit()
        flash('Your concern is submitted and must be reviewed.', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Error submitting concern: {e}")
        flash('Error submitting concern. Please try again.', 'error')
    return redirect(url_for('student_dashboard'))

@app.route('/notifications')
@login_required('student')
def notifications():
    student_id = session['user_id']
    student = Student.query.get(student_id)
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('login'))
    
    # Check if student is active
    if student.status != 'active':
        flash('Your account is not active. Please contact support.', 'error')
        return redirect(url_for('login'))
    notif_type = request.args.get('type', 'all')
    notifications_query = Notification.query.filter_by(user_id=student_id, user_type='student')
    if notif_type != 'all':
        notifications_query = notifications_query.filter_by(notification_type=notif_type)
    notifications = notifications_query.order_by(Notification.created_at.desc()).all()
    # Get unread count for different types
    unread_concerns = sum(1 for n in notifications if not n.is_read and n.notification_type == 'concern_update')
    unread_system = sum(1 for n in notifications if not n.is_read and n.notification_type == 'system')
    unread_general = sum(1 for n in notifications if not n.is_read and n.notification_type == 'general')
    return render_template('students/notifications.html',
                         student=student,
                         notifications=notifications,
                         unread_concerns=unread_concerns,
                         unread_system=unread_system,
                         unread_general=unread_general,
                         notif_type=notif_type)

@app.route('/mark_notification_read/<int:notification_id>', methods=['POST'])
def mark_notification_read(notification_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    notification = Notification.query.get_or_404(notification_id)
    
    # Verify the notification belongs to the current user
    if notification.user_id != session['user_id'] or notification.user_type != session['user_type']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Additional validation for students
    if session['user_type'] == 'student':
        student = Student.query.get(session['user_id'])
        if not student or student.status != 'active':
            return jsonify({'error': 'Account not active'}), 403
    
    try:
        notification.is_read = True
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/delete_notification/<int:notification_id>', methods=['POST'])
def delete_notification(notification_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    notification = Notification.query.get_or_404(notification_id)
    
    # Verify the notification belongs to the current user
    if notification.user_id != session['user_id'] or notification.user_type != session['user_type']:
        return jsonify({'error': 'Unauthorized'}), 403
    
    # Additional validation for students
    if session['user_type'] == 'student':
        student = Student.query.get(session['user_id'])
        if not student or student.status != 'active':
            return jsonify({'error': 'Account not active'}), 403
    
    try:
        db.session.delete(notification)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/ssc_dashboard')
@login_required('ssc')
def ssc_dashboard():
    ssc = SSC.query.get(session['user_id'])
    filter_value = request.args.get('filter', 'all')
    concerns_query = Concern.query
    if filter_value == 'pending':
        concerns_query = concerns_query.filter_by(status='pending')
    elif filter_value == 'processing':
        concerns_query = concerns_query.filter_by(status='processing')
    elif filter_value == 'resolved':
        concerns_query = concerns_query.filter_by(status='resolved')
    concerns = concerns_query.order_by(Concern.submitted_at.desc()).all()
    total_concerns = Concern.query.count()
    pending = Concern.query.filter_by(status='pending').count()
    processing = Concern.query.filter_by(status='processing').count()
    resolved = Concern.query.filter_by(status='resolved').count()
    return render_template(
        'ssc/ssc_dashboard.html',
        concerns=concerns,
        total_concerns=total_concerns,
        pending=pending,
        processing=processing,
        resolved=resolved,
        ssc=ssc,
        filter=filter_value
    )

@app.route('/ssc_concerns')
@login_required('ssc')
def ssc_concerns():
    ssc = SSC.query.get(session['user_id'])
    check_overdue_concerns()
    
    search = request.args.get('search', '').strip()
    status_filter = request.args.get('status', '').strip()
    priority_filter = request.args.get('priority', '').strip().lower()
    page = request.args.get('page', 1, type=int)
    per_page = 15
    
    concerns_query = Concern.query
    
    if search:
        concerns_query = concerns_query.filter(
            (Concern.title.ilike(f'%{search}%')) |
            (Concern.description.ilike(f'%{search}%')) |
            (Concern.concern_type.ilike(f'%{search}%')) |
            (Concern.student.has(Student.fullname.ilike(f'%{search}%'))) |
            (Concern.student.has(Student.student_id_number.ilike(f'%{search}%')))
        )
    
    if status_filter and status_filter.lower() != 'all':
        if status_filter.lower() == 'overdue':
            from datetime import datetime
            now = datetime.utcnow()
            try:
                concerns_query = concerns_query.filter(
                    Concern.deadline < now,
                    Concern.status != 'resolved'
                )
            except Exception as e:
                print(f"Deadline column not found, skipping overdue filter: {e}")
                concerns_query = concerns_query.filter(Concern.status == 'pending')
        else:
            concerns_query = concerns_query.filter(Concern.status == status_filter.lower())
    
    # Priority counts from base filtered set (no priority filter)
    base_for_count = concerns_query
    count_low = base_for_count.filter(Concern.priority_level.ilike('low')).count()
    count_medium = base_for_count.filter(Concern.priority_level.ilike('medium')).count()
    count_high = base_for_count.filter(Concern.priority_level.ilike('high')).count()
    count_urgent = base_for_count.filter(Concern.priority_level.ilike('urgent')).count()
    
    if priority_filter in ('low', 'medium', 'high', 'urgent'):
        concerns_query = concerns_query.filter(Concern.priority_level.ilike(priority_filter))
    
    concerns_query = concerns_query.order_by(Concern.submitted_at.desc())
    pagination_obj = concerns_query.paginate(page=page, per_page=per_page)
    concerns = pagination_obj.items
    
    return render_template('ssc/ssc_concern.html', 
                         concerns=concerns, 
                         ssc=ssc, 
                         search=search, 
                         status_filter=status_filter,
                         priority_filter=priority_filter,
                         count_low=count_low,
                         count_medium=count_medium,
                         count_high=count_high,
                         count_urgent=count_urgent,
                         pagination=pagination_obj)

@app.route('/ssc_students')
@login_required('ssc')
def ssc_students():
    ssc = SSC.query.get(session['user_id'])
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '').strip()
    department = request.args.get('department', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 10
    students_query = Student.query
    if search:
        students_query = students_query.filter(
            (Student.fullname.ilike(f'%{search}%')) |
            (Student.email_address.ilike(f'%{search}%')) |
            (Student.student_id_number.ilike(f'%{search}%')) |
            (Student.course.ilike(f'%{search}%')) |
            (Student.year_lvl.ilike(f'%{search}%'))
        )
    if status == 'online':
        students_query = students_query.filter_by(is_online=True)
    elif status == 'offline':
        students_query = students_query.filter_by(is_online=False)
    if department:
        students_query = students_query.filter(Student.college_dept == department)
    students_query = students_query.order_by(Student.id.desc())
    pagination = students_query.paginate(page=page, per_page=per_page, error_out=False)
    students = pagination.items
    total_students = pagination.total
    # Department list for filter dropdown
    all_departments = ['CCS', 'COE', 'CTE', 'CAS', 'CBAA', 'CONAH', 'CIHMT', 'CIT', 'CCJE']
    return render_template(
        'ssc/ssc_student.html',
        students=students,
        search=search,
        status=status,
        department=department,
        ssc=ssc,
        pagination=pagination,
        total_students=total_students,
        all_departments=all_departments
    )

@app.route('/ssc_notifications')
@login_required('ssc')
def ssc_notifications():
    ssc = SSC.query.get(session['user_id'])
    filter_value = request.args.get('filter', 'all')
    sort_value = request.args.get('sort', 'desc')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    # Show ONLY notifications for the logged-in SSC
    query = Notification.query.filter_by(user_type='ssc', user_id=ssc.id)
    if filter_value == 'read':
        query = query.filter(Notification.is_read == True)
    elif filter_value == 'unread':
        query = query.filter(Notification.is_read == False)
    if sort_value == 'asc':
        query = query.order_by(Notification.created_at.asc())
    else:
        query = query.order_by(Notification.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page)
    notifications = pagination.items
    concerns = Concern.query.order_by(Concern.submitted_at.desc()).all()
    return render_template('ssc/ssc_notifications.html', notifications=notifications, concerns=concerns, ssc=ssc, filter=filter_value, sort=sort_value, pagination=pagination)

@app.route('/admin_dashboard')
@login_required('admin')
def admin_dashboard():
    admin = Admin.query.get(session['user_id'])
    total_students = Student.query.count()
    total_ssc = SSC.query.count()
    total_users = total_students + total_ssc
    # Only count concerns that are not resolved as active
    active_concerns = Concern.query.filter(Concern.status != 'resolved').count()
    resolved_concerns = Concern.query.filter_by(status='resolved').count()
    # Recent activities: last 5 student/ssc registrations and concern submissions
    recent_students = Student.query.order_by(Student.id.desc()).limit(3).all()
    recent_ssc = SSC.query.order_by(SSC.id.desc()).limit(2).all()
    recent_concerns = Concern.query.order_by(Concern.submitted_at.desc()).limit(5).all()
    recent_activities = []
    for s in recent_students:
        recent_activities.append({
            'type': 'student',
            'title': f"New Student Registration: {s.fullname}",
            'time': getattr(s, 'created_at', None),
            'department': s.college_dept,
            'course': s.course
        })
    for s in recent_ssc:
        recent_activities.append({
            'type': 'ssc',
            'title': f"New Guidance Registration: {s.fullname}",
            'time': getattr(s, 'created_at', None),
            'position': s.position
        })
    for c in recent_concerns:
        recent_activities.append({
            'type': 'concern',
            'title': f"New Concern: {c.title}",
            'time': c.submitted_at,
            'status': c.status,
            'resolution_notes': c.resolution_notes
        })
    # Sort by time, newest first
    recent_activities = sorted([a for a in recent_activities if a['time']], key=lambda x: x['time'], reverse=True)[:5]
    return render_template('admin/admin_dashboard.html', total_users=total_users, active_concerns=active_concerns, resolved_concerns=resolved_concerns, recent_activities=recent_activities, admin=admin)

@app.route('/user_management')
@login_required('admin')
def user_management():
    search = request.args.get('search', '').strip()
    role = request.args.get('role', '').strip()
    status = request.args.get('status', '').strip()
    students_query = Student.query
    sscs_query = SSC.query
    admins_query = Admin.query
    if search:
        students_query = students_query.filter((Student.fullname.ilike(f'%{search}%')) | (Student.email_address.ilike(f'%{search}%')))
        sscs_query = sscs_query.filter((SSC.fullname.ilike(f'%{search}%')) | (SSC.email_address.ilike(f'%{search}%')))
        admins_query = admins_query.filter((Admin.fullname.ilike(f'%{search}%')) | (Admin.email_address.ilike(f'%{search}%')))
    if status == 'online':
        students_query = students_query.filter_by(is_online=True)
        sscs_query = sscs_query.filter_by(is_online=True)
    elif status == 'offline':
        students_query = students_query.filter_by(is_online=False)
        sscs_query = sscs_query.filter_by(is_online=False)
    students = students_query.all() if role == '' or role == 'student' else []
    sscs = sscs_query.all() if role == '' or role == 'ssc' else []
    admins = admins_query.all() if role == '' or role == 'admin' else []
    total_students = Student.query.count()
    admin = Admin.query.get(session['user_id'])
    return render_template(
        'admin/user_management.html',
        students=students,
        sscs=sscs,
        admins=admins,
        total_students=total_students,
        search=search,
        role=role,
        status=status,
        admin=admin
    )

@app.route('/admin_concern')
@login_required('admin')
def admin_concern():
    status_filter = request.args.get('status', '').strip()
    sort_by = request.args.get('sort', 'date').strip()
    concern_type_filter = request.args.get('concern_type', '').strip()
    # Count for stat cards
    resolved_count = Concern.query.filter_by(status='resolved').count()
    processing_count = Concern.query.filter_by(status='processing').count()
    pending_count = Concern.query.filter_by(status='pending').count()
    concerns = Concern.query
    if status_filter:
        concerns = concerns.filter_by(status=status_filter)
    if concern_type_filter:
        concerns = concerns.filter_by(concern_type=concern_type_filter)
    if sort_by == 'priority':
        concerns = concerns.order_by(Concern.priority_level.desc())
    elif sort_by == 'status':
        concerns = concerns.order_by(Concern.status)
    else:
        concerns = concerns.order_by(Concern.submitted_at.desc())
    concerns = concerns.all()
    admin = Admin.query.get(session['user_id'])
    
    # Load active concern types for filter dropdown
    try:
        concern_types = ConcernType.query.filter_by(is_archived=False).order_by(ConcernType.name.asc()).all()
    except Exception:
        concern_types = []
    
    return render_template('admin/admin_concern.html', concerns=concerns, resolved_count=resolved_count, processing_count=processing_count, pending_count=pending_count, status_filter=status_filter, sort_by=sort_by, concern_type_filter=concern_type_filter, admin=admin, concern_types=concern_types)

@app.route('/admin_notification')
@login_required('admin')
def admin_notification():
    admin = Admin.query.get(session['user_id'])
    page = request.args.get('page', 1, type=int)
    per_page = 15
    admin_notifications = Notification.query.filter_by(user_type='admin', user_id=admin.id).all()
    recent_students = Student.query.order_by(Student.id.desc()).limit(50).all()
    recent_ssc = SSC.query.order_by(SSC.id.desc()).limit(30).all()
    recent_concerns = Concern.query.order_by(Concern.submitted_at.desc()).limit(50).all()
    recent_activities = []
    for s in recent_students:
        recent_activities.append({
            'type': 'student',
            'title': f"New Student Registration: {s.fullname}",
            'time': getattr(s, 'created_at', None),
            'department': s.college_dept,
            'course': s.course
        })
    for s in recent_ssc:
        recent_activities.append({
            'type': 'ssc',
            'title': f"New Guidance Registration: {s.fullname}",
            'time': getattr(s, 'created_at', None),
            'position': s.position
        })
    for c in recent_concerns:
        recent_activities.append({
            'type': 'concern',
            'title': f"New Concern: {c.title}",
            'time': c.submitted_at,
            'status': c.status,
            'resolution_notes': c.resolution_notes
        })
    for n in admin_notifications:
        activity = {
            'type': 'notification',
            'title': n.title,
            'time': n.created_at,
            'message': n.message
        }
        if n.title == 'New Student Registration' and n.message:
            match = re.search(r'^(.+?)\s+has registered', n.message)
            if match:
                student_name = match.group(1).strip()
                student = Student.query.filter_by(fullname=student_name).first()
                if student:
                    activity['type'] = 'student'
                    activity['department'] = student.college_dept
                    activity['course'] = student.course
        elif n.title == 'New SSC Registration' and n.message:
            match = re.search(r'^(.+?)\s+has registered', n.message)
            if match:
                ssc_name = match.group(1).strip()
                ssc = SSC.query.filter_by(fullname=ssc_name).first()
                if ssc:
                    activity['type'] = 'ssc'
                    activity['position'] = ssc.position
        recent_activities.append(activity)
    recent_activities = sorted([a for a in recent_activities if a.get('time')], key=lambda x: x['time'], reverse=True)
    total = len(recent_activities)
    pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, pages))
    start = (page - 1) * per_page
    recent_activities_page = recent_activities[start:start + per_page]
    pagination = {
        'page': page, 'pages': pages, 'total': total,
        'has_prev': page > 1, 'has_next': page < pages,
        'prev_num': page - 1, 'next_num': page + 1,
        'iter_pages': _iter_pages_list(page, pages)
    }
    return render_template('admin/admin_notification.html', admin=admin, recent_activities=recent_activities_page, pagination=pagination)

def _iter_pages_list(current_page, total_pages, left_edge=1, right_edge=1, left_current=2, right_current=2):
    """Return list of page numbers for pagination (None = ellipsis)."""
    if total_pages <= 1:
        return []
    result = []
    for p in range(1, total_pages + 1):
        if p <= left_edge or p > total_pages - right_edge or (current_page - left_current <= p <= current_page + right_current):
            result.append(p)
        elif result and result[-1] is not None:
            result.append(None)
    return result

@app.route('/admin_activities')
@login_required('admin')
def admin_activities():
    admin = Admin.query.get(session['user_id'])
    page = request.args.get('page', 1, type=int)
    per_page = 15
    # Same sources as Notifications page so Activities reflects everything from Notifications
    students = Student.query.order_by(Student.id.desc()).limit(100).all()
    sscs = SSC.query.order_by(SSC.id.desc()).limit(50).all()
    concerns = Concern.query.order_by(Concern.submitted_at.desc()).limit(100).all()
    admin_notifications = Notification.query.filter_by(user_type='admin', user_id=admin.id).order_by(Notification.created_at.desc()).all()
    activities = []
    for s in students:
        activities.append({
            'type': 'student',
            'title': f"New Student Registration: {s.fullname}",
            'time': getattr(s, 'created_at', None),
            'student_id': s.id,
            'department': s.college_dept,
            'course': s.course
        })
    for s in sscs:
        activities.append({
            'type': 'ssc',
            'title': f"New Guidance Registration: {s.fullname}",
            'time': getattr(s, 'created_at', None),
            'ssc_id': s.id,
            'position': s.position
        })
    for c in concerns:
        activities.append({
            'type': 'concern',
            'title': f"New Concern: {c.title}",
            'time': c.submitted_at,
            'status': c.status,
            'resolution_notes': c.resolution_notes,
            'concern_id': c.id
        })
    # Include all admin notifications (so everything on Notifications page appears in Activities)
    for n in admin_notifications:
        activity = {
            'type': 'notification',
            'title': n.title,
            'time': n.created_at,
            'message': n.message,
            'concern_id': n.concern_id
        }
        if n.title == 'New Student Registration' and n.message:
            match = re.search(r'^(.+?)\s+has registered', n.message)
            if match:
                student_name = match.group(1).strip()
                student = Student.query.filter_by(fullname=student_name).first()
                if student:
                    activity['type'] = 'student'
                    activity['student_id'] = student.id
                    activity['department'] = student.college_dept
                    activity['course'] = student.course
        elif n.title == 'New SSC Registration' and n.message:
            match = re.search(r'^(.+?)\s+has registered', n.message)
            if match:
                ssc_name = match.group(1).strip()
                ssc = SSC.query.filter_by(fullname=ssc_name).first()
                if ssc:
                    activity['type'] = 'ssc'
                    activity['ssc_id'] = ssc.id
                    activity['position'] = ssc.position
        activities.append(activity)
    activities = sorted([a for a in activities if a.get('time')], key=lambda x: x['time'], reverse=True)
    total = len(activities)
    pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, pages))
    start = (page - 1) * per_page
    activities_page = activities[start:start + per_page]
    pagination = {
        'page': page, 'pages': pages, 'total': total,
        'has_prev': page > 1, 'has_next': page < pages,
        'prev_num': page - 1, 'next_num': page + 1,
        'iter_pages': _iter_pages_list(page, pages)
    }
    return render_template('admin/admin_activities.html', activities=activities_page, pagination=pagination)

@app.route('/admin/concern/<int:concern_id>')
@login_required('admin')
def admin_view_concern(concern_id):
    concern = Concern.query.get_or_404(concern_id)
    admin = Admin.query.get(session['user_id'])
    timeline = ConcernHistory.query.filter_by(concern_id=concern.id).order_by(ConcernHistory.timestamp.desc()).all()
    return render_template('admin/admin_concern_detail.html', concern=concern, admin=admin, timeline=timeline)

@app.route('/admin/resolve_concern/<int:concern_id>', methods=['POST'])
@login_required('admin')
def admin_resolve_concern(concern_id):
    concern = Concern.query.get_or_404(concern_id)
    resolution_notes = request.form.get('resolution_notes', '').strip()
    
    if not resolution_notes:
        flash('Resolution notes are required.', 'error')
        return redirect(url_for('admin_view_concern', concern_id=concern_id))
    
    concern.status = 'resolved'
    concern.resolution_notes = resolution_notes
    concern.resolved_by = session['user_id']
    concern.resolved_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # Add to concern history (audit: who resolved, when)
        resolving_admin = Admin.query.get(session['user_id'])
        history = ConcernHistory(
            concern_id=concern.id,
            status='resolved',
            action=f'Concern resolved by admin: {resolution_notes[:50]}{"..." if len(resolution_notes) > 50 else ""}',
            timestamp=datetime.utcnow(),
            actor_type='admin',
            actor_id=session['user_id'],
            actor_name=resolving_admin.fullname if resolving_admin else 'Admin'
        )
        db.session.add(history)
        
        # Notify all admins
        for admin in Admin.query.all():
            if admin.id != session['user_id']:  # Don't notify the resolving admin
                notif = Notification(
                    user_id=admin.id,
                    user_type='admin',
                    title='Concern Resolved',
                    message=f'Admin {session.get("admin_fullname", "Admin")} resolved concern "{concern.title}".',
                    notification_type='concern_update',
                    concern_id=concern.id,
                    created_at=datetime.utcnow()
                )
                db.session.add(notif)
        
        # Notify the student
        student = concern.student
        notif_student = Notification(
            user_id=student.id,
            user_type='student',
            title='Concern Resolved',
            message=f'Your concern "{concern.title}" has been resolved by an administrator.',
            notification_type='concern_update',
            concern_id=concern.id,
            created_at=datetime.utcnow()
        )
        db.session.add(notif_student)
        
        db.session.commit()
        
        # Send email notification
        if student.email_address:
            admin_name = session.get('admin_fullname') or 'Admin'
            has_attachment = concern.response_attachment is not None
            send_concern_reply_email(student.email_address, student.fullname, concern.title, resolution_notes, admin_name, 'Admin', has_attachment)
        
        flash('Concern resolved successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error resolving concern. Please try again.', 'error')
        print(f"Error in admin_resolve_concern: {e}")
    
    return redirect(url_for('admin_view_concern', concern_id=concern_id))

@app.route('/admin/respond_concern/<int:concern_id>', methods=['POST'])
@login_required('admin')
def admin_respond_concern(concern_id):
    concern = Concern.query.get_or_404(concern_id)
    response = request.form.get('response', '').strip()
    
    if not response:
        flash('Response is required.', 'error')
        return redirect(url_for('admin_view_concern', concern_id=concern_id))
    
    # Update concern status to processing
    concern.status = 'processing'
    concern.response_notes = response
    concern.responded_by = session['user_id']
    concern.responded_at = datetime.utcnow()
    
    # Handle file attachment if provided
    attachment_file = request.files.get('attachment')
    if attachment_file and attachment_file.filename:
        # Validate file size (max 10MB)
        if attachment_file.content_length and attachment_file.content_length > 10 * 1024 * 1024:
            flash('File size must be less than 10MB.', 'error')
            return redirect(url_for('admin_view_concern', concern_id=concern_id))
        
        # Validate file type
        allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'}
        file_ext = attachment_file.filename.rsplit('.', 1)[1].lower() if '.' in attachment_file.filename else ''
        if file_ext not in allowed_extensions:
            flash('Invalid file type. Allowed: PDF, DOC, DOCX, JPG, PNG, TXT', 'error')
            return redirect(url_for('admin_view_concern', concern_id=concern_id))
        
        # Save attachment
        admin_id = session['user_id']
        attachment_filename = f"admin_response_{admin_id}_{concern_id}_{secure_filename(attachment_file.filename)}"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], attachment_filename)
        attachment_file.save(upload_path)
        concern.response_attachment = attachment_filename
    
    try:
        db.session.commit()
        
        # Add to concern history (audit: who responded)
        responding_admin = Admin.query.get(session['user_id'])
        history = ConcernHistory(
            concern_id=concern.id,
            status='processing',
            action=f'Admin responded: {response[:50]}{"..." if len(response) > 50 else ""}',
            timestamp=datetime.utcnow(),
            actor_type='admin',
            actor_id=session['user_id'],
            actor_name=responding_admin.fullname if responding_admin else 'Admin'
        )
        db.session.add(history)
        
        # Notify the student
        student = concern.student
        notif_student = Notification(
            user_id=student.id,
            user_type='student',
            title='Admin Response to Your Concern',
            message=f'An admin has responded to your concern "{concern.title}".',
            notification_type='concern_update',
            concern_id=concern.id,
            created_at=datetime.utcnow()
        )
        db.session.add(notif_student)
        
        # Notify all admins
        for admin in Admin.query.all():
            if admin.id != session['user_id']:  # Don't notify the responding admin
                notif_admin = Notification(
                    user_id=admin.id,
                    user_type='admin',
                    title='Concern Response',
                    message=f'Admin {session.get("admin_fullname", "Admin")} responded to concern "{concern.title}".',
                    notification_type='concern_update',
                    concern_id=concern.id,
                    created_at=datetime.utcnow()
                )
                db.session.add(notif_admin)
        
        db.session.commit()
        
        # Send email notification to student
        if student.email_address:
            admin_name = session.get('admin_fullname') or 'Admin'
            has_attachment = concern.response_attachment is not None
            send_concern_reply_email(student.email_address, student.fullname, concern.title, response, admin_name, 'Admin', has_attachment)
        
        flash('Response sent successfully! Concern is now being processed.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error sending response. Please try again.', 'error')
        print(f"Error in admin_respond_concern: {e}")
    
    return redirect(url_for('admin_view_concern', concern_id=concern_id))

@app.route('/admin/update_response/<int:concern_id>', methods=['POST'])
@login_required('admin')
def admin_update_response(concern_id):
    concern = Concern.query.get_or_404(concern_id)
    new_response = request.form.get('response', '').strip()
    
    if not new_response:
        flash('Response is required.', 'error')
        return redirect(url_for('admin_view_concern', concern_id=concern_id))
    
    # Store the old response for history
    old_response = concern.response_notes
    
    # Update the response
    concern.response_notes = new_response
    concern.responded_by = session['user_id']
    concern.responded_at = datetime.utcnow()
    
    # Handle file attachment if provided
    attachment_file = request.files.get('attachment')
    if attachment_file and attachment_file.filename:
        # Validate file size (max 10MB)
        if attachment_file.content_length and attachment_file.content_length > 10 * 1024 * 1024:
            flash('File size must be less than 10MB.', 'error')
            return redirect(url_for('admin_view_concern', concern_id=concern_id))
        
        # Validate file type
        allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'}
        file_ext = attachment_file.filename.rsplit('.', 1)[1].lower() if '.' in attachment_file.filename else ''
        if file_ext not in allowed_extensions:
            flash('Invalid file type. Allowed: PDF, DOC, DOCX, JPG, PNG, TXT', 'error')
            return redirect(url_for('admin_view_concern', concern_id=concern_id))
        
        # Save attachment
        admin_id = session['user_id']
        attachment_filename = f"admin_response_{admin_id}_{concern_id}_{secure_filename(attachment_file.filename)}"
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], attachment_filename)
        attachment_file.save(upload_path)
        concern.response_attachment = attachment_filename
    
    try:
        db.session.commit()
        
        # Add to concern history (audit)
        updating_admin = Admin.query.get(session['user_id'])
        history = ConcernHistory(
            concern_id=concern.id,
            status=concern.status,
            action=f'Admin updated response: {new_response[:50]}{"..." if len(new_response) > 50 else ""}',
            timestamp=datetime.utcnow(),
            actor_type='admin',
            actor_id=session['user_id'],
            actor_name=updating_admin.fullname if updating_admin else 'Admin'
        )
        db.session.add(history)
        
        # Notify the student
        student = concern.student
        notif_student = Notification(
            user_id=student.id,
            user_type='student',
            title='Admin Updated Response to Your Concern',
            message=f'An admin has updated their response to your concern "{concern.title}".',
            notification_type='concern_update',
            concern_id=concern.id,
            created_at=datetime.utcnow()
        )
        db.session.add(notif_student)
        
        # Notify all admins
        for admin in Admin.query.all():
            if admin.id != session['user_id']:  # Don't notify the updating admin
                notif_admin = Notification(
                    user_id=admin.id,
                    user_type='admin',
                    title='Concern Response Updated',
                    message=f'Admin {session.get("admin_fullname", "Admin")} updated response to concern "{concern.title}".',
                    notification_type='concern_update',
                    concern_id=concern.id,
                    created_at=datetime.utcnow()
                )
                db.session.add(notif_admin)
        
        db.session.commit()
        
        # Send email notification to student
        if student.email_address:
            admin_name = session.get('admin_fullname') or 'Admin'
            has_attachment = concern.response_attachment is not None
            send_concern_reply_email(student.email_address, student.fullname, concern.title, new_response, admin_name, 'Admin', has_attachment)
        
        flash('Response updated successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error updating response. Please try again.', 'error')
        print(f"Error in admin_update_response: {e}")
    
    return redirect(url_for('admin_view_concern', concern_id=concern_id))

@app.route('/admin/reject_concern/<int:concern_id>', methods=['POST'])
@login_required('admin')
def admin_reject_concern(concern_id):
    concern = Concern.query.get_or_404(concern_id)
    rejection_reason = request.form.get('rejection_reason', '').strip()
    
    if not rejection_reason:
        flash('Rejection reason is required.', 'error')
        return redirect(url_for('admin_view_concern', concern_id=concern_id))
    
    concern.status = 'rejected'
    concern.rejection_reason = rejection_reason
    concern.rejected_by = session['user_id']
    concern.rejected_at = datetime.utcnow()
    
    try:
        db.session.commit()
        
        # Add to concern history (audit)
        rejecting_admin = Admin.query.get(session['user_id'])
        history = ConcernHistory(
            concern_id=concern.id,
            status='rejected',
            action=f'Concern rejected by admin: {rejection_reason[:50]}{"..." if len(rejection_reason) > 50 else ""}',
            timestamp=datetime.utcnow(),
            actor_type='admin',
            actor_id=session['user_id'],
            actor_name=rejecting_admin.fullname if rejecting_admin else 'Admin'
        )
        db.session.add(history)
        
        # Notify the student
        student = concern.student
        notif_student = Notification(
            user_id=student.id,
            user_type='student',
            title='Concern Rejected',
            message=f'Your concern "{concern.title}" has been rejected. Reason: {rejection_reason}',
            notification_type='concern_update',
            concern_id=concern.id,
            created_at=datetime.utcnow()
        )
        db.session.add(notif_student)
        
        # Notify all admins
        for admin in Admin.query.all():
            if admin.id != session['user_id']:  # Don't notify the rejecting admin
                notif_admin = Notification(
                    user_id=admin.id,
                    user_type='admin',
                    title='Concern Rejected',
                    message=f'Admin {session.get("admin_fullname", "Admin")} rejected concern "{concern.title}".',
                    notification_type='concern_update',
                    concern_id=concern.id,
                    created_at=datetime.utcnow()
                )
                db.session.add(notif_admin)
        
        db.session.commit()
        
        # Send email notification to student
        if student.email_address:
            admin_name = session.get('admin_fullname') or 'Admin'
            send_concern_reply_email(student.email_address, student.fullname, concern.title, f"Your concern has been rejected. Reason: {rejection_reason}", admin_name, 'Admin', False)
        
        flash('Concern rejected successfully!', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Error rejecting concern. Please try again.', 'error')
        print(f"Error in admin_reject_concern: {e}")
    
    return redirect(url_for('admin_view_concern', concern_id=concern_id))



@app.route('/admin/user_approval')
@login_required('admin')
def admin_user_approval():
    sort = request.args.get('sort', 'pending').strip()
    search = request.args.get('search', '').strip()
    course_filter = request.args.get('course', '').strip()
    department_filter = request.args.get('department', '').strip()
    
    student_query = Student.query
    ssc_query = SSC.query
    
    if sort == 'approved':
        student_query = student_query.filter_by(status='active')
        ssc_query = ssc_query.filter_by(status='active')
    elif sort == 'rejected':
        student_query = student_query.filter_by(status='rejected')
        ssc_query = ssc_query.filter_by(status='rejected')
    else:
        student_query = student_query.filter_by(status='pending')
        ssc_query = ssc_query.filter_by(status='pending')
    
    if search:
        search_pattern = f"%{search}%"
        student_query = student_query.filter(
            (Student.fullname.ilike(search_pattern)) |
            (Student.email_address.ilike(search_pattern)) |
            (Student.student_id_number.ilike(search_pattern))
        )
        ssc_query = ssc_query.filter(
            (SSC.fullname.ilike(search_pattern)) |
            (SSC.email_address.ilike(search_pattern)) |
            (SSC.position.ilike(search_pattern))
        )
    
    # Apply course filter
    if course_filter:
        student_query = student_query.filter(Student.course == course_filter)
    
    # Apply department filter
    if department_filter:
        student_query = student_query.filter(Student.college_dept == department_filter)
    
    pending_students = student_query.all()
    pending_sscs = ssc_query.all()
    admin = Admin.query.get(session['user_id'])
    
    # Get unique courses and departments for filter dropdowns
    all_departments = ['CCS', 'COE', 'CTE', 'CAS', 'CBAA', 'CONAH', 'CIHMT', 'CIT', 'CCJE']
    unique_courses = all_departments
    unique_departments = all_departments
    
    return render_template('admin/user_approval.html', 
                         pending_students=pending_students, 
                         pending_sscs=pending_sscs, 
                         sort=sort, 
                         admin=admin, 
                         search=search,
                         department_filter=department_filter,
                         unique_departments=all_departments
    )

@app.route('/admin/approve_student/<int:student_id>', methods=['POST'])
@login_required('admin')
def admin_approve_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.status = 'active'
    db.session.commit()

    # Send email notification using Resend
    try:
        import resend
        import os
        resend.api_key = os.environ.get('RESEND_API_KEY')
        
        params = {
            "from": os.environ.get('MAIL_DEFAULT_SENDER'),
            "to": [student.email_address],
            "subject": "PiyuKonek Registration Approved",
            "html": f"""
                <p>Hello {student.fullname},</p>
                <p>Your registration has been approved! You can now log in to your PiyuKonek account.</p>
                <p>- PiyuKonek Team</p>
            """
        }
        resend.Emails.send(params)
    except Exception as e:
        print(f"[RESEND ERROR] Approve notification: {e}")

    # Notify all admins
    for admin in Admin.query.all():
        notif = Notification(
            user_id=admin.id,
            user_type='admin',
            title='New Student Registration',
            message=f'{student.fullname} has registered as a new student.',
            notification_type='user',
            created_at=datetime.utcnow()
        )
        db.session.add(notif)
    
    db.session.commit()
    flash(f"Student {student.fullname} approved.", "success")
    return redirect(url_for('admin_user_approval'))


@app.route('/admin/reject_student/<int:student_id>', methods=['POST'])
@login_required('admin')
def admin_reject_student(student_id):
    student = Student.query.get_or_404(student_id)
    rejection_reason = (request.form.get('rejection_reason') or '').strip()
    
    if not rejection_reason:
        flash('Please select a reason for rejection.', 'error')
        return redirect(url_for('admin_user_approval'))

    student.status = 'rejected'
    db.session.commit()

    # Send email notification using Resend (Updated from SMTP)
    try:
        import resend
        import os
        resend.api_key = os.environ.get('RESEND_API_KEY')

        params = {
            "from": os.environ.get('MAIL_DEFAULT_SENDER'),
            "to": [student.email_address],
            "subject": "PiyuKonek Registration Status",
            "html": f"""
                <p>Hello {student.fullname},</p>
                <p>Thank you for your interest in PiyuKonek.</p>
                <p>After review, your registration could not be approved at this time.</p>
                <p><strong>Reason for rejection:</strong> {rejection_reason}</p>
                <p>If you believe this is an error, please contact the administration.</p>
                <p>- PiyuKonek Team</p>
            """
        }
        resend.Emails.send(params)
    except Exception as e:
        print(f"[RESEND ERROR] Reject notification: {e}")

    flash(f"Student {student.fullname} rejected. They have been notified by email.", "danger")
    return redirect(url_for('admin_user_approval'))

import resend
import os
from flask import current_app

# Ensure your API key is set (usually in your .env or app config)
resend.api_key = os.getenv('RESEND_API_KEY')

@app.route('/admin/reject_ssc/<int:ssc_id>', methods=['POST'])
@login_required('admin')
def admin_reject_ssc(ssc_id):
    ssc = SSC.query.get_or_404(ssc_id)
    rejection_reason = (request.form.get('rejection_reason') or '').strip()
    
    if not rejection_reason:
        flash('Please select a reason for rejection.', 'error')
        return redirect(url_for('admin_user_approval'))

    # Update Database
    ssc.status = 'rejected'
    db.session.commit()

    # Send Notification via Resend
    try:
        params = {
            "from": "PiyuKonek <noreply@piyukonekweb.site>", # Use verified domain if you have one
            "to": [ssc.email_address],
            "subject": "PiyuKonek Guidance Registration Not Approved",
            "html": f"""
                <p>Hello {ssc.fullname},</p>
                <p>Thank you for your interest in joining PiyuKonek.</p>
                <p><strong>Reason for rejection:</strong> {rejection_reason}</p>
                <p>If you believe this is an error, please contact administration.</p>
                <p>- PiyuKonek Team</p>
            """
        }
        resend.Emails.send(params)
        flash(f"User {ssc.fullname} rejected and notified.", "success")
        
    except Exception as e:
        # This will now print the SPECIFIC Resend error to your terminal
        print(f"[RESEND ERROR]: {e}")
        flash(f"User rejected, but email failed: {str(e)}", "warning")

    return redirect(url_for('admin_user_approval'))

@app.route('/ssc/concern/<int:concern_id>')
@login_required('ssc')
def ssc_concern_detail(concern_id):
    concern = Concern.query.get_or_404(concern_id)
    timeline = ConcernHistory.query.filter_by(concern_id=concern.id).order_by(ConcernHistory.timestamp.desc()).all()
    ssc = SSC.query.get(session['user_id'])
    return render_template('ssc/ssc_concern_detail.html', concern=concern, timeline=timeline, ssc=ssc)

@app.route('/ssc/update_priority/<int:concern_id>', methods=['POST'])
@login_required('ssc')
def ssc_update_priority(concern_id):
    concern = Concern.query.get_or_404(concern_id)
    current_ssc = SSC.query.get(session.get('user_id'))

    # Only assigned SSC or Coordinator/Supervisor may update priority (same rule as responding)
    raw_pos = (current_ssc.position if current_ssc else '') or ''
    pos_norm = ' '.join(raw_pos.replace('_', ' ').replace('-', ' ').lower().split())
    is_lead = ('guidance coordinator' in pos_norm) or ('guidance supervisor' in pos_norm)
    if not current_ssc or not (is_lead or concern.assigned_to == current_ssc.id):
        flash('You are not allowed to update the priority level. This concern is assigned to another staff.', 'error')
        return redirect(url_for('ssc_concern_detail', concern_id=concern_id))

    new_priority = (request.form.get('priority_level') or '').strip().lower()
    allowed = {'low', 'medium', 'high', 'urgent'}
    if new_priority not in allowed:
        flash('Invalid priority level.', 'error')
        return redirect(url_for('ssc_concern_detail', concern_id=concern_id))

    old_priority = (concern.priority_level or '').strip().lower()
    if old_priority == new_priority:
        flash('Priority level is already set to that value.', 'info')
        return redirect(url_for('ssc_concern_detail', concern_id=concern_id))

    concern.priority_level = new_priority
    db.session.commit()

    # Add to concern history / audit: who changed priority, when, old → new
    history = ConcernHistory(
        concern_id=concern.id,
        status=concern.status,
        action=f'Priority level updated to {new_priority} by Guidance',
        timestamp=datetime.utcnow(),
        actor_type='ssc',
        actor_id=current_ssc.id,
        actor_name=current_ssc.fullname,
        old_value=old_priority,
        new_value=new_priority
    )
    db.session.add(history)
    db.session.commit()

    # In-app notification to the student
    try:
        student = concern.student
        notif = Notification(
            user_id=student.id,
            user_type='student',
            title='Concern priority updated',
            message=f'Guidance updated the priority level of your concern "{concern.title}" to {new_priority.title()}.',
            notification_type='concern_update',
            concern_id=concern.id,
            created_at=datetime.utcnow()
        )
        db.session.add(notif)
        db.session.commit()
    except Exception as _:
        db.session.rollback()

    flash('Priority level updated successfully!', 'success')
    return redirect(url_for('ssc_concern_detail', concern_id=concern_id))

@app.route('/ssc/student/<int:student_id>')
@login_required('ssc')
def ssc_student_detail(student_id):
    student = Student.query.get_or_404(student_id)
    ssc = SSC.query.get(session['user_id'])
    return render_template('ssc/ssc_student_detail.html', student=student, ssc=ssc)

@app.route('/ssc/respond_concern/<int:concern_id>', methods=['POST'])
@login_required('ssc')
def ssc_respond_concern(concern_id):
    concern = Concern.query.get_or_404(concern_id)
    current_ssc = SSC.query.get(session.get('user_id'))
    # Only assigned SSC or Coordinator/Supervisor may respond
    raw_pos = (current_ssc.position if current_ssc else '') or ''
    pos_norm = ' '.join(raw_pos.replace('_',' ').replace('-',' ').lower().split())
    is_lead = ('guidance coordinator' in pos_norm) or ('guidance supervisor' in pos_norm)
    if not current_ssc or not (is_lead or concern.assigned_to == current_ssc.id):
        flash('You are not allowed to respond to this concern. It is assigned to another staff.', 'error')
        return redirect(url_for('ssc_concern_detail', concern_id=concern_id))
    response = request.form.get('response')
    
    if response:
        concern.resolution_notes = response
        concern.status = 'processing'
        concern.resolved_by = session['user_id']
        concern.resolved_at = datetime.utcnow()
        
        # Handle file upload for response attachment
        response_attachment = None
        if 'response_attachment' in request.files:
            file = request.files['response_attachment']
            if file and file.filename != '':
                # Validate file type
                allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'}
                if '.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions:
                    # Create unique filename
                    filename = f"response_{concern_id}_{int(time.time())}_{secure_filename(file.filename)}"
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    response_attachment = filename
                    concern.response_attachment = response_attachment
        
        db.session.commit()
        
        # Add to concern history (audit: who reviewed/responded)
        # Create history entry for guidance response
        response_preview = response[:100] + "..." if len(response) > 100 else response
        history = ConcernHistory(
            concern_id=concern.id,
            status='processing',
            action=f'Guidance responded to your concern',
            timestamp=datetime.utcnow(),
            actor_type='ssc',
            actor_id=current_ssc.id,
            actor_name=current_ssc.fullname,
            new_value=response_preview  # Store response preview in new_value
        )
        db.session.add(history)
        db.session.commit()

        # In-app notification to the student
        try:
            student = concern.student
            notif = Notification(
                user_id=student.id,
                user_type='student',
                title='Guidance responded to your concern',
                message=f'Guidance has responded to your concern "{concern.title}".',
                notification_type='concern_update',
                concern_id=concern.id,
                created_at=datetime.utcnow()
            )
            db.session.add(notif)
            db.session.commit()
        except Exception as _:
            db.session.rollback()

        flash('Response sent successfully!', 'success')
        
        # Send email notification to student
        student = concern.student
        if response and student.email_address:
            responder = SSC.query.get(session['user_id'])
            responder_name = responder.fullname if responder else 'Guidance'
            has_attachment = response_attachment is not None
            send_concern_reply_email(student.email_address, student.fullname, concern.title, response, responder_name, 'Guidance', has_attachment)
    
    return redirect(url_for('ssc_concern_detail', concern_id=concern_id))

@app.route('/ssc/resolve_concern/<int:concern_id>', methods=['POST'])
@login_required('ssc')
def ssc_resolve_concern(concern_id):
    concern = Concern.query.get_or_404(concern_id)
    current_ssc = SSC.query.get(session.get('user_id'))
    raw_pos = (current_ssc.position if current_ssc else '') or ''
    pos_norm = ' '.join(raw_pos.replace('_',' ').replace('-',' ').lower().split())
    is_lead = ('guidance coordinator' in pos_norm) or ('guidance supervisor' in pos_norm)
    if not current_ssc or not (is_lead or concern.assigned_to == current_ssc.id):
        flash('You are not allowed to resolve this concern. It is assigned to another staff.', 'error')
        return redirect(url_for('ssc_concern_detail', concern_id=concern_id))
    resolution_notes = request.form.get('resolution_notes', '')
    try:
        concern.status = 'resolved'
        concern.resolved_by = session['user_id']
        concern.resolved_at = datetime.utcnow()
        if resolution_notes:
            concern.resolution_notes = resolution_notes
        db.session.commit()
        # Add to concern history (audit: who resolved, when)
        history = ConcernHistory(
            concern_id=concern.id,
            status='resolved',
            action='Concern marked as resolved by Guidance',
            timestamp=datetime.utcnow(),
            actor_type='ssc',
            actor_id=current_ssc.id,
            actor_name=current_ssc.fullname
        )
        db.session.add(history)
        db.session.commit()

        # In-app notification to the student
        try:
            student = concern.student
            notif = Notification(
                user_id=student.id,
                user_type='student',
                title='Your concern has been resolved',
                message=f'Guidance marked your concern "{concern.title}" as resolved.',
                notification_type='concern_update',
                concern_id=concern.id,
                created_at=datetime.utcnow()
            )
            db.session.add(notif)
            db.session.commit()
        except Exception as _:
            db.session.rollback()

        flash('Concern marked as resolved successfully!', 'success')
        
        # Send email notification to student
        student = concern.student
        if student.email_address and concern.resolution_notes:
            responder = SSC.query.get(session['user_id'])
            responder_name = responder.fullname if responder else 'Guidance'
            has_attachment = concern.response_attachment is not None
            send_concern_reply_email(student.email_address, student.fullname, concern.title, concern.resolution_notes, responder_name, 'Guidance', has_attachment)
    except Exception as e:
        db.session.rollback()
        print(f"Error resolving concern: {e}")
        flash('Error resolving concern. Please try again.', 'error')
    return redirect(url_for('ssc_concerns'))

@app.route('/ssc/notification/<int:notification_id>')
@login_required('ssc')
def ssc_view_notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    # Mark as read if not already
    if not notification.is_read:
        notification.is_read = True
        db.session.commit()
    concern = notification.concern if notification.concern_id else None
    return render_template('ssc/ssc_notification_detail.html', notification=notification, concern=concern)

# Bulk Concern Operations for SSC
@app.route('/ssc/bulk_update_status', methods=['POST'])
@login_required('ssc')
def ssc_bulk_update_status():
    try:
        current_ssc = SSC.query.get(session.get('user_id'))
        concern_ids = request.form.getlist('concern_ids[]')
        new_status = request.form.get('new_status')
        action_notes = request.form.get('action_notes', '')
        
        if not concern_ids or not new_status:
            return jsonify({'success': False, 'message': 'Missing required parameters'})
        
        updated_count = 0
        for concern_id in concern_ids:
            concern = Concern.query.get(concern_id)
            if concern and concern.status != new_status:
                old_status = concern.status
                concern.status = new_status
                
                # Update timestamps based on status
                if new_status == 'processing':
                    concern.processing_at = datetime.utcnow()
                    concern.processed_by = session['user_id']
                elif new_status == 'resolved':
                    concern.resolved_at = datetime.utcnow()
                    concern.resolved_by = session['user_id']
                    if action_notes:
                        concern.resolution_notes = action_notes
                
                # Add to concern history (audit)
                history = ConcernHistory(
                    concern_id=concern.id,
                    status=new_status,
                    action=f'Bulk status update: {old_status} → {new_status} by Guidance',
                    timestamp=datetime.utcnow(),
                    actor_type='ssc',
                    actor_id=current_ssc.id if current_ssc else None,
                    actor_name=current_ssc.fullname if current_ssc else 'Guidance'
                )
                db.session.add(history)
                updated_count += 1
        
        db.session.commit()
        
        # Send notifications to students
        for concern_id in concern_ids:
            concern = Concern.query.get(concern_id)
            if concern and concern.student:
                notification = Notification(
                    user_id=concern.student.id,
                    user_type='student',
                    title=f'Concern Status Updated',
                    message=f'Your concern "{concern.title}" status has been updated to {new_status.title()}',
                    notification_type='concern_update',
                    concern_id=concern.id,
                    is_read=False
                )
                db.session.add(notification)
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Successfully updated {updated_count} concerns to {new_status.title()}',
            'updated_count': updated_count
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in bulk status update: {e}")
        return jsonify({'success': False, 'message': f'Error updating concerns: {str(e)}'})

@app.route('/ssc/bulk_assign', methods=['POST'])
@login_required('ssc')
def ssc_bulk_assign():
    try:
        # Enforce position-based permission: only Guidance Coordinator/Supervisor can assign
        current_ssc = SSC.query.get(session.get('user_id'))
        raw_pos = (current_ssc.position if current_ssc else '') or ''
        pos_norm = ' '.join(raw_pos.replace('_',' ').replace('-',' ').lower().split())
        is_allowed = ('guidance coordinator' in pos_norm) or ('guidance supervisor' in pos_norm)
        if not current_ssc or not is_allowed:
            return jsonify({'success': False, 'message': 'Permission denied: Only Guidance Coordinator/Supervisor can assign staff.'}), 403
        concern_ids = request.form.getlist('concern_ids[]')
        assigned_to = request.form.get('assigned_to')
        
        if not concern_ids or not assigned_to:
            return jsonify({'success': False, 'message': 'Missing required parameters'})
        
        # Get the assigned staff member
        assigned_staff = SSC.query.get(assigned_to)
        if not assigned_staff:
            return jsonify({'success': False, 'message': 'Invalid staff member'})
        
        updated_count = 0
        for concern_id in concern_ids:
            concern = Concern.query.get(concern_id)
            if concern:
                concern.assigned_to = assigned_to
                concern.status = 'processing'
                concern.processing_at = datetime.utcnow()
                
                # Add to concern history (audit: who assigned, who was assigned)
                history = ConcernHistory(
                    concern_id=concern.id,
                    status='processing',
                    action=f'Bulk assigned to {assigned_staff.fullname} by {current_ssc.fullname} ({current_ssc.position})',
                    timestamp=datetime.utcnow(),
                    actor_type='ssc',
                    actor_id=current_ssc.id,
                    actor_name=current_ssc.fullname
                )
                db.session.add(history)

                # Notify the assigned staff
                try:
                    notif_staff = Notification(
                        user_id=assigned_staff.id,
                        user_type='ssc',
                        title='New concern assigned',
                        message=f'Concern #{concern.id} ("{concern.title}") has been assigned to you.',
                        notification_type='concern_assigned',
                        concern_id=concern.id
                    )
                    db.session.add(notif_staff)
                except Exception:
                    pass

                # Optionally notify the student about assignee
                try:
                    if concern.student:
                        notif_student = Notification(
                            user_id=concern.student.id,
                            user_type='student',
                            title='Your concern has been assigned',
                            message=f'Your concern #{concern.id} is now assigned to {assigned_staff.fullname}.',
                            notification_type='concern_assigned',
                            concern_id=concern.id
                        )
                        db.session.add(notif_student)
                except Exception:
                    pass

                # Notify Guidance Coordinator/Supervisor with the assignee name
                try:
                    leads = SSC.query.all()
                    for lead in leads:
                        raw_pos = (lead.position or '')
                        pos_norm_lead = ' '.join(raw_pos.replace('_',' ').replace('-',' ').lower().split())
                        if ('guidance coordinator' in pos_norm_lead) or ('guidance supervisor' in pos_norm_lead):
                            notif_lead = Notification(
                                user_id=lead.id,
                                user_type='ssc',
                                title='Concern assigned to staff',
                                message=f'Concern #{concern.id} ("{concern.title}") assigned to {assigned_staff.fullname}.',
                                notification_type='concern_assigned',
                                concern_id=concern.id
                            )
                            db.session.add(notif_lead)
                except Exception:
                    pass

                # Notify all admins with the assignee name
                try:
                    for admin in Admin.query.all():
                        notif_admin = Notification(
                            user_id=admin.id,
                            user_type='admin',
                            title='Concern assigned to staff',
                            message=f'Concern #{concern.id} ("{concern.title}") assigned to {assigned_staff.fullname}.',
                            notification_type='concern_assigned',
                            concern_id=concern.id
                        )
                        db.session.add(notif_admin)
                except Exception:
                    pass
                updated_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Successfully assigned {updated_count} concerns to {assigned_staff.fullname}',
            'updated_count': updated_count
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in bulk assignment: {e}")
        return jsonify({'success': False, 'message': f'Error assigning concerns: {str(e)}'})

@app.route('/ssc/bulk_export', methods=['POST'])
@login_required('ssc')
def ssc_bulk_export():
    try:
        concern_ids = request.form.getlist('concern_ids[]')
        export_format = request.form.get('export_format', 'csv')
        
        if not concern_ids:
            return jsonify({'success': False, 'message': 'No concerns selected for export'})
        
        concerns = Concern.query.filter(Concern.id.in_(concern_ids)).all()
        
        if export_format == 'csv':
            # Generate CSV
            output = StringIO()
            writer = csv.writer(output)
            writer.writerow(['ID', 'Title', 'Student', 'Type', 'Priority', 'Status', 'Submitted', 'Description'])
            
            for concern in concerns:
                writer.writerow([
                    concern.id,
                    concern.title,
                    concern.student.fullname if concern.student else 'N/A',
                    concern.concern_type,
                    concern.priority_level,
                    concern.status,
                    concern.submitted_at.strftime('%Y-%m-%d %H:%M') if concern.submitted_at else 'N/A',
                    concern.description[:100] + '...' if len(concern.description) > 100 else concern.description
                ])
            
            output.seek(0)
            return Response(
                output.getvalue(),
                mimetype='text/csv',
                headers={'Content-Disposition': f'attachment; filename=bulk_concerns_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.csv'}
            )
        
        elif export_format == 'pdf':
            # Generate PDF
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)
            elements = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=getSampleStyleSheet()['Title'],
                fontSize=16,
                spaceAfter=30,
                alignment=TA_CENTER
            )
            elements.append(Paragraph(f'Bulk Concerns Export - {datetime.utcnow().strftime("%Y-%m-%d %H:%M")}', title_style))
            
            # Table
            data = [['ID', 'Title', 'Student', 'Type', 'Priority', 'Status', 'Submitted']]
            for concern in concerns:
                data.append([
                    str(concern.id),
                    concern.title,
                    concern.student.fullname if concern.student else 'N/A',
                    concern.concern_type or 'N/A',
                    concern.priority_level or 'N/A',
                    concern.status,
                    concern.submitted_at.strftime('%Y-%m-%d %H:%M') if concern.submitted_at else 'N/A'
                ])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            doc.build(elements)
            buffer.seek(0)
            
            return Response(
                buffer.getvalue(),
                mimetype='application/pdf',
                headers={'Content-Disposition': f'attachment; filename=bulk_concerns_export_{datetime.utcnow().strftime("%Y%m%d_%H%M%S")}.pdf'}
            )
        
        else:
            return jsonify({'success': False, 'message': 'Unsupported export format'})
            
    except Exception as e:
        print(f"Error in bulk export: {e}")
        return jsonify({'success': False, 'message': f'Error exporting concerns: {str(e)}'})

@app.route('/ssc/bulk_delete', methods=['POST'])
@login_required('ssc')
def ssc_bulk_delete():
    try:
        current_ssc = SSC.query.get(session.get('user_id'))
        concern_ids = request.form.getlist('concern_ids[]')
        delete_reason = request.form.get('delete_reason', 'Bulk deletion by Guidance')
        
        if not concern_ids:
            return jsonify({'success': False, 'message': 'No concerns selected for deletion'})
        
        deleted_count = 0
        for concern_id in concern_ids:
            concern = Concern.query.get(concern_id)
            if concern and concern.status in ['pending', 'processing']:
                # Soft delete - mark as closed
                concern.status = 'closed'
                concern.closed_at = datetime.utcnow()
                concern.closed_by = session['user_id']
                
                # Add to concern history (audit)
                history = ConcernHistory(
                    concern_id=concern.id,
                    status='closed',
                    action=f'Bulk deletion: {delete_reason}',
                    timestamp=datetime.utcnow(),
                    actor_type='ssc',
                    actor_id=current_ssc.id if current_ssc else None,
                    actor_name=current_ssc.fullname if current_ssc else 'Guidance'
                )
                db.session.add(history)
                deleted_count += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Successfully closed {deleted_count} concerns',
            'deleted_count': deleted_count
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in bulk deletion: {e}")
        return jsonify({'success': False, 'message': f'Error deleting concerns: {str(e)}'})

@app.route('/ssc/get_staff_list')
@login_required('ssc')
def ssc_get_staff_list():
    """Get list of SSC staff for assignment"""
    try:
        staff_list = SSC.query.filter_by(status='active').all()
        staff_data = [{'id': staff.id, 'name': staff.fullname, 'position': staff.position} for staff in staff_list]
        return jsonify({'success': True, 'staff': staff_data})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Admin Analytics Dashboard
@app.route('/admin/analytics')
@login_required('admin')
def admin_analytics():
    admin = Admin.query.get(session['user_id'])

    # System-wide concerns
    all_concerns = Concern.query.order_by(Concern.submitted_at.desc()).all()
    total_concerns = len(all_concerns)
    resolved_concerns = len([c for c in all_concerns if c.status == 'resolved'])
    processing_concerns = len([c for c in all_concerns if c.status == 'processing'])
    pending_concerns = len([c for c in all_concerns if c.status == 'pending'])
    resolution_rate = (resolved_concerns / total_concerns * 100) if total_concerns else 0

    # Response and resolution times (where possible)
    response_times = []
    for concern in all_concerns:
        # Look for first response - check for "Guidance" or "SSC" in action, or status change to processing
        first_response = ConcernHistory.query.filter(
            ConcernHistory.concern_id == concern.id,
            db.or_(
                ConcernHistory.action.like('%SSC%'),
                ConcernHistory.action.like('%Guidance%'),
                ConcernHistory.status == 'processing'
            )
        ).order_by(ConcernHistory.timestamp.asc()).first()
        # Also check if concern has processing_at or responded_at set
        if not first_response and (concern.processing_at or concern.responded_at):
            # Use processing_at or responded_at as first response time
            first_response_time = concern.processing_at or concern.responded_at
            if concern.submitted_at:
                response_times.append((first_response_time - concern.submitted_at).total_seconds() / 3600)
        elif first_response and concern.submitted_at:
            response_times.append((first_response.timestamp - concern.submitted_at).total_seconds() / 3600)
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0

    resolution_times = []
    for concern in all_concerns:
        if concern.status == 'resolved' and concern.resolved_at and concern.submitted_at:
            resolution_times.append((concern.resolved_at - concern.submitted_at).total_seconds() / 3600)
    avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0

    # Priority and type stats
    priority_stats = {}
    type_stats = {}
    for c in all_concerns:
        pr = c.priority_level or 'unknown'
        tp = c.concern_type or 'unknown'
        
        # Normalize concern type to prevent duplicates
        if tp.lower() == 'mental health':
            tp = 'Mental Health'
        elif tp.lower() == 'academic':
            tp = 'Academic'
        elif tp.lower() == 'administrative':
            tp = 'Administrative'
        elif tp.lower() == 'financial':
            tp = 'Financial'
        elif tp.lower() == 'personal':
            tp = 'Personal'
        else:
            tp = tp.title()  # Capitalize first letter of each word
        
        priority_stats.setdefault(pr, {'total': 0, 'resolved': 0})
        type_stats.setdefault(tp, {'total': 0, 'resolved': 0})
        priority_stats[pr]['total'] += 1
        type_stats[tp]['total'] += 1
        if c.status == 'resolved':
            priority_stats[pr]['resolved'] += 1
            type_stats[tp]['resolved'] += 1

    # Monthly performance (last 6 months)
    current_date = datetime.utcnow()
    current_month = current_date.month
    current_year = current_date.year
    monthly_data = []
    for i in range(6):
        month = current_month - i
        year = current_year
        if month <= 0:
            month += 12
            year -= 1
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(seconds=1)
        month_concerns = [c for c in all_concerns if c.submitted_at and month_start <= c.submitted_at <= month_end]
        month_resolved = [c for c in month_concerns if c.status == 'resolved']
        monthly_data.append({
            'month': month_start.strftime('%B %Y'),
            'total': len(month_concerns),
            'resolved': len(month_resolved),
            'rate': (len(month_resolved) / len(month_concerns) * 100) if month_concerns else 0
        })
    monthly_data.reverse()

    recent_concerns = Concern.query.order_by(Concern.updated_at.desc()).limit(10).all()

    return render_template('admin/admin_analytics.html',
                           admin=admin,
                           total_concerns=total_concerns,
                           resolved_concerns=resolved_concerns,
                           processing_concerns=processing_concerns,
                           pending_concerns=pending_concerns,
                           resolution_rate=resolution_rate,
                           avg_response_time=avg_response_time,
                           avg_resolution_time=avg_resolution_time,
                           priority_stats=priority_stats,
                           type_stats=type_stats,
                           monthly_data=monthly_data,
                           recent_concerns=recent_concerns)

@app.route('/admin/analytics/export')
@login_required('admin')
def admin_export_analytics():
    admin = Admin.query.get(session['user_id'])

    # Reuse the same computation as admin_analytics
    all_concerns = Concern.query.order_by(Concern.submitted_at.desc()).all()
    total_concerns = len(all_concerns)
    resolved_concerns = len([c for c in all_concerns if c.status == 'resolved'])
    processing_concerns = len([c for c in all_concerns if c.status == 'processing'])
    pending_concerns = len([c for c in all_concerns if c.status == 'pending'])
    resolution_rate = (resolved_concerns / total_concerns * 100) if total_concerns else 0

    response_times = []
    for concern in all_concerns:
        first_response = ConcernHistory.query.filter(
            ConcernHistory.concern_id == concern.id,
            ConcernHistory.action.like('%SSC%')
        ).order_by(ConcernHistory.timestamp.asc()).first()
        if first_response and concern.submitted_at:
            response_times.append((first_response.timestamp - concern.submitted_at).total_seconds() / 3600)
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0

    resolution_times = []
    for concern in all_concerns:
        if concern.status == 'resolved' and concern.resolved_at and concern.submitted_at:
            resolution_times.append((concern.resolved_at - concern.submitted_at).total_seconds() / 3600)
    avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0

    priority_stats = {}
    type_stats = {}
    for c in all_concerns:
        pr = c.priority_level or 'unknown'
        tp = c.concern_type or 'unknown'
        priority_stats.setdefault(pr, {'total': 0, 'resolved': 0})
        type_stats.setdefault(tp, {'total': 0, 'resolved': 0})
        priority_stats[pr]['total'] += 1
        type_stats[tp]['total'] += 1
        if c.status == 'resolved':
            priority_stats[pr]['resolved'] += 1
            type_stats[tp]['resolved'] += 1

    current_date = datetime.utcnow()
    current_month = current_date.month
    current_year = current_date.year
    monthly_data = []
    for i in range(6):
        month = current_month - i
        year = current_year
        if month <= 0:
            month += 12
            year -= 1
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(seconds=1)
        month_concerns = [c for c in all_concerns if c.submitted_at and month_start <= c.submitted_at <= month_end]
        month_resolved = [c for c in month_concerns if c.status == 'resolved']
        monthly_data.append([
            month_start.strftime('%B %Y'),
            len(month_concerns),
            len(month_resolved),
            f"{(len(month_resolved) / len(month_concerns) * 100) if month_concerns else 0:.1f}%"
        ])
    monthly_data.reverse()

    recent_concerns = Concern.query.order_by(Concern.updated_at.desc()).limit(10).all()

    # Build PDF with professional styling
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), 
                            leftMargin=50, rightMargin=50, 
                            topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    elements = []

    # Professional color scheme
    primary_color = colors.HexColor('#1e293b')  # Dark slate
    accent_color = colors.HexColor('#4CAF50')   # Green
    light_gray = colors.HexColor('#f8fafc')     # Very light gray
    border_color = colors.HexColor('#e2e8f0')    # Light border
    text_secondary = colors.HexColor('#64748b') # Gray text

    # Header Section
    logo_path = os.path.join(app.static_folder, 'images', 'logo.png')
    if os.path.exists(logo_path):
        logo = Image(logo_path, width=60, height=60)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1, 8))
    
    # Title styles
    title_style = ParagraphStyle(
        name='TitleCenter',
        parent=styles['Title'],
        alignment=TA_CENTER,
        fontSize=22,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        spaceAfter=4,
        leading=26
    )
    
    subtitle_style = ParagraphStyle(
        name='SubtitleCenter',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=11,
        textColor=text_secondary,
        spaceAfter=16,
        leading=14
    )
    
    elements.append(Paragraph('Admin Analytics Report', title_style))
    elements.append(Paragraph('PiyuKonek - Laguna State Polytechnic University - Sta. Cruz Campus', subtitle_style))
    elements.append(Spacer(1, 20))

    # Meta information with better styling
    meta_style = ParagraphStyle(
        name='MetaRight',
        parent=styles['Normal'],
        alignment=TA_RIGHT,
        fontSize=9,
        textColor=text_secondary,
        spaceAfter=2,
        leading=11
    )
    elements.append(Paragraph(f"<b>Prepared by:</b> {admin.fullname} (Admin)", meta_style))
    elements.append(Paragraph(f"<b>Date Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M')}", meta_style))
    elements.append(Spacer(1, 20))

    # Overall Summary Section with improved styling
    section_heading_style = ParagraphStyle(
        name='SectionHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=primary_color,
        fontName='Helvetica-Bold',
        spaceBefore=16,
        spaceAfter=10,
        leading=18
    )
    
    elements.append(Paragraph('1. Overall Summary', section_heading_style))
    
    kpi_header = ['Total', 'Resolved', 'Processing', 'Pending', 'Resolution Rate', 'Avg Response (hrs)', 'Avg Resolution (hrs)']
    kpi_values = [
        str(total_concerns),
        str(resolved_concerns),
        str(processing_concerns),
        str(pending_concerns),
        f"{resolution_rate:.1f}%",
        f"{avg_response_time:.1f}",
        f"{avg_resolution_time:.1f}"
    ]
    # Calculate equal column widths for 7 columns (landscape width - margins = 792 - 100 = 692)
    kpi_col_width = (792 - 100) / 7
    kpi_table = Table([kpi_header, kpi_values], colWidths=[kpi_col_width] * 7)
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), accent_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('FONTSIZE', (0,1), (-1,1), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('TOPPADDING', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,1), (-1,1), 8),
        ('TOPPADDING', (0,1), (-1,1), 8),
        ('BACKGROUND', (0,1), (-1,1), light_gray),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,1), [colors.white, light_gray]),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 20))

    # Monthly Performance Section
    elements.append(Paragraph('2. Monthly Performance (Last 6 Months)', section_heading_style))
    monthly_header = [['Month', 'Total', 'Resolved', 'Resolution Rate %']]
    # Calculate equal column widths for 4 columns
    monthly_col_width = (792 - 100) / 4
    monthly_table = Table(monthly_header + monthly_data, colWidths=[monthly_col_width] * 4, repeatRows=1)
    monthly_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('TOPPADDING', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,1), (-1,-1), 7),
        ('TOPPADDING', (0,1), (-1,-1), 7),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_gray]),
    ]))
    elements.append(monthly_table)
    elements.append(Spacer(1, 20))

    # Concerns by Priority Level Section
    elements.append(Paragraph('3. Concerns by Priority Level', section_heading_style))
    pr_rows = [['Priority', 'Total', 'Resolved']]
    order_map = {'urgent': 3, 'high': 2, 'medium': 1, 'low': 0}
    for key in sorted(priority_stats.keys(), key=lambda k: order_map.get(str(k).lower(), -1), reverse=True):
        pr = priority_stats[key]
        pr_rows.append([key.title(), str(pr['total']), str(pr['resolved'])])
    # Calculate equal column widths for 3 columns
    pr_col_width = (792 - 100) / 3
    pr_table = Table(pr_rows, colWidths=[pr_col_width] * 3, repeatRows=1)
    pr_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('TOPPADDING', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,1), (-1,-1), 7),
        ('TOPPADDING', (0,1), (-1,-1), 7),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_gray]),
    ]))
    elements.append(pr_table)
    elements.append(Spacer(1, 20))

    # Concerns by Type Section
    elements.append(Paragraph('4. Concerns by Type', section_heading_style))
    tp_rows = [['Type', 'Total', 'Resolved']]
    for key in sorted(type_stats.keys()):
        tp = type_stats[key]
        tp_rows.append([key.title(), str(tp['total']), str(tp['resolved'])])
    # Calculate equal column widths for 3 columns
    tp_col_width = (792 - 100) / 3
    tp_table = Table(tp_rows, colWidths=[tp_col_width] * 3, repeatRows=1)
    tp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('TOPPADDING', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,1), (-1,-1), 7),
        ('TOPPADDING', (0,1), (-1,-1), 7),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_gray]),
    ]))
    elements.append(tp_table)
    elements.append(Spacer(1, 20))

    # Recent Concerns Section
    elements.append(Paragraph('5. Recent Concerns', section_heading_style))
    rc_rows = [['ID', 'Title', 'Type', 'Priority', 'Status', 'Submitted', 'Resolved']]
    for c in recent_concerns:
        rc_rows.append([
            str(c.id),
            c.title[:30] + '...' if len(c.title) > 30 else c.title,
            c.concern_type.title() if c.concern_type else 'N/A',
            c.priority_level.title() if c.priority_level else 'N/A',
            c.status.title() if c.status else 'N/A',
            c.submitted_at.strftime('%Y-%m-%d %H:%M') if c.submitted_at else 'N/A',
            c.resolved_at.strftime('%Y-%m-%d %H:%M') if c.resolved_at else '-'
        ])
    # Calculate equal column widths for 7 columns
    rc_col_width = (792 - 100) / 7
    rc_table = Table(rc_rows, colWidths=[rc_col_width] * 7, repeatRows=1)
    rc_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('ALIGN', (1,1), (1,-1), 'LEFT'),  # Left align title
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 10),
        ('TOPPADDING', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, border_color),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_gray]),
    ]))
    elements.append(rc_table)
    elements.append(Spacer(1, 20))

    # Professional footer
    foot_style = ParagraphStyle(
        name='FootCenter',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=8,
        textColor=text_secondary,
        spaceBefore=10,
        leading=10
    )
    elements.append(Spacer(1, 10))
    elements.append(Paragraph('This is a system-generated report from PiyuKonek.', foot_style))

    doc.build(elements)
    buffer.seek(0)
    return app.response_class(
        buffer.getvalue(),
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename=admin_analytics_{datetime.now().strftime("%Y%m%d")}.pdf'}
    )
# Performance Analytics Dashboard for SSC
@app.route('/ssc/analytics')
@login_required('ssc')
def ssc_analytics():
    """SSC Performance Analytics Dashboard"""
    ssc_id = session['user_id']
    ssc = SSC.query.get(ssc_id)
    
    # Get current month and year
    current_date = datetime.utcnow()
    current_month = current_date.month
    current_year = current_date.year
    
    # Get all concerns in the system so analytics reflects current submissions and statuses
    all_concerns = Concern.query.all()
    
    # Calculate performance metrics
    total_concerns_handled = len(all_concerns)
    resolved_concerns = len([c for c in all_concerns if c.status == 'resolved'])
    processing_concerns = len([c for c in all_concerns if c.status == 'processing'])
    
    # Calculate resolution rate
    resolution_rate = (resolved_concerns / total_concerns_handled * 100) if total_concerns_handled > 0 else 0
    
    # Calculate average response time (time from submission to first response)
    response_times = []
    for concern in all_concerns:
        # Find first response time - check for "Guidance" or "SSC" in action, or status change to processing
        first_response = ConcernHistory.query.filter(
            ConcernHistory.concern_id == concern.id,
            db.or_(
                ConcernHistory.action.like('%SSC%'),
                ConcernHistory.action.like('%Guidance%'),
                ConcernHistory.status == 'processing'
            )
        ).order_by(ConcernHistory.timestamp.asc()).first()
        
        # Also check if concern has processing_at or responded_at set
        if not first_response and (concern.processing_at or concern.responded_at):
            first_response_time = concern.processing_at or concern.responded_at
            if concern.submitted_at:
                response_time = (first_response_time - concern.submitted_at).total_seconds() / 3600
                response_times.append(response_time)
        elif first_response and concern.submitted_at:
            response_time = (first_response.timestamp - concern.submitted_at).total_seconds() / 3600  # in hours
            response_times.append(response_time)
    
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0
    
    # Calculate average resolution time
    resolution_times = []
    for concern in all_concerns:
        if concern.status == 'resolved' and concern.resolved_at:
            resolution_time = (concern.resolved_at - concern.submitted_at).total_seconds() / 3600  # in hours
            resolution_times.append(resolution_time)
    
    avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0
    
    # Get concerns by priority level
    priority_stats = {}
    for concern in all_concerns:
        priority = concern.priority_level
        if priority not in priority_stats:
            priority_stats[priority] = {'total': 0, 'resolved': 0}
        priority_stats[priority]['total'] += 1
        if concern.status == 'resolved':
            priority_stats[priority]['resolved'] += 1
    
    # Get concerns by type
    type_stats = {}
    for concern in all_concerns:
        concern_type = concern.concern_type or 'unknown'
        
        # Normalize concern type to prevent duplicates
        if concern_type.lower() == 'mental health':
            concern_type = 'Mental Health'
        elif concern_type.lower() == 'academic':
            concern_type = 'Academic'
        elif concern_type.lower() == 'administrative':
            concern_type = 'Administrative'
        elif concern_type.lower() == 'financial':
            concern_type = 'Financial'
        elif concern_type.lower() == 'personal':
            concern_type = 'Personal'
        else:
            concern_type = concern_type.title()  # Capitalize first letter of each word
        
        if concern_type not in type_stats:
            type_stats[concern_type] = {'total': 0, 'resolved': 0}
        type_stats[concern_type]['total'] += 1
        if concern.status == 'resolved':
            type_stats[concern_type]['resolved'] += 1
    
    # Get monthly performance data (last 6 months)
    monthly_data = []
    for i in range(6):
        month = current_month - i
        year = current_year
        if month <= 0:
            month += 12
            year -= 1
        
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        month_concerns = [c for c in all_concerns if month_start <= c.submitted_at <= month_end]
        month_resolved = [c for c in month_concerns if c.status == 'resolved']
        
        monthly_data.append({
            'month': month_start.strftime('%B %Y'),
            'total': len(month_concerns),
            'resolved': len(month_resolved),
            'rate': (len(month_resolved) / len(month_concerns) * 100) if month_concerns else 0
        })
    
    monthly_data.reverse()  # Show oldest to newest
    
    # Get recent concerns for quick overview (latest updates system-wide)
    recent_concerns = Concern.query.order_by(Concern.updated_at.desc()).limit(5).all()
    
    # Calculate satisfaction score (not available without rating system)
    avg_satisfaction = 0
    
    # Counts by status for parity with dashboard
    pending_concerns = len([c for c in all_concerns if c.status == 'pending'])

    return render_template('ssc/analytics_dashboard.html', 
                         ssc=ssc,
                         total_concerns=total_concerns_handled,
                         resolved_concerns=resolved_concerns,
                         processing_concerns=processing_concerns,
                         pending_concerns=pending_concerns,
                         resolution_rate=resolution_rate,
                         avg_response_time=avg_response_time,
                         avg_resolution_time=avg_resolution_time,
                         priority_stats=priority_stats,
                         type_stats=type_stats,
                         monthly_data=monthly_data,
                         recent_concerns=recent_concerns,
                         avg_satisfaction=avg_satisfaction)

@app.route('/ssc/analytics/export')
@login_required('ssc')
def export_ssc_analytics():
    """Export SSC analytics report as a styled PDF"""
    ssc_id = session['user_id']
    ssc = SSC.query.get(ssc_id)

    # Collect analytics data (mirror ssc_analytics route)
    all_concerns = Concern.query.all()

    total_concerns_handled = len(all_concerns)
    resolved_concerns = len([c for c in all_concerns if c.status == 'resolved'])
    processing_concerns = len([c for c in all_concerns if c.status == 'processing'])
    resolution_rate = (resolved_concerns / total_concerns_handled * 100) if total_concerns_handled > 0 else 0

    # Response/Resolution time calculations
    response_times = []
    for concern in all_concerns:
        # Find first response time - check for "Guidance" or "SSC" in action, or status change to processing
        first_response = ConcernHistory.query.filter(
            ConcernHistory.concern_id == concern.id,
            db.or_(
                ConcernHistory.action.like('%SSC%'),
                ConcernHistory.action.like('%Guidance%'),
                ConcernHistory.status == 'processing'
            )
        ).order_by(ConcernHistory.timestamp.asc()).first()
        
        # Also check if concern has processing_at or responded_at set
        if not first_response and (concern.processing_at or concern.responded_at):
            first_response_time = concern.processing_at or concern.responded_at
            if concern.submitted_at:
                response_time = (first_response_time - concern.submitted_at).total_seconds() / 3600
                response_times.append(response_time)
        elif first_response and concern.submitted_at:
            response_time = (first_response.timestamp - concern.submitted_at).total_seconds() / 3600
            response_times.append(response_time)
    avg_response_time = sum(response_times) / len(response_times) if response_times else 0

    resolution_times = []
    for concern in all_concerns:
        if concern.status == 'resolved' and concern.resolved_at:
            resolution_time = (concern.resolved_at - concern.submitted_at).total_seconds() / 3600
            resolution_times.append(resolution_time)
    avg_resolution_time = sum(resolution_times) / len(resolution_times) if resolution_times else 0

    # Priority stats
    priority_stats = {}
    for concern in all_concerns:
        priority = concern.priority_level
        if priority not in priority_stats:
            priority_stats[priority] = {'total': 0, 'resolved': 0}
        priority_stats[priority]['total'] += 1
        if concern.status == 'resolved':
            priority_stats[priority]['resolved'] += 1

    # Type stats
    type_stats = {}
    for concern in all_concerns:
        ctype = concern.concern_type or 'unknown'
        
        # Normalize concern type to prevent duplicates
        if ctype.lower() == 'mental health':
            ctype = 'Mental Health'
        elif ctype.lower() == 'academic':
            ctype = 'Academic'
        elif ctype.lower() == 'administrative':
            ctype = 'Administrative'
        elif ctype.lower() == 'financial':
            ctype = 'Financial'
        elif ctype.lower() == 'personal':
            ctype = 'Personal'
        else:
            ctype = ctype.title()  # Capitalize first letter of each word
        
        if ctype not in type_stats:
            type_stats[ctype] = {'total': 0, 'resolved': 0}
        type_stats[ctype]['total'] += 1
        if concern.status == 'resolved':
            type_stats[ctype]['resolved'] += 1

    # Monthly performance (last 6 months)
    current_date = datetime.utcnow()
    current_month = current_date.month
    current_year = current_date.year
    monthly_data = []
    for i in range(6):
        month = current_month - i
        year = current_year
        if month <= 0:
            month += 12
            year -= 1
        month_start = datetime(year, month, 1)
        if month == 12:
            month_end = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            month_end = datetime(year, month + 1, 1) - timedelta(seconds=1)
        month_concerns = [c for c in all_concerns if c.submitted_at and month_start <= c.submitted_at <= month_end]
        month_resolved = [c for c in month_concerns if c.status == 'resolved']
        monthly_data.append({
            'month': month_start.strftime('%B %Y'),
            'total': len(month_concerns),
            'resolved': len(month_resolved),
            'rate': (len(month_resolved) / len(month_concerns) * 100) if month_concerns else 0
        })
    monthly_data.reverse()

    recent_concerns = Concern.query.filter_by(resolved_by=ssc_id).order_by(Concern.updated_at.desc()).limit(10).all()

    # Build PDF with simple, clean styling
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, 
                            leftMargin=50, rightMargin=50, 
                            topMargin=50, bottomMargin=50)
    styles = getSampleStyleSheet()
    elements = []

    # Simple, clean styles
    title_style = ParagraphStyle(
        name='TitleCenter',
        parent=styles['Title'],
        alignment=TA_CENTER,
        fontSize=20,
        textColor=colors.HexColor('#1e293b'),
        fontName='Helvetica-Bold',
        spaceAfter=8
    )
    subtitle_style = ParagraphStyle(
        name='Subtle',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=20
    )
    heading2_style = ParagraphStyle(
        name='Heading2Custom',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#1e293b'),
        fontName='Helvetica-Bold',
        spaceBefore=16,
        spaceAfter=8
    )
    meta_style = ParagraphStyle(
        name='MetaRight',
        parent=styles['Normal'],
        alignment=TA_RIGHT,
        fontSize=9,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=6
    )
    kpi_cell_style = ParagraphStyle(
        name='KPICell',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=12,
        fontName='Helvetica-Bold',
        textColor=colors.HexColor('#1e293b')
    )

    # Simple header
    elements.append(Paragraph('<b>Guidance Performance Analytics Report</b>', title_style))
    elements.append(Paragraph('Laguna State Polytechnic University - Sta. Cruz Campus', subtitle_style))
    
    # Simple divider
    elements.append(Spacer(1, 12))
    divider = Table([['']], colWidths=[496])
    divider.setStyle(TableStyle([
        ('LINEBELOW', (0, 0), (0, 0), 1, colors.HexColor('#4CAF50')),
        ('TOPPADDING', (0, 0), (0, 0), 0),
        ('BOTTOMPADDING', (0, 0), (0, 0), 12),
    ]))
    elements.append(divider)
    
    # Prepared by info
    elements.append(Paragraph(f'<b>Prepared by:</b> {ssc.fullname} ({getattr(ssc, "position", "SSC Staff")})', meta_style))
    elements.append(Paragraph(f'<b>Date Generated:</b> {datetime.now().strftime("%B %d, %Y at %I:%M %p")}', meta_style))
    elements.append(Spacer(1, 16))

    # Simple KPI table with wrapped headers to prevent overlapping
    header_style = ParagraphStyle(
        name='KPIHeader',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=9,
        fontName='Helvetica-Bold',
        textColor=colors.white,
        leading=11
    )
    kpi_header = [
        Paragraph('Total<br/>Concerns', header_style),
        Paragraph('Resolved', header_style),
        Paragraph('Processing', header_style),
        Paragraph('Resolution<br/>Rate', header_style),
        Paragraph('Avg Response<br/>Time', header_style),
        Paragraph('Avg Resolution<br/>Time', header_style)
    ]
    kpi_values = [
        str(total_concerns_handled),
        str(resolved_concerns),
        str(processing_concerns),
        f'{resolution_rate:.1f}%',
        f'{avg_response_time:.1f} hrs',
        f'{avg_resolution_time:.1f} hrs'
    ]
    # Adjusted column widths: shorter columns for first 3, wider for last 3 with longer text
    kpi_table = Table([kpi_header, kpi_values], colWidths=[70, 70, 75, 85, 95, 100])
    kpi_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,1), 10),
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,1), (-1,1), 8),
        ('BOTTOMPADDING', (0,1), (-1,1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    elements.append(kpi_table)
    elements.append(Spacer(1, 20))

    # Monthly performance table - simple style
    monthly_rows = [['Month', 'Total Concerns', 'Resolved', 'Resolution Rate']]
    for item in monthly_data:
        monthly_rows.append([
            item['month'], 
            str(item['total']), 
            str(item['resolved']), 
            f"{item['rate']:.1f}%"
        ])
    monthly_table = Table(monthly_rows, repeatRows=1, colWidths=[124, 124, 124, 124])
    monthly_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    elements.append(Paragraph('<b>Monthly Performance (Last 6 Months)</b>', heading2_style))
    elements.append(monthly_table)
    elements.append(Spacer(1, 16))

    # Priority stats table - simple style
    pr_rows = [['Priority Level', 'Total Concerns', 'Resolved']]
    order_map = {'urgent': 3, 'high': 2, 'medium': 1, 'low': 0}
    for key in sorted(priority_stats.keys(), key=lambda k: order_map.get(str(k).lower(), -1), reverse=True):
        pr = priority_stats[key]
        pr_rows.append([key.title() if key else 'Unknown', str(pr['total']), str(pr['resolved'])])
    pr_table = Table(pr_rows, repeatRows=1, colWidths=[165, 165, 166])
    pr_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    elements.append(Paragraph('<b>Concerns by Priority Level</b>', heading2_style))
    elements.append(pr_table)
    elements.append(Spacer(1, 16))

    # Type stats table - simple style
    tp_rows = [['Concern Type', 'Total Concerns', 'Resolved']]
    for key in sorted(type_stats.keys()):
        tp = type_stats[key]
        tp_rows.append([key.title() if key else 'Unknown', str(tp['total']), str(tp['resolved'])])
    tp_table = Table(tp_rows, repeatRows=1, colWidths=[165, 165, 166])
    tp_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('TOPPADDING', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
    ]))
    elements.append(Paragraph('<b>Concerns by Type</b>', heading2_style))
    elements.append(tp_table)
    elements.append(Spacer(1, 16))

    # Recent concerns - simple style
    if recent_concerns:
        rc_rows = [['ID', 'Title', 'Type', 'Priority', 'Status', 'Submitted Date', 'Resolved Date']]
        for c in recent_concerns:
            rc_rows.append([
                str(c.id),
                c.title[:25] + '...' if len(c.title) > 25 else c.title,
                (c.concern_type.title() if c.concern_type else 'N/A')[:12],
                (c.priority_level.title() if c.priority_level else 'N/A'),
                (c.status.title() if c.status else 'N/A'),
                c.submitted_at.strftime('%m/%d/%Y') if c.submitted_at else 'N/A',
                c.resolved_at.strftime('%m/%d/%Y') if c.resolved_at else 'N/A'
            ])
        rc_table = Table(rc_rows, repeatRows=1, colWidths=[35, 100, 70, 65, 65, 80, 80])
        rc_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,0), 9),
            ('FONTSIZE', (0,1), (-1,-1), 8),
            ('TOPPADDING', (0,0), (-1,0), 8),
            ('BOTTOMPADDING', (0,0), (-1,0), 8),
            ('TOPPADDING', (0,1), (-1,-1), 5),
            ('BOTTOMPADDING', (0,1), (-1,-1), 5),
            ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ]))
        elements.append(Paragraph('<b>Recent Concerns (Last 10)</b>', heading2_style))
        elements.append(rc_table)
    else:
        elements.append(Paragraph('<b>Recent Concerns (Last 10)</b>', heading2_style))
        elements.append(Paragraph('No recent concerns found.', styles['Normal']))
    
    elements.append(Spacer(1, 16))

    # Simple footer
    footer_style = ParagraphStyle(
        name='FootCenter',
        parent=styles['Normal'],
        alignment=TA_CENTER,
        fontSize=8,
        textColor=colors.HexColor('#94a3b8'),
    )
    elements.append(Spacer(1, 12))
    elements.append(Paragraph('This report was automatically generated by the PiyuKonek System<br/>Laguna State Polytechnic University - Sta. Cruz Campus', footer_style))

    # Build and return
    doc.build(elements)
    buffer.seek(0)
    return app.response_class(
        buffer.getvalue(),
        mimetype='application/pdf',
        headers={'Content-Disposition': f'attachment; filename=ssc_analytics_{ssc.username}_{datetime.now().strftime("%Y%m%d")}.pdf'}
    )

@app.route('/admin/upload_profile_image', methods=['POST'])
@login_required('admin')
def admin_upload_profile_image():
    admin = Admin.query.get(session['user_id'])
    if 'profile_image' not in request.files:
        flash('No file part', 'error')
        return redirect(request.referrer or url_for('user_management'))
    file = request.files['profile_image']
    if file.filename == '':
        flash('No selected file', 'error')
        return redirect(request.referrer or url_for('user_management'))
    if file:
        filename = f"admin_profile_{admin.id}_{secure_filename(file.filename)}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        admin.profile_image = filename
        db.session.commit()
        flash('Profile image updated successfully!', 'success')
    return redirect(request.referrer or url_for('user_management'))

# -------------------- INIT --------------------

@app.route('/test_db')
def test_db():
    try:
        # Test database connection
        students = Student.query.all()
        print(f"[DEBUG] Found {len(students)} students in database")
        for student in students:
            print(f"[DEBUG] Student: {student.username}, ID: {student.id}")
        return f"Database test successful. Found {len(students)} students."
    except Exception as e:
        print(f"[DEBUG] Database error: {e}")
        return f"Database error: {e}"

@app.route('/logout')
def logout():
    # Set student as offline if they are logged in as a student
    if 'user_id' in session and session.get('user_type') == 'student':
        student = Student.query.get(session['user_id'])
        if student:
            student.is_online = False
            student.last_seen = datetime.utcnow()
            db.session.commit()
    
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

@app.route('/chat/messages', methods=['GET'])
def get_messages():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    user_id = session['user_id']
    user_type = session['user_type']
    
    # Additional validation for students
    if user_type == 'student':
        student = Student.query.get(user_id)
        if not student or student.status != 'active':
            return jsonify({'error': 'Account not active'}), 403
    
    concern_id = request.args.get('concern_id', type=int)
    query = Message.query.filter(
        ((Message.sender_id == user_id) & (Message.sender_type == user_type)) |
        ((Message.recipient_id == user_id) & (Message.recipient_type == user_type))
    )
    if concern_id:
        query = query.filter(Message.concern_id == concern_id)
    messages = query.order_by(Message.timestamp.asc()).all()
    result = []
    for m in messages:
        student_name = None
        student_course = None
        sender_name = None
        sender_profile_image = None
        # If sender is student, get their info
        if m.sender_type == 'student':
            student = Student.query.get(m.sender_id)
            if student:
                student_name = student.fullname
                student_course = student.course
                sender_name = student.fullname
                sender_profile_image = student.profile_image
        elif m.sender_type == 'admin':
            admin = Admin.query.get(m.sender_id)
            if admin:
                sender_name = admin.fullname
                sender_profile_image = admin.profile_image
        elif m.sender_type == 'ssc':
            ssc = SSC.query.get(m.sender_id)
            if ssc:
                sender_name = ssc.fullname
                sender_profile_image = ssc.profile_image
        # If recipient is student, get their info (for replies)
        elif m.recipient_type == 'student':
            student = Student.query.get(m.recipient_id)
            if student:
                student_name = student.fullname
                student_course = student.course
        result.append({
            'id': m.id,
            'sender_id': m.sender_id,
            'sender_type': m.sender_type,
            'recipient_id': m.recipient_id,
            'recipient_type': m.recipient_type,
            'content': m.content,
            'attachment': m.attachment_path,
            'attachment_name': m.attachment_name,
            'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M'),
            'concern_id': m.concern_id,
            'student_name': student_name,
            'student_course': student_course,
            'sender_name': sender_name,
            'sender_profile_image': sender_profile_image
        })
    return jsonify(result)

@app.route('/chat/messages', methods=['POST'])
def send_message():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    sender_id = session['user_id']
    sender_type = session['user_type']
    
    # Additional validation for students
    if sender_type == 'student':
        student = Student.query.get(sender_id)
        if not student or student.status != 'active':
            return jsonify({'error': 'Account not active'}), 403
    concern_id = None
    if request.content_type and 'multipart/form-data' in request.content_type:
        recipient_id = request.form.get('recipient_id')
        recipient_type = request.form.get('recipient_type')
        content = request.form.get('content', '')
        concern_id = request.form.get('concern_id', type=int)
        # Handle file uploads (existing code)
        attachment_path = None
        attachment_name = None
        attachment_type = None
        files = []
        for key in request.files:
            if key.startswith('file_'):
                files.append(request.files[key])
        if files:
            file = files[0]
            if file and file.filename:
                filename = secure_filename(file.filename)
                import time
                timestamp = int(time.time())
                unique_filename = f"chat_{sender_id}_{timestamp}_{filename}"
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                attachment_path = unique_filename
                attachment_name = file.filename
                attachment_type = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        message = Message(
            sender_id=sender_id,
            sender_type=sender_type,
            recipient_id=recipient_id,
            recipient_type=recipient_type,
            content=content,
            attachment_path=attachment_path,
            attachment_name=attachment_name,
            attachment_type=attachment_type,
            concern_id=concern_id
        )
    else:
        data = request.get_json()
        recipient_id = data.get('recipient_id')
        recipient_type = data.get('recipient_type')
        content = data.get('content')
        concern_id = data.get('concern_id')
        if not all([recipient_id, recipient_type, content]):
            return jsonify({'error': 'Missing fields'}), 400
        message = Message(
            sender_id=sender_id,
            sender_type=sender_type,
            recipient_id=recipient_id,
            recipient_type=recipient_type,
            content=content,
            concern_id=concern_id
        )
    db.session.add(message)
    db.session.commit()
    return jsonify({'success': True, 'message': {
        'id': message.id,
        'sender_id': message.sender_id,
        'sender_type': message.sender_type,
        'recipient_id': message.recipient_id,
        'recipient_type': message.recipient_type,
        'content': message.content,
        'attachment': message.attachment_path,
        'attachment_name': message.attachment_name,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M'),
        'concern_id': message.concern_id
    }})

@app.route('/chat/files/<filename>')
def chat_file(filename):
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401

    if not filename.startswith('chat_'):
        return jsonify({'error': 'Invalid file'}), 403

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    abs_file_path = os.path.abspath(file_path)
    print('Looking for file at:', file_path)
    print('Absolute path:', abs_file_path)
    if os.path.exists(abs_file_path):
        # Use the directory and filename separately for robust serving
        return send_from_directory(os.path.dirname(abs_file_path), filename)
    else:
        print('File not found at:', abs_file_path)
        return jsonify({'error': 'File not found'}), 404

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Online status management routes
@app.route('/update_online_status', methods=['POST'])
def update_online_status():
    if 'user_id' not in session or session.get('user_type') != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    
    student_id = session['user_id']
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Update online status and last seen
    student.is_online = True
    student.last_seen = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/set_offline', methods=['POST'])
def set_offline():
    if 'user_id' not in session or session.get('user_type') != 'student':
        return jsonify({'error': 'Unauthorized'}), 401
    
    student_id = session['user_id']
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Set offline status
    student.is_online = False
    student.last_seen = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/get_students_online_status')
def get_students_online_status():
    if 'user_id' not in session or session.get('user_type') not in ['ssc', 'admin']:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get all students with their online status
    students = Student.query.all()
    online_status = {}
    
    for student in students:
        online_status[student.id] = {
            'is_online': student.is_online,
            'last_seen': student.last_seen.isoformat() if student.last_seen else None
        }
    
    return jsonify(online_status)

@app.route('/test_online_status')
def test_online_status():
    """Test route to verify online status functionality"""
    students = Student.query.all()
    result = []
    
    for student in students:
        result.append({
            'id': student.id,
            'name': student.fullname,
            'is_online': student.is_online,
            'last_seen': student.last_seen.isoformat() if student.last_seen else None,
            'status': student.status
        })
    
    return jsonify({
        'total_students': len(result),
        'online_students': sum(1 for s in result if s['is_online']),
        'offline_students': sum(1 for s in result if not s['is_online']),
        'students': result
    })

@login_required('admin')
@app.route('/admin/messages')
def admin_messages():
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_conversation/<int:student_id>', methods=['POST'])
@login_required('admin')
def delete_conversation(student_id):
    admin_id = session.get('user_id')
    try:
        Message.query.filter(
            ((Message.sender_id == admin_id) & (Message.recipient_id == student_id) & (Message.sender_type == 'admin') & (Message.recipient_type == 'student')) |
            ((Message.sender_id == student_id) & (Message.recipient_id == admin_id) & (Message.sender_type == 'student') & (Message.recipient_type == 'admin'))
        ).delete(synchronize_session=False)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/ssc/messages')
@login_required('ssc')
def ssc_message():
    ssc_id = session.get('user_id')
    # Only include students who have at least one message with non-empty/whitespace content or an attachment
    student_ids = db.session.query(Message.sender_id).filter(
        or_(
            and_(
                (((Message.recipient_type == 'ssc') & (Message.sender_type == 'student')) |
                 ((Message.recipient_type == 'admin') & (Message.sender_type == 'student'))),
                (func.length(func.trim(Message.content)) > 0)
            ),
            and_(
                (((Message.recipient_type == 'ssc') & (Message.sender_type == 'student')) |
                 ((Message.recipient_type == 'admin') & (Message.sender_type == 'student'))),
                Message.attachment_path != None
            )
        )
    ).distinct().all()
    student_ids = [sid[0] for sid in student_ids]
    students = Student.query.filter(Student.id.in_(student_ids)).all()
    student_list = [{
        'id': s.id,
        'fullname': s.fullname,
        'profile_image': s.profile_image,
        'is_online': s.is_online,
        'email_address': s.email_address,
        'course': s.course,
        'year_lvl': s.year_lvl,
        'type': 'student'
    } for s in students]

    # Get selected recipient (student or admin)
    selected_id = request.args.get('student_id', type=int)
    selected_type = request.args.get('type', default='student')
    conversation = []
    selected_recipient = None
    if selected_id:
        if selected_type == 'admin':
            selected_recipient = Admin.query.get(selected_id)
            # Get all messages between SSC and this admin
            conversation_msgs = Message.query.filter(
                (
                    ((Message.sender_id == ssc_id) & (Message.sender_type == 'ssc') & (Message.recipient_id == selected_id) & (Message.recipient_type == 'admin')) |
                    ((Message.sender_id == selected_id) & (Message.sender_type == 'admin') & (Message.recipient_id == ssc_id) & (Message.recipient_type == 'ssc'))
                )
            ).order_by(Message.timestamp.asc()).all()
        else:
            selected_recipient = Student.query.get(selected_id)
            # Get all messages between SSC/admin and this student
            conversation_msgs = Message.query.filter(
                (
                    ((Message.sender_id == ssc_id) & (Message.sender_type == 'ssc') & (Message.recipient_id == selected_id) & (Message.recipient_type == 'student')) |
                    ((Message.sender_id == selected_id) & (Message.sender_type == 'student') & (Message.recipient_id == ssc_id) & (Message.recipient_type == 'ssc')) |
                    ((Message.sender_type == 'admin') & (Message.recipient_id == selected_id) & (Message.recipient_type == 'student')) |
                    ((Message.sender_id == selected_id) & (Message.sender_type == 'student') & (Message.recipient_type == 'admin'))
                )
            ).order_by(Message.timestamp.asc()).all()
        for m in conversation_msgs:
            sender_name = None
            sender_profile_image = None
            is_ssc = False
            is_admin = False
            if m.sender_type == 'student':
                sender_name = selected_recipient.fullname
                sender_profile_image = selected_recipient.profile_image
            elif m.sender_type == 'ssc':
                ssc = SSC.query.get(ssc_id)
                sender_name = ssc.fullname
                sender_profile_image = ssc.profile_image
                is_ssc = True
            elif m.sender_type == 'admin':
                admin = Admin.query.get(m.sender_id)
                sender_name = admin.fullname if admin else 'Admin'
                sender_profile_image = admin.profile_image if admin else None
                is_admin = True
            conversation.append({
                'sender_name': sender_name,
                'sender_profile_image': sender_profile_image,
                'content': m.content,
                'timestamp': m.timestamp.strftime('%Y-%m-%d %H:%M'),
                'is_ssc': is_ssc,
                'is_admin': is_admin,
                'attachment_path': m.attachment_path,
                'attachment_type': m.attachment_type,
                'attachment_name': m.attachment_name
            })
    return render_template(
        'ssc/ssc_message.html',
        students=student_list,
        conversation=conversation,
        selected_student=selected_recipient,
        selected_type=selected_type
    )

@app.route('/ssc/delete_conversation/<int:student_id>', methods=['POST'])
@login_required('ssc')
def ssc_delete_conversation(student_id):
    try:
        ssc_id = session.get('user_id')
        # Delete all messages between this SSC and the student
        Message.query.filter(
            ((Message.sender_id == ssc_id) & (Message.recipient_id == student_id) & (Message.sender_type == 'ssc') & (Message.recipient_type == 'student')) |
            ((Message.sender_id == student_id) & (Message.recipient_id == ssc_id) & (Message.sender_type == 'student') & (Message.recipient_type == 'ssc'))
        ).delete(synchronize_session=False)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/chatbot/analyze_concern', methods=['POST'])
@login_required('student')
def analyze_concern():
    concern_text = request.json.get('concern')
    if not concern_text:
        return jsonify({'error': 'No concern provided'}), 400

    HF_API_TOKEN = app.config.get('HF_API_TOKEN') or os.environ.get('HF_API_TOKEN')
    if not HF_API_TOKEN:
        return jsonify({'error': 'AI chatbot is not configured. Set HF_API_TOKEN.'}), 503
    HF_API_URL = "https://api-inference.huggingface.co/models/google/flan-t5-large"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    payload = {"inputs": f"Give helpful advice for this student concern: {concern_text}"}

    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        print(result)  # <-- Check your terminal for this output!
        # Try to extract the reply
        if isinstance(result, list) and 'generated_text' in result[0]:
            ai_reply = result[0]['generated_text']
        elif isinstance(result, dict) and 'generated_text' in result:
            ai_reply = result['generated_text']
        else:
            ai_reply = str(result)
        return jsonify({'reply': ai_reply})
    except Exception as e:
        print(f"[CHATBOT ERROR] {e}")
        return jsonify({'error': 'Sorry, I could not process your concern.'}), 500

@app.route('/edit_concern/<int:concern_id>', methods=['GET', 'POST'])
@login_required('student')
def edit_concern(concern_id):
    concern = Concern.query.get_or_404(concern_id)
    student_id = session['user_id']
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('concern'))
    
    # Check if student is active
    if student.status != 'active':
        flash('Your account is not active. Please contact support.', 'error')
        return redirect(url_for('concern'))
    
    # Only allow editing if the concern belongs to the student and is pending
    if concern.student_id != student_id or concern.status != 'pending':
        flash('You can only edit your own pending concerns.', 'error')
        return redirect(url_for('concern'))
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('concern-title')
        description = request.form.get('concern-details')
        concern_type = request.form.get('concern-type')
        priority_level = request.form.get('concern-priority')
        
        # Validate required fields
        if not all([title, description, concern_type, priority_level]):
            flash('All fields are required.', 'error')
            return render_template('students/edit_concern.html', concern=concern, student=student)
        
        # Validate file size if uploaded
        docs_file = request.files.get('docs')
        if docs_file and docs_file.filename:
            # Check file size (max 10MB)
            if docs_file.content_length and docs_file.content_length > 10 * 1024 * 1024:
                flash('File size must be less than 10MB.', 'error')
                return render_template('students/edit_concern.html', concern=concern, student=student)
            
            # Validate file type
            allowed_extensions = {'pdf', 'doc', 'docx', 'jpg', 'jpeg', 'png', 'txt'}
            file_ext = docs_file.filename.rsplit('.', 1)[1].lower() if '.' in docs_file.filename else ''
            if file_ext not in allowed_extensions:
                flash('Invalid file type. Allowed: PDF, DOC, DOCX, JPG, PNG, TXT', 'error')
                return render_template('students/edit_concern.html', concern=concern, student=student)
            
            docs_filename = f"concern_{student_id}_{secure_filename(docs_file.filename)}"
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], docs_filename)
            docs_file.save(upload_path)
            concern.docs = docs_filename
        
        # Update concern
        concern.title = title
        concern.description = description
        concern.concern_type = concern_type
        concern.priority_level = priority_level
        
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Error updating concern. Please try again.', 'error')
            print(f"Error updating concern: {e}")
            # Load active concern types
            try:
                concern_types = ConcernType.query.filter_by(is_archived=False).order_by(ConcernType.name.asc()).all()
            except Exception:
                concern_types = []
            return render_template('students/edit_concern.html', concern=concern, student=student, concern_types=concern_types)
        # Add to concern history (audit: student edited)
        history = ConcernHistory(
            concern_id=concern.id,
            status='pending',
            action='Concern edited by student',
            timestamp=datetime.utcnow(),
            actor_type='student',
            actor_id=student_id,
            actor_name=student.fullname
        )
        db.session.add(history)
        db.session.commit()
        flash('Concern updated successfully.', 'success')
        return redirect(url_for('concern'))
    
    # Load active concern types
    try:
        concern_types = ConcernType.query.filter_by(is_archived=False).order_by(ConcernType.name.asc()).all()
    except Exception:
        concern_types = []
    
    return render_template('students/edit_concern.html', concern=concern, student=student, concern_types=concern_types)

@app.route('/student/profile', methods=['GET', 'POST'])
@login_required('student')
def student_profile():
    student_id = session['user_id']
    student = Student.query.get_or_404(student_id)
    
    # Check if student is active
    if student.status != 'active':
        flash('Your account is not active. Please contact support.', 'error')
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        # Get form data
        fullname = request.form.get('fullname')
        email_address = request.form.get('email_address')
        course = request.form.get('course')
        college_dept = request.form.get('college_dept')
        year_lvl = request.form.get('year_lvl')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # Handle profile image upload
        profile_image_file = request.files.get('profile_image')
        if profile_image_file and profile_image_file.filename:
            # Delete old profile image if exists
            if student.profile_image:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], student.profile_image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            # Save new profile image
            profile_image_filename = f"profile_{student.username}_{secure_filename(profile_image_file.filename)}"
            profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_image_filename)
            profile_image_file.save(profile_image_path)
            student.profile_image = profile_image_filename
        
        # Validate email format
        if not email_address or '@' not in email_address:
            flash('Please enter a valid email address.', 'error')
            return render_template('students/profile.html', student=student)
        
        # Check if email is already taken by another student
        existing_student = Student.query.filter_by(email_address=email_address).first()
        if existing_student and existing_student.id != student_id:
            flash('Email address is already registered by another student.', 'error')
            return render_template('students/profile.html', student=student)
        
        # Update basic profile information
        student.fullname = fullname
        student.email_address = email_address
        student.course = course
        student.college_dept = college_dept
        student.year_lvl = year_lvl
        
        # Handle password change if requested
        if current_password and new_password and confirm_password:
            # Verify current password
            if not check_password_hash(student.password, current_password):
                flash('Current password is incorrect.', 'error')
                return render_template('students/profile.html', student=student)
            
            # Validate new password
            if len(new_password) < 8:
                flash('New password must be at least 8 characters long.', 'error')
                return render_template('students/profile.html', student=student)
            
            if not new_password.isalnum():
                flash('New password must contain only letters and numbers (alphanumeric).', 'error')
                return render_template('students/profile.html', student=student)
            
            # Confirm password match
            if new_password != confirm_password:
                flash('New password and confirm password do not match.', 'error')
                return render_template('students/profile.html', student=student)
            
            # Update password
            student.password = generate_password_hash(new_password)
            flash('Password updated successfully.', 'success')
        
        try:
            db.session.commit()
            flash('Profile updated successfully.', 'success')
            return redirect(url_for('student_profile'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'error')
            print(f"Error updating student profile: {e}")
            return render_template('students/profile.html', student=student)
    
    return render_template('students/profile.html', student=student)

@app.route('/ssc/profile', methods=['GET', 'POST'])
@login_required('ssc')
def ssc_profile():
    ssc_id = session['user_id']
    ssc = SSC.query.get_or_404(ssc_id)
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email_address = request.form.get('email_address')
        position = request.form.get('position')
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        # Profile image upload with crop/preview
        profile_image_file = request.files.get('profile_image')
        if profile_image_file and profile_image_file.filename:
            # Delete old profile image if exists
            if ssc.profile_image:
                old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], ssc.profile_image)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            # Save new profile image (unique filename so header/top-right reflects update and avoids cache)
            profile_image_filename = f"ssc_profile_{ssc.username}_{int(time.time())}_{secure_filename(profile_image_file.filename)}"
            profile_image_path = os.path.join(app.config['UPLOAD_FOLDER'], profile_image_filename)
            profile_image_file.save(profile_image_path)
            ssc.profile_image = profile_image_filename
        ssc.fullname = fullname
        ssc.email_address = email_address
        ssc.position = position
        # Password change
        if current_password and new_password and confirm_password:
            if not check_password_hash(ssc.password, current_password):
                flash('Current password is incorrect.', 'error')
                return render_template('ssc/ssc_profile.html', ssc=ssc)
            if len(new_password) < 8 or not new_password.isalnum():
                flash('New password must be at least 8 characters and alphanumeric.', 'error')
                return render_template('ssc/ssc_profile.html', ssc=ssc)
            if new_password != confirm_password:
                flash('New password and confirm password do not match.', 'error')
                return render_template('ssc/ssc_profile.html', ssc=ssc)
            ssc.password = generate_password_hash(new_password)
            flash('You successfully changed your password.', 'success')
        try:
            db.session.commit()
            if not (current_password and new_password and confirm_password):
                flash('Profile updated successfully.', 'success')
            return redirect(url_for('ssc_profile'))
        except Exception as e:
            db.session.rollback()
            flash('Error updating profile. Please try again.', 'error')
    return render_template('ssc/ssc_profile.html', ssc=ssc)

@app.route('/ssc/export/concerns')
@login_required('ssc')
def export_concerns_csv():
    concerns = Concern.query.order_by(Concern.submitted_at.desc()).all()
    si = StringIO()
    writer = csv.writer(si)
    # Write header
    writer.writerow([
        'ID', 'Student Name', 'Title', 'Description', 'Type', 'Priority', 'Status', 'Submitted At', 'Resolved At', 'Resolution Notes'
    ])
    for c in concerns:
        writer.writerow([
            c.id,
            c.student.fullname if c.student else '',
            c.title,
            c.description,
            c.concern_type,
            c.priority_level,
            c.status,
            c.submitted_at.strftime('%Y-%m-%d %H:%M') if c.submitted_at else '',
            c.resolved_at.strftime('%Y-%m-%d %H:%M') if c.resolved_at else '',
            c.resolution_notes or ''
        ])
    output = si.getvalue()
    si.close()
    return app.response_class(
        output,
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment;filename=concerns_export.csv'
        }
    )

@app.route('/ssc/export/students')
@login_required('ssc')
def export_students_csv():
    students = Student.query.order_by(Student.id.desc()).all()
    si = StringIO()
    writer = csv.writer(si)
    # Write header
    writer.writerow([
        'ID', 'Full Name', 'Username', 'Student ID Number', 'Email', 'Course', 'Department', 'Year Level', 'Status', 'Created At'
    ])
    for s in students:
        writer.writerow([
            s.id,
            s.fullname,
            s.username,
            s.student_id_number,
            s.email_address,
            s.course,
            s.college_dept,
            s.year_lvl,
            s.status,
            s.created_at.strftime('%Y-%m-%d %H:%M') if s.created_at else ''
        ])
    output = si.getvalue()
    si.close()
    return app.response_class(
        output,
        mimetype='text/csv',
        headers={
            'Content-Disposition': 'attachment;filename=students_export.csv'
        }
    )

@app.route('/ssc/export/concern/<int:concern_id>/pdf')
@login_required('ssc')
def export_concern_pdf(concern_id):
    concern = Concern.query.get_or_404(concern_id)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 0.75 * inch

    # University Header
    logo_path = os.path.join(app.static_folder, 'images', 'logo.png')
    if os.path.exists(logo_path):
        p.drawImage(logo_path, inch, y - 0.5*inch, width=0.8*inch, height=0.8*inch, mask='auto')
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, y, "Laguna State Polytechnic University")
    p.setFont("Helvetica", 11)
    p.drawCentredString(width/2, y - 0.25*inch, "Sta. Cruz Campus, Laguna, Philippines")
    y -= 1.1 * inch

    # Report Title
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width/2, y, f"Concern Report")
    y -= 0.3 * inch
    p.setFont("Helvetica-Bold", 13)
    p.drawCentredString(width/2, y, f"Concern ID: {concern.id}")
    y -= 0.5 * inch

    # Concern Details
    p.setFont("Helvetica", 12)
    p.drawString(inch, y, f"Title: {concern.title}")
    y -= 0.25 * inch
    p.drawString(inch, y, f"Student: {concern.student.fullname if concern.student else ''}")
    y -= 0.25 * inch
    p.drawString(inch, y, f"Type: {concern.concern_type}")
    y -= 0.25 * inch
    p.drawString(inch, y, f"Priority: {concern.priority_level}")
    y -= 0.25 * inch
    p.drawString(inch, y, f"Status: {concern.status}")
    y -= 0.25 * inch
    p.drawString(inch, y, f"Date Submitted: {concern.submitted_at.strftime('%Y-%m-%d %H:%M') if concern.submitted_at else ''}")
    y -= 0.25 * inch
    if concern.resolved_at:
        p.drawString(inch, y, f"Date Resolved: {concern.resolved_at.strftime('%Y-%m-%d %H:%M')}")
        y -= 0.25 * inch
    y -= 0.15 * inch
    p.line(inch, y, width - inch, y)
    y -= 0.3 * inch

    # Description Section
    p.setFont("Helvetica-Bold", 13)
    p.drawString(inch, y, "Description:")
    y -= 0.2 * inch
    p.setFont("Helvetica", 12)
    max_width = width - 2*inch - 0.15*inch
    def wrap_text(text, fontname, fontsize, max_width):
        lines = []
        for paragraph in text.splitlines():
            if not paragraph.strip():
                lines.append('')
                continue
            line = ''
            for word in paragraph.split():
                test_line = f'{line} {word}'.strip()
                if p.stringWidth(test_line, fontname, fontsize) <= max_width:
                    line = test_line
                else:
                    if line:
                        lines.append(line)
                    line = word
            if line:
                lines.append(line)
        return lines
    desc_lines = wrap_text(concern.description, "Helvetica", 12, max_width)
    for line in desc_lines:
        p.drawString(inch + 0.15*inch, y, line)
        y -= 0.18 * inch

    # Resolution Notes Section
    if concern.resolution_notes:
        y -= 0.1 * inch
        p.setFont("Helvetica-Bold", 13)
        p.drawString(inch, y, "Resolution Notes:")
        y -= 0.2 * inch
        p.setFont("Helvetica", 12)
        res_lines = wrap_text(concern.resolution_notes, "Helvetica", 12, max_width)
        for line in res_lines:
            p.drawString(inch + 0.15*inch, y, line)
            y -= 0.18 * inch

    # Signature/Prepared by
    y -= 0.5 * inch
    p.setFont("Helvetica", 11)
    p.drawString(inch, y, f"Prepared by: {session.get('user_type').upper()} - {session.get('user_id')}")
    y -= 0.2 * inch
    p.drawString(inch, y, f"Date Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Footer
    p.setFont("Helvetica-Oblique", 9)
    p.setFillGray(0.5)
    p.drawCentredString(width/2, 0.6*inch, "This is a system-generated report from PiyuKonek.")
    p.setFillGray(0)

    p.showPage()
    p.save()
    buffer.seek(0)
    return app.response_class(
        buffer.getvalue(),
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment;filename=concern_{concern.id}_formal.pdf'
        }
    )

@app.route('/admin/export/concern/<int:concern_id>/pdf')
@login_required('admin')
def admin_export_concern_pdf(concern_id):
    concern = Concern.query.get_or_404(concern_id)
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 0.75 * inch

    # University Header
    logo_path = os.path.join(app.static_folder, 'images', 'logo.png')
    if os.path.exists(logo_path):
        p.drawImage(logo_path, inch, y - 0.5*inch, width=0.8*inch, height=0.8*inch, mask='auto')
    p.setFont("Helvetica-Bold", 16)
    p.drawCentredString(width/2, y, "Laguna State Polytechnic University")
    p.setFont("Helvetica", 11)
    p.drawCentredString(width/2, y - 0.25*inch, "Sta. Cruz Campus, Laguna, Philippines")
    y -= 1.1 * inch

    # Report Title
    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width/2, y, f"Concern Report")
    y -= 0.3 * inch
    p.setFont("Helvetica-Bold", 13)
    p.drawCentredString(width/2, y, f"Concern ID: {concern.id}")
    y -= 0.5 * inch

    # Concern Details
    p.setFont("Helvetica", 12)
    p.drawString(inch, y, f"Title: {concern.title}")
    y -= 0.25 * inch
    p.drawString(inch, y, f"Student: {concern.student.fullname if concern.student else ''}")
    y -= 0.25 * inch
    p.drawString(inch, y, f"Type: {concern.concern_type}")
    y -= 0.25 * inch
    p.drawString(inch, y, f"Priority: {concern.priority_level}")
    y -= 0.25 * inch
    p.drawString(inch, y, f"Status: {concern.status}")
    y -= 0.25 * inch
    p.drawString(inch, y, f"Date Submitted: {concern.submitted_at.strftime('%Y-%m-%d %H:%M') if concern.submitted_at else ''}")
    y -= 0.25 * inch
    if concern.resolved_at:
        p.drawString(inch, y, f"Date Resolved: {concern.resolved_at.strftime('%Y-%m-%d %H:%M')}")
        y -= 0.25 * inch
    y -= 0.15 * inch
    p.line(inch, y, width - inch, y)
    y -= 0.3 * inch

    # Description Section
    p.setFont("Helvetica-Bold", 13)
    p.drawString(inch, y, "Description:")
    y -= 0.2 * inch
    p.setFont("Helvetica", 12)
    max_width = width - 2*inch - 0.15*inch
    def wrap_text(text, fontname, fontsize, max_width):
        lines = []
        for paragraph in text.splitlines():
            if not paragraph.strip():
                lines.append('')
                continue
            line = ''
            for word in paragraph.split():
                test_line = f'{line} {word}'.strip()
                if p.stringWidth(test_line, fontname, fontsize) <= max_width:
                    line = test_line
                else:
                    if line:
                        lines.append(line)
                    line = word
            if line:
                lines.append(line)
        return lines
    desc_lines = wrap_text(concern.description, "Helvetica", 12, max_width)
    for line in desc_lines:
        p.drawString(inch + 0.15*inch, y, line)
        y -= 0.18 * inch

    # Resolution Notes Section
    if concern.resolution_notes:
        y -= 0.1 * inch
        p.setFont("Helvetica-Bold", 13)
        p.drawString(inch, y, "Resolution Notes:")
        y -= 0.2 * inch
        p.setFont("Helvetica", 12)
        res_lines = wrap_text(concern.resolution_notes, "Helvetica", 12, max_width)
        for line in res_lines:
            p.drawString(inch + 0.15*inch, y, line)
            y -= 0.18 * inch

    # Signature/Prepared by
    y -= 0.5 * inch
    p.setFont("Helvetica", 11)
    p.drawString(inch, y, f"Prepared by: ADMIN - {session.get('user_id')}")
    y -= 0.2 * inch
    p.drawString(inch, y, f"Date Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # Footer
    p.setFont("Helvetica-Oblique", 9)
    p.setFillGray(0.5)
    p.drawCentredString(width/2, 0.6*inch, "This is a system-generated report from PiyuKonek.")
    p.setFillGray(0)

    p.showPage()
    p.save()
    buffer.seek(0)
    return app.response_class(
        buffer.getvalue(),
        mimetype='application/pdf',
        headers={
            'Content-Disposition': f'attachment;filename=concern_{concern.id}_formal.pdf'
        }
    )

@app.route('/admin/export/concerns/pdf')
@login_required('admin')
def admin_export_concerns_pdf():
    from reportlab.lib.pagesizes import letter, landscape
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.lib.styles import getSampleStyleSheet
    from datetime import datetime, timedelta
    import io

    # Get filter parameters
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    concern_type = request.args.get('concern_type')
    status = request.args.get('status')

    concerns_query = Concern.query
    # Filter by date range
    if start_date:
        try:
            start_dt = datetime.strptime(start_date, '%Y-%m-%d')
            concerns_query = concerns_query.filter(Concern.submitted_at >= start_dt)
        except Exception:
            pass
    if end_date:
        try:
            end_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            concerns_query = concerns_query.filter(Concern.submitted_at < end_dt)
        except Exception:
            pass
    if concern_type:
        concerns_query = concerns_query.filter(Concern.concern_type == concern_type)
    if status:
        concerns_query = concerns_query.filter(Concern.status == status)
    concerns = concerns_query.order_by(Concern.submitted_at.desc()).all()

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    elements = []
    styles = getSampleStyleSheet()

    # Logo and Title
    logo_path = os.path.join(app.static_folder, 'images', 'logo.png')
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=60, height=60))
    center_style = ParagraphStyle(name='Center', parent=styles['Normal'], alignment=TA_CENTER)
    center_title = ParagraphStyle(name='CenterTitle', parent=styles['Title'], alignment=TA_CENTER)
    center_heading = ParagraphStyle(name='CenterHeading', parent=styles['Heading2'], alignment=TA_CENTER)
    elements.append(Paragraph('<b>Laguna State Polytechnic University</b>', center_title))
    elements.append(Paragraph('Sta. Cruz Campus, Laguna, Philippines', center_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph('<b>Custom Concern Report</b>', center_heading))
    elements.append(Spacer(1, 8))

    # Filter summary
    filter_summary = '<b>Filters:</b> '
    if start_date:
        filter_summary += f'Start Date: {start_date} '
    if end_date:
        filter_summary += f'End Date: {end_date} '
    if concern_type:
        filter_summary += f'Concern Type: {concern_type.title()} '
    if status:
        filter_summary += f'Status: {status.title()} '
    if filter_summary == '<b>Filters:</b> ':
        filter_summary += 'None (All Concerns)'
    elements.append(Paragraph(filter_summary, styles['Normal']))
    elements.append(Spacer(1, 8))

    # Table header
    data = [[
        'ID', 'Student Name', 'Title', 'Type', 'Priority', 'Status', 'Submitted At', 'Resolved At'
    ]]
    for c in concerns:
        data.append([
            c.id,
            c.student.fullname if c.student else '',
            c.title,
            c.concern_type,
            c.priority_level,
            c.status,
            c.submitted_at.strftime('%Y-%m-%d %H:%M') if c.submitted_at else '',
            c.resolved_at.strftime('%Y-%m-%d %H:%M') if c.resolved_at else ''
        ])
    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 11),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTSIZE', (0,1), (-1,-1), 10),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))
    # Get the logged-in admin's full name
    admin_id = session.get('user_id')
    admin = Admin.query.get(admin_id)
    admin_name = admin.fullname if admin else f'ADMIN - {admin_id}'
    right_style = ParagraphStyle(name='Right', parent=styles['Normal'], alignment=TA_RIGHT)
    elements.append(Paragraph(f"Prepared by: {admin_name} (Admin)", right_style))
    elements.append(Paragraph(f"Date Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", right_style))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph('<font size=8 color="#888888">This is a system-generated report from PiyuKonek.</font>', center_style))
    doc.build(elements)
    buffer.seek(0)
    return app.response_class(
        buffer.getvalue(),
        mimetype='application/pdf',
        headers={
            'Content-Disposition': 'attachment;filename=concerns_custom_report.pdf'
        }
    )

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = None
        user_type = None
        # Try to find user in all tables
        student = Student.query.filter_by(email_address=email).first()
        if student:
            user = student
            user_type = 'student'
        else:
            ssc = SSC.query.filter_by(email_address=email).first()
            if ssc:
                user = ssc
                user_type = 'ssc'
            else:
                admin = Admin.query.filter_by(email_address=email).first()
                if admin:
                    user = admin
                    user_type = 'admin'
                else:
                    user = User.query.filter_by(email=email).first()
                    if user:
                        user_type = user.user_type
        if user:
            token = serializer.dumps({'email': email, 'user_type': user_type}, salt='password-reset-salt')
            reset_url = url_for('reset_password', token=token, _external=True)
            try:
                msg = MailMessage('PiyuKonek Password Reset', recipients=[email])
                msg.body = f"Hello,\n\nTo reset your password, click the link below:\n{reset_url}\n\nIf you did not request this, please ignore this email.\n\n- PiyuKonek Team"
                mail.send(msg)
                flash('A password reset link has been sent to your email address.', 'info')
            except Exception as e:
                print(f"[MAIL ERROR] {e}")
                flash('Failed to send password reset email. Please try again later.', 'danger')
        else:
            flash('No account found with that email address.', 'error')
        return redirect(url_for('forgot_password'))
    return render_template('accounts/forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    try:
        data = serializer.loads(token, salt='password-reset-salt', max_age=3600)
        email = data['email']
        user_type = data['user_type']
    except SignatureExpired:
        flash('The password reset link has expired.', 'error')
        return redirect(url_for('forgot_password'))
    except BadSignature:
        flash('Invalid or tampered password reset link.', 'error')
        return redirect(url_for('forgot_password'))
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if len(new_password) < 8:
            flash('Password must be at least 8 characters long.', 'error')
            return render_template('accounts/reset_password.html', token=token)
        if not new_password.isalnum():
            flash('Password must contain only letters and numbers (alphanumeric).', 'error')
            return render_template('accounts/reset_password.html', token=token)
        if new_password != confirm_password:
            flash('Passwords do not match.', 'error')
            return render_template('accounts/reset_password.html', token=token)
        # Update password in the correct table
        user = None
        if user_type == 'student':
            user = Student.query.filter_by(email_address=email).first()
        elif user_type == 'ssc':
            user = SSC.query.filter_by(email_address=email).first()
        elif user_type == 'admin':
            user = Admin.query.filter_by(email_address=email).first()
        else:
            user = User.query.filter_by(email=email).first()
        if user:
            user.password = generate_password_hash(new_password)
            db.session.commit()
            flash('Your password has been reset successfully. You can now log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('User not found.', 'error')
            return redirect(url_for('forgot_password'))
    return render_template('accounts/reset_password.html', token=token)

@app.route('/mark_all_notifications_read', methods=['POST'])
@login_required('student')
def mark_all_notifications_read():
    student_id = session['user_id']
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Check if student is active
    if student.status != 'active':
        return jsonify({'error': 'Account not active'}), 403
    
    notif_type = request.json.get('type')
    query = Notification.query.filter_by(user_id=student_id, user_type='student')
    if notif_type and notif_type != 'all':
        query = query.filter_by(notification_type=notif_type)
    try:
        query.update({Notification.is_read: True}, synchronize_session=False)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/delete_all_notifications', methods=['POST'])
@login_required('student')
def delete_all_notifications():
    student_id = session['user_id']
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Check if student is active
    if student.status != 'active':
        return jsonify({'error': 'Account not active'}), 403
    
    notif_type = request.json.get('type')
    query = Notification.query.filter_by(user_id=student_id, user_type='student')
    if notif_type and notif_type != 'all':
        query = query.filter_by(notification_type=notif_type)
    try:
        query.delete(synchronize_session=False)
        db.session.commit()
        return jsonify({'success': True})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# -------------------- SMART REMINDER FUNCTIONS --------------------

def check_unresolved_concern_reminders():
    """Check for unresolved concerns and send reminders after 3-5 days"""
    from datetime import datetime, timedelta
    
    # Get concerns that have been pending for more than 3 days
    reminder_date_3 = datetime.utcnow() - timedelta(days=3)
    reminder_date_5 = datetime.utcnow() - timedelta(days=5)
    
    # Check for 3-day reminders
    concerns_3_days = Concern.query.filter(
        Concern.status == 'pending',
        Concern.submitted_at <= reminder_date_3,
        Concern.submitted_at > reminder_date_3 - timedelta(days=1)
    ).all()
    
    # Check for 5-day reminders
    concerns_5_days = Concern.query.filter(
        Concern.status == 'pending',
        Concern.submitted_at <= reminder_date_5,
        Concern.submitted_at > reminder_date_5 - timedelta(days=1)
    ).all()
    
    for concern in concerns_3_days:
        # Check if we already sent a 3-day reminder recently
        recent_reminder = Notification.query.filter(
            Notification.concern_id == concern.id,
            Notification.notification_type == 'reminder_3_days',
            Notification.created_at >= datetime.utcnow() - timedelta(hours=12)
        ).first()
        
        if not recent_reminder:
            # Create reminder notification
            reminder = Notification(
                user_id=concern.student_id,
                user_type='student',
                title='Concern Reminder - 3 Days',
                message=f'Your concern "{concern.title}" has been pending for 3 days. Please check for updates or contact support if needed.',
                notification_type='reminder_3_days',
                concern_id=concern.id,
                created_at=datetime.utcnow()
            )
            db.session.add(reminder)
    
    for concern in concerns_5_days:
        # Check if we already sent a 5-day reminder recently
        recent_reminder = Notification.query.filter(
            Notification.concern_id == concern.id,
            Notification.notification_type == 'reminder_5_days',
            Notification.created_at >= datetime.utcnow() - timedelta(hours=12)
        ).first()
        
        if not recent_reminder:
            # Create urgent reminder notification
            reminder = Notification(
                user_id=concern.student_id,
                user_type='student',
                title='Urgent: Concern Pending - 5 Days',
                message=f'Your concern "{concern.title}" has been pending for 5 days. This is taking longer than usual. Please contact support immediately.',
                notification_type='reminder_5_days',
                concern_id=concern.id,
                created_at=datetime.utcnow()
            )
            db.session.add(reminder)
    
    try:
        db.session.commit()
        print(f"Sent {len(concerns_3_days)} 3-day reminders and {len(concerns_5_days)} 5-day reminders")
    except Exception as e:
        db.session.rollback()
        print(f"Error sending reminders: {e}")

@app.route('/check_reminders', methods=['POST'])
@login_required('student')
def check_reminders():
    """Manual trigger to check for reminders (for testing)"""
    student_id = session['user_id']
    student = Student.query.get(student_id)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Check if student is active
    if student.status != 'active':
        return jsonify({'error': 'Account not active'}), 403
    
    try:
        check_unresolved_concern_reminders()
        return jsonify({'success': True, 'message': 'Reminders checked successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    return jsonify({'success': True})

@app.route('/ssc/concern_types', methods=['GET'])
@login_required('ssc')
def ssc_concern_types():
    try:
        types = ConcernType.query.order_by(ConcernType.name.asc()).all()
        active_types = [t for t in types if not t.is_archived]
        archived_types = [t for t in types if t.is_archived]
        ssc = SSC.query.get(session.get('user_id'))
        return render_template('ssc/ssc_concern_types.html', ssc=ssc, active_types=active_types, archived_types=archived_types)
    except Exception:
        flash('Unable to load concern types.', 'error')
        return redirect(url_for('ssc_concerns'))

@app.route('/ssc/concern_types', methods=['POST'])
@login_required('ssc')
def ssc_add_concern_type():
    name = (request.form.get('name') or '').strip()
    if not name:
        flash('Type name is required.', 'error')
        return redirect(url_for('ssc_concern_types'))
    name_norm = ' '.join(name.split())
    existing = ConcernType.query.filter(db.func.lower(ConcernType.name) == name_norm.lower()).first()
    if existing:
        flash('Concern type already exists.', 'error')
        return redirect(url_for('ssc_concern_types'))
    ct = ConcernType(name=name_norm, created_by=session.get('user_id'))
    db.session.add(ct)
    db.session.commit()
    flash('Concern type added.', 'success')
    return redirect(url_for('ssc_concern_types'))

@app.route('/ssc/concern_types/<int:type_id>', methods=['POST'])
@login_required('ssc')
def ssc_update_concern_type(type_id):
    action = request.form.get('action')
    ct = ConcernType.query.get_or_404(type_id)
    if action == 'archive':
        ct.is_archived = True
        ct.archived_at = datetime.utcnow()
    elif action == 'restore':
        ct.is_archived = False
        ct.archived_at = None
    elif action == 'rename':
        new_name = (request.form.get('name') or '').strip()
        if new_name:
            conflict = ConcernType.query.filter(db.func.lower(ConcernType.name) == new_name.lower(), ConcernType.id != ct.id).first()
            if conflict:
                flash('Another type with that name already exists.', 'error')
                return redirect(url_for('ssc_concern_types'))
            ct.name = ' '.join(new_name.split())
    db.session.commit()
    flash('Concern type updated.', 'success')
    return redirect(url_for('ssc_concern_types'))

# Admin Concern Types Routes
@app.route('/admin/concern_types', methods=['GET'])
@login_required('admin')
def admin_concern_types():
    try:
        types = ConcernType.query.order_by(ConcernType.name.asc()).all()
        active_types = [t for t in types if not t.is_archived]
        archived_types = [t for t in types if t.is_archived]
        admin = Admin.query.get(session.get('user_id'))
        return render_template('admin/admin_concern_types.html', admin=admin, active_types=active_types, archived_types=archived_types)
    except Exception:
        flash('Unable to load concern types.', 'error')
        return redirect(url_for('admin_concern'))

@app.route('/admin/concern_types', methods=['POST'])
@login_required('admin')
def admin_add_concern_type():
    name = (request.form.get('name') or '').strip()
    if not name:
        flash('Type name is required.', 'error')
        return redirect(url_for('admin_concern_types'))
    name_norm = ' '.join(name.split())
    existing = ConcernType.query.filter(db.func.lower(ConcernType.name) == name_norm.lower()).first()
    if existing:
        flash('Concern type already exists.', 'error')
        return redirect(url_for('admin_concern_types'))
    ct = ConcernType(name=name_norm, created_by=session.get('user_id'))
    db.session.add(ct)
    db.session.commit()
    flash('Concern type added.', 'success')
    return redirect(url_for('admin_concern_types'))

@app.route('/admin/concern_types/<int:type_id>', methods=['POST'])
@login_required('admin')
def admin_update_concern_type(type_id):
    action = request.form.get('action')
    ct = ConcernType.query.get_or_404(type_id)
    if action == 'archive':
        ct.is_archived = True
        ct.archived_at = datetime.utcnow()
    elif action == 'restore':
        ct.is_archived = False
        ct.archived_at = None
    elif action == 'rename':
        new_name = (request.form.get('name') or '').strip()
        if new_name:
            conflict = ConcernType.query.filter(db.func.lower(ConcernType.name) == new_name.lower(), ConcernType.id != type_id).first()
            if conflict:
                flash('Another type with that name already exists.', 'error')
                return redirect(url_for('admin_concern_types'))
            ct.name = ' '.join(new_name.split())
    db.session.commit()
    flash('Concern type updated.', 'success')
    return redirect(url_for('admin_concern_types'))

# -------------------- DEPARTMENT AND COURSE MANAGEMENT --------------------

@app.route('/admin/departments')
@login_required('admin')
def admin_departments():
    """Admin page for managing departments"""
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('search', '').strip()
    
    # Build query
    query = Department.query
    
    # Apply filters
    if status_filter == 'active':
        query = query.filter(Department.status == 'active')
    elif status_filter == 'archived':
        query = query.filter(Department.status == 'archived')
    
    if search_query:
        query = query.filter(
            db.or_(
                Department.name.ilike(f'%{search_query}%'),
                Department.code.ilike(f'%{search_query}%'),
                Department.description.ilike(f'%{search_query}%')
            )
        )
    
    # Get departments with course counts
    departments = query.order_by(Department.name).all()
    
    # Add course counts to each department
    for dept in departments:
        dept.active_courses_count = Course.query.filter(
            Course.department_id == dept.id,
            Course.status == 'active'
        ).count()
        dept.total_courses_count = Course.query.filter(
            Course.department_id == dept.id
        ).count()
    
    return render_template('admin/admin_departments.html', 
                         departments=departments,
                         status_filter=status_filter,
                         search_query=search_query)

@app.route('/admin/departments/add', methods=['POST'])
@login_required('admin')
def admin_add_department():
    """Add a new department"""
    name = request.form.get('name', '').strip()
    code = request.form.get('code', '').strip().upper()
    description = request.form.get('description', '').strip()
    
    if not name or not code:
        flash('Department name and code are required.', 'error')
        return redirect(url_for('admin_departments'))
    
    # Check for duplicates
    existing_name = Department.query.filter(db.func.lower(Department.name) == name.lower()).first()
    if existing_name:
        flash('A department with this name already exists.', 'error')
        return redirect(url_for('admin_departments'))
    
    existing_code = Department.query.filter(db.func.lower(Department.code) == code.lower()).first()
    if existing_code:
        flash('A department with this code already exists.', 'error')
        return redirect(url_for('admin_departments'))
    
    try:
        department = Department(
            name=name,
            code=code,
            description=description if description else None,
            created_by=session.get('user_id', 1)  # Default to 1 if no user_id in session
        )
        db.session.add(department)
        db.session.commit()
        flash(f'Department "{name}" added successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error adding department. Please try again.', 'error')
    
    return redirect(url_for('admin_departments'))

@app.route('/admin/departments/<int:dept_id>/update', methods=['POST'])
@login_required('admin')
def admin_update_department(dept_id):
    """Update department details"""
    department = Department.query.get_or_404(dept_id)
    
    name = request.form.get('name', '').strip()
    code = request.form.get('code', '').strip().upper()
    description = request.form.get('description', '').strip()
    
    if not name or not code:
        flash('Department name and code are required.', 'error')
        return redirect(url_for('admin_departments'))
    
    # Check for duplicates (excluding current department)
    existing_name = Department.query.filter(
        db.func.lower(Department.name) == name.lower(),
        Department.id != dept_id
    ).first()
    if existing_name:
        flash('A department with this name already exists.', 'error')
        return redirect(url_for('admin_departments'))
    
    existing_code = Department.query.filter(
        db.func.lower(Department.code) == code.lower(),
        Department.id != dept_id
    ).first()
    if existing_code:
        flash('A department with this code already exists.', 'error')
        return redirect(url_for('admin_departments'))
    
    try:
        department.name = name
        department.code = code
        department.description = description if description else None
        db.session.commit()
        flash(f'Department "{name}" updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating department. Please try again.', 'error')
    
    return redirect(url_for('admin_departments'))

@app.route('/admin/departments/<int:dept_id>/archive', methods=['POST'])
@login_required('admin')
def admin_archive_department(dept_id):
    """Archive a department"""
    department = Department.query.get_or_404(dept_id)
    
    if department.status == 'archived':
        flash('Department is already archived.', 'warning')
        return redirect(url_for('admin_departments'))
    
    try:
        department.status = 'archived'
        # Also archive all courses in this department
        Course.query.filter(Course.department_id == dept_id).update({'status': 'archived'})
        db.session.commit()
        flash(f'Department "{department.name}" and all its courses have been archived.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error archiving department. Please try again.', 'error')
    
    return redirect(url_for('admin_departments'))

@app.route('/admin/departments/<int:dept_id>/restore', methods=['POST'])
@login_required('admin')
def admin_restore_department(dept_id):
    """Restore an archived department"""
    department = Department.query.get_or_404(dept_id)
    
    if department.status == 'active':
        flash('Department is already active.', 'warning')
        return redirect(url_for('admin_departments'))
    
    try:
        department.status = 'active'
        db.session.commit()
        flash(f'Department "{department.name}" has been restored.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error restoring department. Please try again.', 'error')
    
    return redirect(url_for('admin_departments'))

@app.route('/admin/courses')
@login_required('admin')
def admin_courses():
    """Admin page for managing courses"""
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    dept_filter = request.args.get('department', 'all')
    search_query = request.args.get('search', '').strip()
    
    # Build query
    query = db.session.query(Course, Department).join(Department, Course.department_id == Department.id)
    
    # Apply filters
    if status_filter == 'active':
        query = query.filter(Course.status == 'active')
    elif status_filter == 'archived':
        query = query.filter(Course.status == 'archived')
    
    if dept_filter != 'all':
        try:
            dept_id = int(dept_filter)
            query = query.filter(Course.department_id == dept_id)
        except ValueError:
            pass
    
    if search_query:
        query = query.filter(
            db.or_(
                Course.name.ilike(f'%{search_query}%'),
                Course.code.ilike(f'%{search_query}%'),
                Course.description.ilike(f'%{search_query}%'),
                Department.name.ilike(f'%{search_query}%')
            )
        )
    
    # Get courses with department info
    course_data = query.order_by(Department.name, Course.name).all()
    
    # Get all active departments for the filter dropdown
    departments = Department.query.filter(Department.status == 'active').order_by(Department.name).all()
    
    return render_template('admin/admin_courses.html', 
                         course_data=course_data,
                         departments=departments,
                         status_filter=status_filter,
                         dept_filter=dept_filter,
                         search_query=search_query)

@app.route('/admin/courses/add', methods=['POST'])
@login_required('admin')
def admin_add_course():
    """Add a new course"""
    name = request.form.get('name', '').strip()
    code = request.form.get('code', '').strip().upper()
    description = request.form.get('description', '').strip()
    department_id = request.form.get('department_id')
    
    if not name or not code or not department_id:
        flash('Course name, code, and department are required.', 'error')
        return redirect(url_for('admin_courses'))
    
    try:
        department_id = int(department_id)
        department = Department.query.get(department_id)
        if not department or department.status != 'active':
            flash('Invalid or inactive department selected.', 'error')
            return redirect(url_for('admin_courses'))
    except ValueError:
        flash('Invalid department selected.', 'error')
        return redirect(url_for('admin_courses'))
    
    # Check for duplicate course code within the department
    existing_course = Course.query.filter(
        db.func.lower(Course.code) == code.lower(),
        Course.department_id == department_id
    ).first()
    if existing_course:
        flash('A course with this code already exists in this department.', 'error')
        return redirect(url_for('admin_courses'))
    
    try:
        course = Course(
            name=name,
            code=code,
            description=description if description else None,
            department_id=department_id,
            created_by=session.get('user_id', 1)  # Default to 1 if no user_id in session
        )
        db.session.add(course)
        db.session.commit()
        flash(f'Course "{name}" added successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error adding course. Please try again.', 'error')
    
    return redirect(url_for('admin_courses'))

@app.route('/admin/courses/<int:course_id>/update', methods=['POST'])
@login_required('admin')
def admin_update_course(course_id):
    """Update course details"""
    course = Course.query.get_or_404(course_id)
    
    name = request.form.get('name', '').strip()
    code = request.form.get('code', '').strip().upper()
    description = request.form.get('description', '').strip()
    department_id = request.form.get('department_id')
    
    if not name or not code or not department_id:
        flash('Course name, code, and department are required.', 'error')
        return redirect(url_for('admin_courses'))
    
    try:
        department_id = int(department_id)
        department = Department.query.get(department_id)
        if not department or department.status != 'active':
            flash('Invalid or inactive department selected.', 'error')
            return redirect(url_for('admin_courses'))
    except ValueError:
        flash('Invalid department selected.', 'error')
        return redirect(url_for('admin_courses'))
    
    # Check for duplicate course code within the department (excluding current course)
    existing_course = Course.query.filter(
        db.func.lower(Course.code) == code.lower(),
        Course.department_id == department_id,
        Course.id != course_id
    ).first()
    if existing_course:
        flash('A course with this code already exists in this department.', 'error')
        return redirect(url_for('admin_courses'))
    
    try:
        course.name = name
        course.code = code
        course.description = description if description else None
        course.department_id = department_id
        db.session.commit()
        flash(f'Course "{name}" updated successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error updating course. Please try again.', 'error')
    
    return redirect(url_for('admin_courses'))

@app.route('/admin/courses/<int:course_id>/archive', methods=['POST'])
@login_required('admin')
def admin_archive_course(course_id):
    """Archive a course"""
    course = Course.query.get_or_404(course_id)
    
    if course.status == 'archived':
        flash('Course is already archived.', 'warning')
        return redirect(url_for('admin_courses'))
    
    try:
        course.status = 'archived'
        db.session.commit()
        flash(f'Course "{course.name}" has been archived.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error archiving course. Please try again.', 'error')
    
    return redirect(url_for('admin_courses'))

@app.route('/admin/courses/<int:course_id>/restore', methods=['POST'])
@login_required('admin')
def admin_restore_course(course_id):
    """Restore an archived course"""
    course = Course.query.get_or_404(course_id)
    
    if course.status == 'active':
        flash('Course is already active.', 'warning')
        return redirect(url_for('admin_courses'))
    
    # Check if the department is active
    if course.department.status != 'active':
        flash('Cannot restore course. The department must be active first.', 'error')
        return redirect(url_for('admin_courses'))
    
    try:
        course.status = 'active'
        db.session.commit()
        flash(f'Course "{course.name}" has been restored.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Error restoring course. Please try again.', 'error')
    
    return redirect(url_for('admin_courses'))

@app.route('/student/reminders')
@login_required('student')
def student_reminders():
    """View pending reminders for the student"""
    student_id = session['user_id']
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('login'))
    
    # Check if student is active
    if student.status != 'active':
        flash('Your account is not active. Please contact support.', 'error')
        return redirect(url_for('login'))
    
    # Get student's unresolved concerns (pending or processing)
    pending_concerns = (
        Concern.query
        .filter(
            Concern.student_id == student_id,
            Concern.status.in_(['pending', 'processing'])
        )
        .order_by(Concern.submitted_at.desc())
        .all()
    )
    
    # Calculate days pending for each concern
    for concern in pending_concerns:
        days_pending = (datetime.utcnow() - concern.submitted_at).days
        concern.days_pending = days_pending
    
    return render_template('students/reminders.html', 
                         student=student, 
                         pending_concerns=pending_concerns)

def get_online_staff():
    online_ssc = SSC.query.filter_by(is_online=True).all()
    online_admins = Admin.query.filter_by().all()  # If you want only online admins, add is_online=True if available
    online_list = []
    for s in online_ssc:
        online_list.append(f"SSC: {s.fullname}")
    for a in online_admins:
        if hasattr(a, 'is_online') and a.is_online:
            online_list.append(f"Admin: {a.fullname}")
    return online_list

def send_concern_reply_email(student_email, student_name, concern_title, resolution_notes, responder_name, responder_role, has_attachment=False):
    attachment_info = ""
    if has_attachment:
        attachment_info = "\n\nRESPONSE ATTACHMENT:\n------------------\nA file has been attached to this response. Please log in to the portal to view and download the attachment."
    
    try:
        import resend
        import os
        resend.api_key = os.environ.get('RESEND_API_KEY')

        email_html = f"""
        <p>Dear {student_name},</p>
        <p>We are pleased to inform you that your concern has been addressed by the Guidance staffs.</p>
        <p><strong>CONCERN DETAILS:</strong><br>
        Title: {concern_title}<br>
        Resolved by: {responder_name} ({responder_role})</p>
        <p><strong>RESOLUTION FEEDBACK:</strong><br>
        {resolution_notes}{attachment_info}</p>
        <p>Best regards,<br>{responder_name}<br>{responder_role}<br>LSPU PiyuKonek Support Team</p>
        """

        resend.Emails.send({
            "from": os.environ.get('MAIL_DEFAULT_SENDER'),
            "to": student_email,
            "subject": f"[LSPU PiyuKonek] Concern Resolution: {concern_title}",
            "html": email_html
        })
    except Exception as e:
        print(f"[MAIL ERROR] {e}")

@app.route('/student/concern/<int:concern_id>/timeline')
@login_required('student')
def student_concern_timeline(concern_id):
    student_id = session['user_id']
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('login'))
    
    # Get the concern and verify it belongs to the student
    concern = Concern.query.get(concern_id)
    if not concern or concern.student_id != student_id:
        flash('Concern not found or access denied.', 'error')
        return redirect(url_for('concern'))
    
    # Get concern timeline/history (newest first)
    timeline = ConcernHistory.query.filter_by(concern_id=concern_id).order_by(ConcernHistory.timestamp.desc()).all()
    
    # Get related messages for this concern
    messages = Message.query.filter_by(concern_id=concern_id).order_by(Message.timestamp.asc()).all()
    
    # Build single list of all events sorted by date descending (newest at top)
    events = []
    if concern.submitted_at:
        events.append({'type': 'submission', 'timestamp': concern.submitted_at})
    for h in timeline:
        events.append({'type': 'history', 'timestamp': h.timestamp, 'event': h})
    for m in messages:
        events.append({'type': 'message', 'timestamp': m.timestamp, 'message': m})
    
    # Add guidance response event if resolution_notes exists (even if status is not resolved)
    # This ensures guidance responses are always shown in timeline, even if status is still 'processing'
    if concern.resolution_notes:
        # Find if there's already a history entry for this response
        response_history = None
        for h in timeline:
            if 'responded' in h.action.lower() or 'response' in h.action.lower():
                response_history = h
                break
        
        # If no history entry found but we have resolution_notes and resolved_at, create event
        # This handles cases where response was added but history wasn't created properly
        if not response_history and concern.resolved_at:
            events.append({
                'type': 'guidance_response', 
                'timestamp': concern.resolved_at,
                'response': concern.resolution_notes,
                'attachment': concern.response_attachment,
                'responder': concern.resolved_by
            })
        # If history entry exists, mark it so template can show response content
        elif response_history:
            # The template will check for 'responded' in action and show resolution_notes
            pass
    
    # Add resolved event if status is resolved
    if concern.status == 'resolved' and concern.resolved_at:
        # Check if we already added a guidance_response event for this timestamp
        has_response_event = any(
            e.get('type') == 'guidance_response' and 
            e.get('timestamp') == concern.resolved_at 
            for e in events
        )
        if not has_response_event:
            events.append({'type': 'resolved', 'timestamp': concern.resolved_at})
    
    events.sort(key=lambda x: x['timestamp'] or datetime.min, reverse=True)
    
    # Get notifications related to this concern
    notifications = Notification.query.filter_by(concern_id=concern_id, user_id=student_id, user_type='student').order_by(Notification.created_at.asc()).all()
    
    return render_template('students/concern_timeline.html', 
                         concern=concern, 
                         timeline=timeline, 
                         events=events,
                         messages=messages, 
                         notifications=notifications,
                         student=student)

@app.route('/student/concern/<int:concern_id>/timeline/download')
@login_required('student')
def student_concern_timeline_download(concern_id):
    student_id = session['user_id']
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('login'))
    
    # Get the concern and verify it belongs to the student
    concern = Concern.query.get(concern_id)
    if not concern or concern.student_id != student_id:
        flash('Concern not found or access denied.', 'error')
        return redirect(url_for('concern'))
    
    # Get concern timeline/history
    timeline = ConcernHistory.query.filter_by(concern_id=concern_id).order_by(ConcernHistory.timestamp.desc()).all()
    
    # Get related messages for this concern
    messages = Message.query.filter_by(concern_id=concern_id).order_by(Message.timestamp.asc()).all()
    
    # Create PDF
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Add styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=10,
        spaceBefore=15
    )
    normal_style = styles['Normal']
    
    # Title
    elements.append(Paragraph(f"Concern Timeline Report", title_style))
    elements.append(Spacer(1, 20))
    
    # Concern Details
    elements.append(Paragraph(f"<b>Concern Title:</b> {concern.title}", heading_style))
    elements.append(Paragraph(f"<b>Type:</b> {concern.concern_type.title()}", normal_style))
    elements.append(Paragraph(f"<b>Priority:</b> {concern.priority_level.title()}", normal_style))
    elements.append(Paragraph(f"<b>Status:</b> {concern.status.title()}", normal_style))
    elements.append(Paragraph(f"<b>Submitted:</b> {concern.submitted_at.strftime('%B %d, %Y at %I:%M %p')}", normal_style))
    if concern.resolved_at:
        elements.append(Paragraph(f"<b>Resolved:</b> {concern.resolved_at.strftime('%B %d, %Y at %I:%M %p')}", normal_style))
    elements.append(Spacer(1, 20))
    
    # Timeline
    elements.append(Paragraph("Timeline of Events", heading_style))
    for event in timeline:
        elements.append(Paragraph(f"<b>{event.timestamp.strftime('%B %d, %Y at %I:%M %p')}</b>", normal_style))
        elements.append(Paragraph(f"Status: {event.status.title()}", normal_style))
        elements.append(Paragraph(f"Action: {event.action}", normal_style))
        elements.append(Spacer(1, 10))
    
    # Messages
    if messages:
        elements.append(Paragraph("Conversation History", heading_style))
        for message in messages:
            sender_name = "You" if message.sender_id == student_id else "Staff"
            elements.append(Paragraph(f"<b>{message.timestamp.strftime('%B %d, %Y at %I:%M %p')} - {sender_name}</b>", normal_style))
            elements.append(Paragraph(message.content, normal_style))
            if message.attachment_name:
                elements.append(Paragraph(f"Attachment: {message.attachment_name}", normal_style))
            elements.append(Spacer(1, 10))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"concern_timeline_{concern_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mimetype='application/pdf'
    )





@app.route('/student/concern/<int:concern_id>')
@login_required('student')
def view_concern(concern_id):
    """View a specific concern for students"""
    student_id = session['user_id']
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('login'))
    
    # Get the concern and verify it belongs to the student
    concern = Concern.query.get(concern_id)
    if not concern or concern.student_id != student_id:
        flash('Concern not found or access denied.', 'error')
        return redirect(url_for('student_dashboard'))
    
    # Get concern timeline/history
    timeline = ConcernHistory.query.filter_by(concern_id=concern_id).order_by(ConcernHistory.timestamp.desc()).all()
    
    # Get related messages for this concern
    messages = Message.query.filter_by(concern_id=concern_id).order_by(Message.timestamp.asc()).all()
    
    return render_template('students/concern.html', 
                         concern=concern, 
                         timeline=timeline, 
                         messages=messages, 
                         student=student)

# -------------------- STUDENT CONCERN HISTORY EXPORT --------------------

@app.route('/student/export/concern-history')
@login_required('student')
def student_export_concern_history():
    """Export student's complete concern history"""
    student_id = session['user_id']
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('login'))
    
    # Check if student is active
    if student.status != 'active':
        flash('Your account is not active. Please contact support.', 'error')
        return redirect(url_for('login'))
    
    # Get all concerns for the student
    concerns = Concern.query.filter_by(student_id=student_id).order_by(Concern.submitted_at.desc()).all()
    
    if not concerns:
        flash('No concerns found to export.', 'info')
        return redirect(url_for('student_dashboard'))
    
    return export_concern_history_pdf(student, concerns)



def export_concern_history_pdf(student, concerns):
    """Export concern history as PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    elements = []
    
    # Header with logo and title
    logo_path = os.path.join(app.static_folder, 'images', 'logo.png')
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=50, height=50))
    
    title_style = ParagraphStyle(
        name='TitleCenter',
        parent=styles['Title'],
        fontSize=18,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    subtitle_style = ParagraphStyle(
        name='SubtitleCenter',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph('Personal Concern History Report', title_style))
    elements.append(Paragraph('Laguna State Polytechnic University - Sta. Cruz Campus', subtitle_style))
    
    # Student information
    student_style = ParagraphStyle(
        name='StudentInfo',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=20
    )
    
    elements.append(Paragraph(f"<b>Student Name:</b> {student.fullname}", student_style))
    elements.append(Paragraph(f"<b>Student ID:</b> {student.student_id_number}", student_style))
    elements.append(Paragraph(f"<b>Course:</b> {student.course}", student_style))
    elements.append(Paragraph(f"<b>Department:</b> {student.college_dept}", student_style))
    elements.append(Paragraph(f"<b>Year Level:</b> {student.year_lvl}", student_style))
    elements.append(Paragraph(f"<b>Report Generated:</b> {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", student_style))
    elements.append(Spacer(1, 20))
    
    # Summary statistics
    total_concerns = len(concerns)
    resolved_concerns = len([c for c in concerns if c.status == 'resolved'])
    pending_concerns = len([c for c in concerns if c.status == 'pending'])
    processing_concerns = len([c for c in concerns if c.status == 'processing'])
    
    summary_style = ParagraphStyle(
        name='Summary',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=15
    )
    
    elements.append(Paragraph("<b>Summary Statistics:</b>", summary_style))
    elements.append(Paragraph(f"• Total Concerns: {total_concerns}", summary_style))
    elements.append(Paragraph(f"• Resolved: {resolved_concerns}", summary_style))
    elements.append(Paragraph(f"• Processing: {processing_concerns}", summary_style))
    elements.append(Paragraph(f"• Pending: {pending_concerns}", summary_style))
    elements.append(Paragraph(f"• Resolution Rate: {(resolved_concerns/total_concerns*100):.1f}%" if total_concerns > 0 else "• Resolution Rate: 0%", summary_style))
    elements.append(Spacer(1, 20))
    
    # Concerns by type
    type_stats = {}
    for concern in concerns:
        concern_type = concern.concern_type or 'Other'
        if concern_type not in type_stats:
            type_stats[concern_type] = 0
        type_stats[concern_type] += 1
    
    if type_stats:
        elements.append(Paragraph("<b>Concerns by Type:</b>", summary_style))
        for concern_type, count in type_stats.items():
            elements.append(Paragraph(f"• {concern_type.title()}: {count}", summary_style))
        elements.append(Spacer(1, 20))
    
    # Detailed concerns table
    elements.append(Paragraph("<b>Detailed Concern History:</b>", summary_style))
    elements.append(Spacer(1, 10))
    
    # Create table data
    table_data = [['ID', 'Title', 'Type', 'Priority', 'Status', 'Submitted', 'Resolved', 'Days']]
    
    for concern in concerns:
        # Calculate resolution time
        resolution_time = 'N/A'
        if concern.resolved_at and concern.submitted_at:
            days = (concern.resolved_at - concern.submitted_at).days
            resolution_time = str(days)
        
        table_data.append([
            str(concern.id),
            concern.title[:30] + '...' if len(concern.title) > 30 else concern.title,
            concern.concern_type.title() if concern.concern_type else 'N/A',
            concern.priority_level.title() if concern.priority_level else 'N/A',
            concern.status.title() if concern.status else 'N/A',
            concern.submitted_at.strftime('%Y-%m-%d') if concern.submitted_at else 'N/A',
            concern.resolved_at.strftime('%Y-%m-%d') if concern.resolved_at else 'N/A',
            resolution_time
        ])
    
    # Create table
    table = Table(table_data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('BACKGROUND', (0, 1), (-1, -1), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 20))
    
    # Recent concerns with details (last 5)
    if concerns:
        elements.append(Paragraph("<b>Recent Concerns (Last 5):</b>", summary_style))
        elements.append(Spacer(1, 10))
        
        for i, concern in enumerate(concerns[:5]):
            concern_style = ParagraphStyle(
                name='ConcernDetail',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=15,
                leftIndent=20
            )
            
            elements.append(Paragraph(f"<b>Concern #{concern.id}: {concern.title}</b>", concern_style))
            elements.append(Paragraph(f"Type: {concern.concern_type.title() if concern.concern_type else 'N/A'} | Priority: {concern.priority_level.title() if concern.priority_level else 'N/A'} | Status: {concern.status.title() if concern.status else 'N/A'}", concern_style))
            elements.append(Paragraph(f"Submitted: {concern.submitted_at.strftime('%B %d, %Y at %I:%M %p') if concern.submitted_at else 'N/A'}", concern_style))
            if concern.resolved_at:
                elements.append(Paragraph(f"Resolved: {concern.resolved_at.strftime('%B %d, %Y at %I:%M %p')}", concern_style))
            elements.append(Paragraph(f"Description: {concern.description[:150]}{'...' if len(concern.description) > 150 else ''}", concern_style))
            if concern.resolution_notes:
                elements.append(Paragraph(f"Resolution: {concern.resolution_notes[:150]}{'...' if len(concern.resolution_notes) > 150 else ''}", concern_style))
            elements.append(Spacer(1, 10))
    
    # Footer
    footer_style = ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        spaceBefore=30
    )
    elements.append(Paragraph('<font color="#888888">This report was generated from the PiyuKonek Student Concern Management System.</font>', footer_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"concern_history_{student.username}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mimetype='application/pdf'
    )

@app.route('/student/export/concern-details/<int:concern_id>')
@login_required('student')
def student_export_concern_details(concern_id):
    """Export detailed information about a specific concern"""
    student_id = session['user_id']
    student = Student.query.get(student_id)
    
    if not student:
        flash('Student not found.', 'error')
        return redirect(url_for('login'))
    
    # Get the concern and verify it belongs to the student
    concern = Concern.query.get(concern_id)
    if not concern or concern.student_id != student_id:
        flash('Concern not found or access denied.', 'error')
        return redirect(url_for('student_dashboard'))
    
    return export_concern_details_pdf(student, concern)



def export_concern_details_pdf(student, concern):
    """Export detailed concern information as PDF"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=30, rightMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    elements = []
    
    # Header
    logo_path = os.path.join(app.static_folder, 'images', 'logo.png')
    if os.path.exists(logo_path):
        elements.append(Image(logo_path, width=50, height=50))
    
    title_style = ParagraphStyle(
        name='TitleCenter',
        parent=styles['Title'],
        fontSize=16,
        spaceAfter=20,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph(f'Concern Details Report - #{concern.id}', title_style))
    elements.append(Spacer(1, 20))
    
    # Concern details
    detail_style = ParagraphStyle(
        name='Detail',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8
    )
    
    elements.append(Paragraph(f"<b>Title:</b> {concern.title}", detail_style))
    elements.append(Paragraph(f"<b>Type:</b> {concern.concern_type.title() if concern.concern_type else 'N/A'}", detail_style))
    elements.append(Paragraph(f"<b>Priority:</b> {concern.priority_level.title() if concern.priority_level else 'N/A'}", detail_style))
    elements.append(Paragraph(f"<b>Status:</b> {concern.status.title() if concern.status else 'N/A'}", detail_style))
    elements.append(Paragraph(f"<b>Submitted:</b> {concern.submitted_at.strftime('%B %d, %Y at %I:%M %p') if concern.submitted_at else 'N/A'}", detail_style))
    if concern.resolved_at:
        elements.append(Paragraph(f"<b>Resolved:</b> {concern.resolved_at.strftime('%B %d, %Y at %I:%M %p')}", detail_style))
    elements.append(Spacer(1, 15))
    
    # Description
    elements.append(Paragraph("<b>Description:</b>", detail_style))
    elements.append(Paragraph(concern.description, detail_style))
    elements.append(Spacer(1, 15))
    
    # Resolution notes
    if concern.resolution_notes:
        elements.append(Paragraph("<b>Resolution Notes:</b>", detail_style))
        elements.append(Paragraph(concern.resolution_notes, detail_style))
        elements.append(Spacer(1, 15))
    
    # Timeline
    elements.append(Paragraph("<b>Timeline:</b>", detail_style))
    timeline = ConcernHistory.query.filter_by(concern_id=concern.id).order_by(ConcernHistory.timestamp.desc()).all()
    for event in timeline:
        elements.append(Paragraph(f"<b>{event.timestamp.strftime('%B %d, %Y at %I:%M %p')}</b> - {event.status.title()}", detail_style))
        elements.append(Paragraph(f"Action: {event.action}", detail_style))
        elements.append(Spacer(1, 8))
    
    # Messages
    messages = Message.query.filter_by(concern_id=concern.id).order_by(Message.timestamp.asc()).all()
    if messages:
        elements.append(Paragraph("<b>Messages:</b>", detail_style))
        for message in messages:
            sender_name = "You" if message.sender_id == student.id else "Staff"
            elements.append(Paragraph(f"<b>{message.timestamp.strftime('%B %d, %Y at %I:%M %p')} - {sender_name}</b>", detail_style))
            elements.append(Paragraph(message.content, detail_style))
            if message.attachment_name:
                elements.append(Paragraph(f"Attachment: {message.attachment_name}", detail_style))
            elements.append(Spacer(1, 8))
    
    # Attachments
    attachments = ConcernAttachment.query.filter_by(concern_id=concern.id).all()
    if attachments:
        elements.append(Paragraph("<b>Attachments:</b>", detail_style))
        for attachment in attachments:
            elements.append(Paragraph(f"• {attachment.original_filename} ({attachment.file_size} bytes)", detail_style))
    
    # Footer
    footer_style = ParagraphStyle(
        name='Footer',
        parent=styles['Normal'],
        fontSize=8,
        alignment=TA_CENTER,
        spaceBefore=30
    )
    elements.append(Paragraph('<font color="#888888">Generated from PiyuKonek Student Concern Management System</font>', footer_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"concern_details_{concern.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    # NEVER use debug=True in production - set FLASK_DEBUG=false and FLASK_ENV=production
    debug_mode = os.environ.get('FLASK_DEBUG', 'true').lower() == 'true'
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
    
