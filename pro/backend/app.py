from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from datetime import datetime, timedelta, date
from sqlalchemy import func, or_, and_
import os
import random

app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///skillconnect_india.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=7)

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
jwt = JWTManager(app)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# ==================== DATABASE MODELS ====================

class User(db.Model):
    """Enhanced User model with comprehensive fields"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    password_hash = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(20), nullable=False, index=True)
    profile_image = db.Column(db.String(255))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    address = db.Column(db.String(255))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_verified = db.Column(db.Boolean, default=False)
    is_premium = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    phone_verified = db.Column(db.Boolean, default=False)
    last_login = db.Column(db.DateTime)
    last_seen = db.Column(db.DateTime)
    login_count = db.Column(db.Integer, default=0)
    profile_views = db.Column(db.Integer, default=0)
    preferred_language = db.Column(db.String(20), default='en')
    timezone = db.Column(db.String(50))
    notification_preferences = db.Column(db.Text)
    bio = db.Column(db.Text)
    social_linkedin = db.Column(db.String(255))
    social_twitter = db.Column(db.String(255))
    social_facebook = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = db.Column(db.DateTime)
    
    # Relationships
    worker_profile = db.relationship('WorkerProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    employer_profile = db.relationship('EmployerProfile', back_populates='user', uselist=False, cascade='all, delete-orphan')
    jobs_posted = db.relationship('Job', back_populates='employer', foreign_keys='Job.employer_id', cascade='all, delete-orphan')
    applications = db.relationship('Application', back_populates='applicant', cascade='all, delete-orphan')
    reviews_given = db.relationship('Review', foreign_keys='Review.reviewer_id', back_populates='reviewer', cascade='all, delete-orphan')
    reviews_received = db.relationship('Review', foreign_keys='Review.reviewee_id', back_populates='reviewee', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    saved_jobs = db.relationship('SavedJob', back_populates='user', cascade='all, delete-orphan')
    job_alerts = db.relationship('JobAlert', back_populates='user', cascade='all, delete-orphan')
    payments_made = db.relationship('Payment', foreign_keys='Payment.payer_id', back_populates='payer', cascade='all, delete-orphan')
    payments_received = db.relationship('Payment', foreign_keys='Payment.payee_id', back_populates='payee', cascade='all, delete-orphan')
    disputes_filed = db.relationship('Dispute', foreign_keys='Dispute.filed_by_id', back_populates='filed_by', cascade='all, delete-orphan')
    disputes_against = db.relationship('Dispute', foreign_keys='Dispute.filed_against_id', back_populates='filed_against', cascade='all, delete-orphan')
    activities = db.relationship('UserActivity', back_populates='user', cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'phone': self.phone,
            'user_type': self.user_type,
            'profile_image': self.profile_image,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'is_premium': self.is_premium,
            'bio': self.bio,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class EmployerProfile(db.Model):
    """Detailed employer/company profile"""
    __tablename__ = 'employer_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    company_name = db.Column(db.String(200), nullable=False)
    company_registration_number = db.Column(db.String(100))
    company_size = db.Column(db.String(50))
    industry = db.Column(db.String(100))
    founded_year = db.Column(db.Integer)
    website = db.Column(db.String(255))
    location = db.Column(db.String(100))
    headquarters = db.Column(db.String(200))
    description = db.Column(db.Text)
    mission_statement = db.Column(db.Text)
    logo = db.Column(db.String(255))
    cover_image = db.Column(db.String(255))
    rating = db.Column(db.Float, default=0.0)
    total_hires = db.Column(db.Integer, default=0)
    total_jobs_posted = db.Column(db.Integer, default=0)
    active_jobs_count = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Float, default=0.0)
    average_rating = db.Column(db.Float, default=0.0)
    response_time = db.Column(db.Integer)
    response_rate = db.Column(db.Float, default=0.0)
    verified_company = db.Column(db.Boolean, default=False)
    featured = db.Column(db.Boolean, default=False)
    benefits_offered = db.Column(db.Text)
    company_culture = db.Column(db.Text)
    social_responsibility = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', back_populates='worker_profile')
    certifications = db.relationship('Certification', back_populates='worker', cascade='all, delete-orphan')
    work_history = db.relationship('WorkHistory', back_populates='worker', cascade='all, delete-orphan')
    education = db.relationship('Education', back_populates='worker', cascade='all, delete-orphan')
    portfolio_items = db.relationship('PortfolioItem', back_populates='worker', cascade='all, delete-orphan')
    skills_endorsements = db.relationship('SkillEndorsement', back_populates='worker', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.user.name,
            'email': self.user.email,
            'phone': self.user.phone,
            'title': self.title,
            'professional_headline': self.professional_headline,
            'skills': self.skills,
            'experience_years': self.experience_years,
            'experience_level': self.experience_level,
            'hourly_rate': f'₹{self.hourly_rate}',
            'hourly_rate_value': self.hourly_rate,
            'location': self.location,
            'bio': self.bio,
            'availability': self.availability,
            'work_preference': self.work_preference,
            'rating': self.rating,
            'jobs_completed': self.jobs_completed,
            'total_earnings': self.total_earnings,
            'response_rate': self.response_rate,
            'on_time_delivery': self.on_time_delivery,
            'verified': self.verified,
            'top_rated': self.top_rated,
            'avatar': ''.join([word[0].upper() for word in self.user.name.split()[:2]])
        }

class Certification(db.Model):
    """Professional certifications and licenses"""
    __tablename__ = 'certifications'
    
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker_profiles.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    issuing_organization = db.Column(db.String(200))
    credential_id = db.Column(db.String(100))
    credential_url = db.Column(db.String(255))
    issue_date = db.Column(db.Date)
    expiry_date = db.Column(db.Date)
    does_not_expire = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    certificate_file = db.Column(db.String(255))
    verified = db.Column(db.Boolean, default=False)
    verification_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    worker = db.relationship('WorkerProfile', back_populates='certifications')

class Education(db.Model):
    """Educational background"""
    __tablename__ = 'education'
    
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker_profiles.id'), nullable=False)
    institution_name = db.Column(db.String(200), nullable=False)
    degree = db.Column(db.String(100))
    field_of_study = db.Column(db.String(100))
    grade = db.Column(db.String(50))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_current = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    activities = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    worker = db.relationship('WorkerProfile', back_populates='education')

class WorkHistory(db.Model):
    """Work experience history"""
    __tablename__ = 'work_history'
    
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker_profiles.id'), nullable=False)
    job_title = db.Column(db.String(200), nullable=False)
    company = db.Column(db.String(200))
    employment_type = db.Column(db.String(50))
    location = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    is_current = db.Column(db.Boolean, default=False)
    description = db.Column(db.Text)
    achievements = db.Column(db.Text)
    skills_used = db.Column(db.String(500))
    reference_name = db.Column(db.String(100))
    reference_contact = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    worker = db.relationship('WorkerProfile', back_populates='work_history')

class PortfolioItem(db.Model):
    """Worker portfolio/past work showcase"""
    __tablename__ = 'portfolio_items'
    
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker_profiles.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    project_url = db.Column(db.String(255))
    image_urls = db.Column(db.Text)
    video_url = db.Column(db.String(255))
    project_date = db.Column(db.Date)
    skills_demonstrated = db.Column(db.String(500))
    client_name = db.Column(db.String(100))
    project_duration = db.Column(db.String(50))
    budget_range = db.Column(db.String(50))
    featured = db.Column(db.Boolean, default=False)
    views_count = db.Column(db.Integer, default=0)
    likes_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    worker = db.relationship('WorkerProfile', back_populates='portfolio_items')

class SkillEndorsement(db.Model):
    """Skill endorsements from other users"""
    __tablename__ = 'skill_endorsements'
    
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker_profiles.id'), nullable=False)
    endorser_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    skill_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    worker = db.relationship('WorkerProfile', back_populates='skills_endorsements')
    endorser = db.relationship('User')

class Job(db.Model):
    """Comprehensive job posting model"""
    __tablename__ = 'jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    employer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False, index=True)
    company = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False, index=True)
    sub_category = db.Column(db.String(50))
    job_type = db.Column(db.String(20), nullable=False, index=True)
    work_mode = db.Column(db.String(20))
    location = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    salary_range = db.Column(db.String(100), nullable=False)
    salary_min = db.Column(db.Float)
    salary_max = db.Column(db.Float)
    salary_currency = db.Column(db.String(10), default='INR')
    salary_period = db.Column(db.String(20))
    description = db.Column(db.Text, nullable=False)
    responsibilities = db.Column(db.Text)
    requirements = db.Column(db.Text)
    qualifications = db.Column(db.Text)
    skills_required = db.Column(db.Text, nullable=False)
    experience_required = db.Column(db.Integer)
    experience_level = db.Column(db.String(50))
    education_required = db.Column(db.String(100))
    certifications_required = db.Column(db.Text)
    benefits = db.Column(db.Text)
    perks = db.Column(db.Text)
    work_schedule = db.Column(db.String(200))
    number_of_positions = db.Column(db.Integer, default=1)
    urgent = db.Column(db.Boolean, default=False, index=True)
    featured = db.Column(db.Boolean, default=False, index=True)
    remote_ok = db.Column(db.Boolean, default=False)
    relocation_assistance = db.Column(db.Boolean, default=False)
    visa_sponsorship = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='active', index=True)
    priority = db.Column(db.Integer, default=0)
    views_count = db.Column(db.Integer, default=0)
    applications_count = db.Column(db.Integer, default=0)
    saved_count = db.Column(db.Integer, default=0)
    posted_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    filled_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    employer = db.relationship('User', back_populates='jobs_posted')
    applications = db.relationship('Application', back_populates='job', cascade='all, delete-orphan')
    saved_by = db.relationship('SavedJob', back_populates='job', cascade='all, delete-orphan')
    reviews = db.relationship('Review', back_populates='job', cascade='all, delete-orphan')
    milestones = db.relationship('JobMilestone', back_populates='job', cascade='all, delete-orphan')
    questions = db.relationship('JobQuestion', back_populates='job', cascade='all, delete-orphan')
    
    def to_dict(self):
        icons = {
            'electrical': '⚡',
            'plumbing': '🔧',
            'construction': '🏗️',
            'carpentry': '🪚',
            'painting': '🎨',
            'welding': '🔥',
            'hvac': '❄️',
            'landscaping': '🌳',
            'roofing': '🏠',
            'masonry': '🧱'
        }
        return {
            'id': self.id,
            'employer_id': self.employer_id,
            'employer_name': self.employer.name,
            'employer_phone': self.employer.phone,
            'employer_email': self.employer.email,
            'title': self.title,
            'company': self.company,
            'category': self.category,
            'job_type': self.job_type,
            'work_mode': self.work_mode,
            'location': self.location,
            'type': self.job_type,
            'salary': self.salary_range,
            'salary_min': self.salary_min,
            'salary_max': self.salary_max,
            'description': self.description,
            'responsibilities': self.responsibilities,
            'requirements': self.requirements,
            'skills': self.skills_required,
            'experience_required': self.experience_required,
            'benefits': self.benefits,
            'urgent': self.urgent,
            'featured': self.featured,
            'remote_ok': self.remote_ok,
            'status': self.status,
            'views_count': self.views_count,
            'applications_count': self.applications_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'icon': icons.get(self.category.lower(), '💼')
        }

class JobMilestone(db.Model):
    __tablename__ = 'job_milestones'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False)
    due_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')
    order_index = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    job = db.relationship('Job', back_populates='milestones')

class JobQuestion(db.Model):
    __tablename__ = 'job_questions'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    question_type = db.Column(db.String(50))
    required = db.Column(db.Boolean, default=True)
    order_index = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    job = db.relationship('Job', back_populates='questions')
    answers = db.relationship('ApplicationAnswer', back_populates='question', cascade='all, delete-orphan')

class SavedJob(db.Model):
    __tablename__ = 'saved_jobs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', back_populates='saved_jobs')
    job = db.relationship('Job', back_populates='saved_by')

class Application(db.Model):
    __tablename__ = 'applications'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    status = db.Column(db.String(20), default='pending', index=True)
    application_stage = db.Column(db.String(50))
    cover_letter = db.Column(db.Text)
    resume_url = db.Column(db.String(255))
    portfolio_url = db.Column(db.String(255))
    expected_salary = db.Column(db.Float)
    available_from = db.Column(db.Date)
    notice_period = db.Column(db.String(50))
    years_of_experience = db.Column(db.Integer)
    custom_responses = db.Column(db.Text)
    viewed_by_employer = db.Column(db.Boolean, default=False)
    employer_rating = db.Column(db.Integer)
    employer_notes = db.Column(db.Text)
    interview_scheduled_at = db.Column(db.DateTime)
    interview_location = db.Column(db.String(255))
    interview_type = db.Column(db.String(50))
    interview_notes = db.Column(db.Text)
    rejection_reason = db.Column(db.Text)
    feedback = db.Column(db.Text)
    application_score = db.Column(db.Float)
    applied_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    viewed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    applicant = db.relationship('User', back_populates='applications')
    job = db.relationship('Job', back_populates='applications')
    answers = db.relationship('ApplicationAnswer', back_populates='application', cascade='all, delete-orphan')
    status_history = db.relationship('ApplicationStatusHistory', back_populates='application', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'job_id': self.job_id,
            'job_title': self.job.title,
            'company': self.job.company,
            'user_id': self.user_id,
            'applicant_name': self.applicant.name,
            'status': self.status,
            'cover_letter': self.cover_letter,
            'expected_salary': self.expected_salary,
            'available_from': self.available_from.isoformat() if self.available_from else None,
            'viewed_by_employer': self.viewed_by_employer,
            'applied_at': self.applied_at.isoformat()
        }

class ApplicationAnswer(db.Model):
    __tablename__ = 'application_answers'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    question_id = db.Column(db.Integer, db.ForeignKey('job_questions.id'), nullable=False)
    answer = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    application = db.relationship('Application', back_populates='answers')
    question = db.relationship('JobQuestion', back_populates='answers')

class ApplicationStatusHistory(db.Model):
    __tablename__ = 'application_status_history'
    
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('applications.id'), nullable=False)
    from_status = db.Column(db.String(20))
    to_status = db.Column(db.String(20), nullable=False)
    changed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    application = db.relationship('Application', back_populates='status_history')
    changed_by = db.relationship('User')

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'))
    rating = db.Column(db.Float, nullable=False)
    title = db.Column(db.String(200))
    comment = db.Column(db.Text)
    work_quality = db.Column(db.Float)
    communication = db.Column(db.Float)
    professionalism = db.Column(db.Float)
    punctuality = db.Column(db.Float)
    expertise = db.Column(db.Float)
    value_for_money = db.Column(db.Float)
    would_recommend = db.Column(db.Boolean, default=True)
    would_hire_again = db.Column(db.Boolean)
    helpful_count = db.Column(db.Integer, default=0)
    not_helpful_count = db.Column(db.Integer, default=0)
    reported = db.Column(db.Boolean, default=False)
    verified_hire = db.Column(db.Boolean, default=False)
    response = db.Column(db.Text)
    response_date = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], back_populates='reviews_given')
    reviewee = db.relationship('User', foreign_keys=[reviewee_id], back_populates='reviews_received')
    job = db.relationship('Job', back_populates='reviews')

class CompanyReview(db.Model):
    __tablename__ = 'company_reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('employer_profiles.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Float, nullable=False)
    title = db.Column(db.String(200))
    pros = db.Column(db.Text)
    cons = db.Column(db.Text)
    advice_to_management = db.Column(db.Text)
    work_life_balance = db.Column(db.Float)
    compensation_benefits = db.Column(db.Float)
    job_security = db.Column(db.Float)
    management = db.Column(db.Float)
    culture = db.Column(db.Float)
    employment_status = db.Column(db.String(50))
    job_title = db.Column(db.String(100))
    years_worked = db.Column(db.Integer)
    recommends = db.Column(db.Boolean)
    helpful_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    company = db.relationship('EmployerProfile', back_populates='company_reviews')
    reviewer = db.relationship('User')

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    type = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    link = db.Column(db.String(255))
    icon = db.Column(db.String(50))
    priority = db.Column(db.String(20), default='normal')
    category = db.Column(db.String(50))
    is_read = db.Column(db.Boolean, default=False, index=True)
    read_at = db.Column(db.DateTime)
    is_archived = db.Column(db.Boolean, default=False)
    action_required = db.Column(db.Boolean, default=False)
    action_url = db.Column(db.String(255))
    action_label = db.Column(db.String(100))
    expires_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', back_populates='notifications')

class JobAlert(db.Model):
    __tablename__ = 'job_alerts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(100))
    keywords = db.Column(db.String(500))
    category = db.Column(db.String(50))
    location = db.Column(db.String(100))
    job_type = db.Column(db.String(20))
    min_salary = db.Column(db.Float)
    max_salary = db.Column(db.Float)
    remote_only = db.Column(db.Boolean, default=False)
    frequency = db.Column(db.String(20), default='daily')
    is_active = db.Column(db.Boolean, default=True)
    last_sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', back_populates='job_alerts')

class Payment(db.Model):
    __tablename__ = 'payments'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    payer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    payee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), default='INR')
    payment_method = db.Column(db.String(50))
    payment_provider = db.Column(db.String(50))
    transaction_id = db.Column(db.String(100), unique=True)
    invoice_number = db.Column(db.String(100))
    description = db.Column(db.Text)
    fee = db.Column(db.Float, default=0.0)
    net_amount = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending', index=True)
    status_message = db.Column(db.String(255))
    milestone_id = db.Column(db.Integer, db.ForeignKey('job_milestones.id'))
    refund_amount = db.Column(db.Float)
    refund_reason = db.Column(db.Text)
    refunded_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    completed_at = db.Column(db.DateTime)
    
    job = db.relationship('Job')
    payer = db.relationship('User', foreign_keys=[payer_id], back_populates='payments_made')
    payee = db.relationship('User', foreign_keys=[payee_id], back_populates='payments_received')
    milestone = db.relationship('JobMilestone')

class Dispute(db.Model):
    __tablename__ = 'disputes'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    filed_by_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filed_against_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    evidence_urls = db.Column(db.Text)
    status = db.Column(db.String(20), default='open', index=True)
    resolution = db.Column(db.Text)
    resolution_date = db.Column(db.DateTime)
    resolved_by_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    priority = db.Column(db.String(20), default='normal')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    job = db.relationship('Job')
    filed_by = db.relationship('User', foreign_keys=[filed_by_id], back_populates='disputes_filed')
    filed_against = db.relationship('User', foreign_keys=[filed_against_id], back_populates='disputes_against')
    resolved_by = db.relationship('User', foreign_keys=[resolved_by_id])

class UserActivity(db.Model):
    __tablename__ = 'user_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    activity_type = db.Column(db.String(50), nullable=False, index=True)
    description = db.Column(db.String(255))
    activity_metadata = db.Column(db.Text)
    ip_address = db.Column(db.String(50))
    user_agent = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    user = db.relationship('User', back_populates='activities')

class Contract(db.Model):
    __tablename__ = 'contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('jobs.id'), nullable=False)
    employer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contract_type = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    terms = db.Column(db.Text, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='draft', index=True)
    employer_signed = db.Column(db.Boolean, default=False)
    worker_signed = db.Column(db.Boolean, default=False)
    employer_signed_at = db.Column(db.DateTime)
    worker_signed_at = db.Column(db.DateTime)
    document_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    job = db.relationship('Job')
    employer = db.relationship('User', foreign_keys=[employer_id])
    worker = db.relationship('User', foreign_keys=[worker_id])

# ==================== API ROUTES ====================

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        required_fields = ['name', 'email', 'password', 'user_type']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email already registered'}), 400
        
        user = User(
            name=data['name'],
            email=data['email'],
            user_type=data['user_type'],
            phone=data.get('phone'),
            city=data.get('city'),
            state=data.get('state'),
            country='India'
        )
        user.set_password(data['password'])
        
        db.session.add(user)
        db.session.commit()
        
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'message': 'Registration successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Registration error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or 'email' not in data or 'password' not in data:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        user.last_login = datetime.utcnow()
        user.login_count += 1
        db.session.commit()
        
        access_token = create_access_token(identity=user.id)
        return jsonify({
            'message': 'Login successful',
            'access_token': access_token,
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        print(f"Login error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def get_stats():
    try:
        stats = {
            'active_jobs': Job.query.filter_by(status='active').count(),
            'total_workers': WorkerProfile.query.count(),
            'total_employers': User.query.filter_by(user_type='employer').count(),
            'total_applications': Application.query.count(),
            'total_users': User.query.count(),
            'featured_jobs': Job.query.filter_by(featured=True, status='active').count(),
            'urgent_jobs': Job.query.filter_by(urgent=True, status='active').count(),
            'total_reviews': Review.query.count()
        }
        return jsonify({'stats': stats}), 200
    except Exception as e:
        print(f"Stats error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/jobs', methods=['GET', 'POST'])
def jobs():
    if request.method == 'GET':
        try:
            query = Job.query.filter_by(status='active')
            
            job_type = request.args.get('type')
            category = request.args.get('category')
            keyword = request.args.get('keyword')
            location = request.args.get('location')
            remote = request.args.get('remote')
            min_salary = request.args.get('min_salary')
            max_salary = request.args.get('max_salary')
            
            if job_type:
                query = query.filter_by(job_type=job_type)
            if category:
                query = query.filter_by(category=category)
            if keyword:
                query = query.filter(or_(
                    Job.title.contains(keyword),
                    Job.description.contains(keyword),
                    Job.skills_required.contains(keyword)
                ))
            if location:
                query = query.filter(Job.location.contains(location))
            if remote == 'true':
                query = query.filter_by(remote_ok=True)
            if min_salary:
                query = query.filter(Job.salary_min >= float(min_salary))
            if max_salary:
                query = query.filter(Job.salary_max <= float(max_salary))
            
            sort_by = request.args.get('sort', 'created_at')
            if sort_by == 'salary':
                query = query.order_by(Job.salary_max.desc())
            elif sort_by == 'applications':
                query = query.order_by(Job.applications_count.desc())
            else:
                query = query.order_by(Job.created_at.desc())
            
            page = int(request.args.get('page', 1))
            per_page = int(request.args.get('per_page', 20))
            pagination = query.paginate(page=page, per_page=per_page, error_out=False)
            
            return jsonify({
                'jobs': [job.to_dict() for job in pagination.items],
                'total': pagination.total,
                'pages': pagination.pages,
                'current_page': page
            }), 200
            
        except Exception as e:
            print(f"Get jobs error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            current_user_id = get_jwt_identity()
            data = request.get_json()
            
            required_fields = ['title', 'company', 'category', 'location', 'job_type', 'salary_range', 'description', 'skills_required']
            if not all(field in data for field in required_fields):
                return jsonify({'error': 'Missing required fields'}), 400
            
            expires_at = datetime.utcnow() + timedelta(days=30)
            
            job = Job(
                employer_id=current_user_id,
                title=data['title'],
                company=data['company'],
                category=data['category'],
                location=data['location'],
                job_type=data['job_type'],
                salary_range=data['salary_range'],
                description=data['description'],
                skills_required=data['skills_required'],
                urgent=data.get('urgent', False),
                featured=data.get('featured', False),
                remote_ok=data.get('remote_ok', False),
                work_mode=data.get('work_mode', 'on-site'),
                experience_required=data.get('experience_required'),
                education_required=data.get('education_required'),
                benefits=data.get('benefits'),
                responsibilities=data.get('responsibilities'),
                requirements=data.get('requirements'),
                expires_at=expires_at,
                country='India'
            )
            
            db.session.add(job)
            db.session.commit()
            
            return jsonify({'message': 'Job posted successfully', 'job': job.to_dict()}), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"Post job error: {str(e)}")
            return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<int:job_id>', methods=['GET', 'PUT', 'DELETE'])
def job_detail(job_id):
    job = Job.query.get_or_404(job_id)
    
    if request.method == 'GET':
        try:
            job.views_count += 1
            db.session.commit()
            return jsonify({'job': job.to_dict()}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            current_user_id = get_jwt_identity()
            if job.employer_id != current_user_id:
                return jsonify({'error': 'Unauthorized'}), 403
            
            data = request.get_json()
            for key, value in data.items():
                if hasattr(job, key):
                    setattr(job, key, value)
            
            db.session.commit()
            return jsonify({'message': 'Job updated', 'job': job.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'DELETE':
        try:
            current_user_id = get_jwt_identity()
            if job.employer_id != current_user_id:
                return jsonify({'error': 'Unauthorized'}), 403
            
            job.status = 'closed'
            db.session.commit()
            return jsonify({'message': 'Job closed'}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

@app.route('/api/jobs/<int:job_id>/apply', methods=['POST'])
@jwt_required()
def apply_job(job_id):
    try:
        current_user_id = get_jwt_identity()
        
        job = Job.query.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        if job.status != 'active':
            return jsonify({'error': 'Job is no longer accepting applications'}), 400
        
        existing = Application.query.filter_by(job_id=job_id, user_id=current_user_id).first()
        if existing:
            return jsonify({'error': 'Already applied to this job'}), 400
        
        data = request.get_json() or {}
        
        application = Application(
            job_id=job_id,
            user_id=current_user_id,
            cover_letter=data.get('cover_letter'),
            expected_salary=data.get('expected_salary'),
            available_from=data.get('available_from')
        )
        
        job.applications_count += 1
        
        db.session.add(application)
        db.session.commit()
        
        notification = Notification(
            user_id=job.employer_id,
            type='new_application',
            title='New Job Application',
            content=f'Someone applied for {job.title}',
            link=f'/applications/{application.id}'
        )
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({'message': 'Application submitted successfully'}), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Apply job error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/workers', methods=['GET'])
def get_workers():
    try:
        query = WorkerProfile.query
        
        category = request.args.get('category')
        location = request.args.get('location')
        min_rate = request.args.get('min_rate')
        max_rate = request.args.get('max_rate')
        min_experience = request.args.get('min_experience')
        verified_only = request.args.get('verified')
        top_rated = request.args.get('top_rated')
        skills = request.args.get('skills')
        user_id = request.args.get('user_id')
        
        if user_id:
            query = query.filter_by(user_id=int(user_id))
        if category:
            query = query.filter_by(primary_category=category)
        if location:
            query = query.filter(WorkerProfile.location.contains(location))
        if min_rate:
            query = query.filter(WorkerProfile.hourly_rate >= float(min_rate))
        if max_rate:
            query = query.filter(WorkerProfile.hourly_rate <= float(max_rate))
        if min_experience:
            query = query.filter(WorkerProfile.experience_years >= int(min_experience))
        if verified_only == 'true':
            query = query.filter_by(verified=True)
        if top_rated == 'true':
            query = query.filter_by(top_rated=True)
        if skills:
            query = query.filter(WorkerProfile.skills.contains(skills))
        
        sort_by = request.args.get('sort', 'rating')
        if sort_by == 'rating':
            query = query.order_by(WorkerProfile.rating.desc())
        elif sort_by == 'experience':
            query = query.order_by(WorkerProfile.experience_years.desc())
        elif sort_by == 'rate_low':
            query = query.order_by(WorkerProfile.hourly_rate.asc())
        elif sort_by == 'rate_high':
            query = query.order_by(WorkerProfile.hourly_rate.desc())
        
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return jsonify({
            'workers': [worker.to_dict() for worker in pagination.items],
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        print(f"Get workers error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/workers/profile', methods=['GET', 'POST', 'PUT'])
@jwt_required()
def worker_profile():
    current_user_id = get_jwt_identity()
    
    if request.method == 'GET':
        try:
            profile = WorkerProfile.query.filter_by(user_id=current_user_id).first()
            if not profile:
                return jsonify({'error': 'Profile not found'}), 404
            return jsonify({'profile': profile.to_dict()}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'POST':
        try:
            existing = WorkerProfile.query.filter_by(user_id=current_user_id).first()
            if existing:
                return jsonify({'error': 'Profile already exists'}), 400
            
            data = request.get_json()
            required_fields = ['title', 'skills', 'experience_years', 'hourly_rate', 'location', 'bio']
            if not all(field in data for field in required_fields):
                return jsonify({'error': 'Missing required fields'}), 400
            
            profile = WorkerProfile(
                user_id=current_user_id,
                title=data['title'],
                skills=data['skills'],
                experience_years=data['experience_years'],
                hourly_rate=data['hourly_rate'],
                location=data['location'],
                bio=data['bio'],
                primary_category=data.get('category'),
                work_preference=data.get('work_preference', 'on-site'),
                availability=data.get('availability', 'available')
            )
            
            db.session.add(profile)
            db.session.commit()
            
            return jsonify({'message': 'Profile created successfully', 'profile': profile.to_dict()}), 201
            
        except Exception as e:
            db.session.rollback()
            print(f"Create profile error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            profile = WorkerProfile.query.filter_by(user_id=current_user_id).first()
            if not profile:
                return jsonify({'error': 'Profile not found'}), 404
            
            data = request.get_json()
            for key, value in data.items():
                if hasattr(profile, key):
                    setattr(profile, key, value)
            
            db.session.commit()
            return jsonify({'message': 'Profile updated', 'profile': profile.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

@app.route('/api/applications', methods=['GET'])
@jwt_required()
def get_applications():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if user.user_type == 'worker':
            applications = Application.query.filter_by(user_id=current_user_id).all()
        else:
            job_ids = [job.id for job in Job.query.filter_by(employer_id=current_user_id).all()]
            applications = Application.query.filter(Application.job_id.in_(job_ids)).all()
        
        return jsonify({'applications': [app.to_dict() for app in applications]}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/applications/<int:app_id>', methods=['GET', 'PUT'])
@jwt_required()
def application_detail(app_id):
    application = Application.query.get_or_404(app_id)
    current_user_id = get_jwt_identity()
    
    if request.method == 'GET':
        try:
            if application.user_id != current_user_id and application.job.employer_id != current_user_id:
                return jsonify({'error': 'Unauthorized'}), 403
            
            if application.job.employer_id == current_user_id and not application.viewed_by_employer:
                application.viewed_by_employer = True
                application.viewed_at = datetime.utcnow()
                db.session.commit()
            
            return jsonify({'application': application.to_dict()}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    elif request.method == 'PUT':
        try:
            if application.job.employer_id != current_user_id:
                return jsonify({'error': 'Unauthorized'}), 403
            
            data = request.get_json()
            old_status = application.status
            
            if 'status' in data:
                application.status = data['status']
                
                history = ApplicationStatusHistory(
                    application_id=app_id,
                    from_status=old_status,
                    to_status=data['status'],
                    changed_by_id=current_user_id,
                    notes=data.get('notes')
                )
                db.session.add(history)
                
                notification = Notification(
                    user_id=application.user_id,
                    type='application_status',
                    title='Application Status Updated',
                    content=f'Your application status changed to {data["status"]}',
                    link=f'/applications/{app_id}'
                )
                db.session.add(notification)
            
            if 'employer_notes' in data:
                application.employer_notes = data['employer_notes']
            
            db.session.commit()
            return jsonify({'message': 'Application updated', 'application': application.to_dict()}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 500

@app.route('/api/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    try:
        current_user_id = get_jwt_identity()
        
        unread_only = request.args.get('unread', 'false').lower() == 'true'
        
        query = Notification.query.filter_by(user_id=current_user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        
        notifications = query.order_by(Notification.created_at.desc()).limit(50).all()
        
        return jsonify({
            'notifications': [{'id': n.id, 'type': n.type, 'title': n.title, 'content': n.content, 'is_read': n.is_read, 'created_at': n.created_at.isoformat()} for n in notifications],
            'unread_count': Notification.query.filter_by(user_id=current_user_id, is_read=False).count()
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/notifications/<int:notif_id>/read', methods=['PUT'])
@jwt_required()
def mark_notification_read(notif_id):
    try:
        current_user_id = get_jwt_identity()
        notification = Notification.query.get_or_404(notif_id)
        
        if notification.user_id != current_user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({'message': 'Notification marked as read'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'ok',
        'message': 'SkillConnect India Backend API is running',
        'timestamp': datetime.utcnow().isoformat()
    }), 200

# ==================== SEED DATA WITH INDIAN NAMES & LOCATIONS ====================

def seed_indian_data():
    """Seed database with Indian sample data"""
    
    if User.query.count() > 0:
        print("Database already has data. Skipping seed.")
        return
    
    print("\n" + "="*50)
    print("Seeding database with Indian data...")
    print("="*50)
    
    indian_cities = [
        {'city': 'Mumbai', 'state': 'Maharashtra'},
        {'city': 'Delhi', 'state': 'Delhi'},
        {'city': 'Bengaluru', 'state': 'Karnataka'},
        {'city': 'Hyderabad', 'state': 'Telangana'},
        {'city': 'Pune', 'state': 'Maharashtra'},
        {'city': 'Chennai', 'state': 'Tamil Nadu'},
        {'city': 'Kolkata', 'state': 'West Bengal'},
        {'city': 'Ahmedabad', 'state': 'Gujarat'},
    ]
    
    employers_data = [
        {'name': 'BuildTech India Pvt Ltd', 'email': 'hr@buildtech.in', 'company': 'BuildTech India', 'industry': 'Construction', 'size': '201-500'},
        {'name': 'PowerGrid Electricals', 'email': 'jobs@powergrid.in', 'company': 'PowerGrid Electricals', 'industry': 'Electrical Services', 'size': '51-200'},
        {'name': 'Sharma Plumbing Solutions', 'email': 'careers@sharmaplumb.in', 'company': 'Sharma Plumbing', 'industry': 'Plumbing', 'size': '11-50'},
        {'name': 'Patel Carpentry Works', 'email': 'info@patelcarpentry.in', 'company': 'Patel Carpentry', 'industry': 'Carpentry', 'size': '11-50'},
        {'name': 'Modern Painters India', 'email': 'contact@modernpainters.in', 'company': 'Modern Painters', 'industry': 'Painting', 'size': '11-50'},
    ]
    
    employers = []
    for emp_data in employers_data:
        location = random.choice(indian_cities)
        user = User(
            name=emp_data['name'],
            email=emp_data['email'],
            user_type='employer',
            phone=f'+91-{random.randint(7000000000, 9999999999)}',
            city=location['city'],
            state=location['state'],
            country='India',
            is_verified=True,
            bio=f'Leading {emp_data["industry"]} company in India'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.flush()
        
        profile = EmployerProfile(
            user_id=user.id,
            company_name=emp_data['company'],
            industry=emp_data['industry'],
            company_size=emp_data['size'],
            founded_year=random.randint(1990, 2020),
            website=f'https://www.{emp_data["company"].lower().replace(" ", "")}.in',
            location=f'{location["city"]}, {location["state"]}',
            description=f'We are a trusted {emp_data["industry"]} company serving clients across India.',
            rating=round(random.uniform(4.0, 5.0), 1),
            verified_company=True,
            total_hires=random.randint(10, 100),
            response_rate=round(random.uniform(85, 100), 1)
        )
        db.session.add(profile)
        employers.append(user)
    
    db.session.commit()
    print(f"Created {len(employers)} employer accounts")
    
    workers_data = [
        {'name': 'Rajesh Kumar', 'email': 'rajesh.kumar@email.com', 'title': 'Master Electrician', 'category': 'electrical', 'skills': 'Electrical Wiring, Circuit Design, Safety Compliance, Troubleshooting', 'exp': 12, 'rate': 500},
        {'name': 'Priya Sharma', 'email': 'priya.sharma@email.com', 'title': 'Senior Construction Foreman', 'category': 'construction', 'skills': 'Project Management, Team Leadership, Blueprint Reading, Safety', 'exp': 15, 'rate': 600},
        {'name': 'Amit Patel', 'email': 'amit.patel@email.com', 'title': 'Licensed Plumber', 'category': 'plumbing', 'skills': 'Pipe Installation, Drain Cleaning, Water Heaters, Gas Lines', 'exp': 8, 'rate': 450},
        {'name': 'Sunita Singh', 'email': 'sunita.singh@email.com', 'title': 'Expert Carpenter', 'category': 'carpentry', 'skills': 'Fine Woodworking, Custom Cabinets, Framing, Finishing', 'exp': 10, 'rate': 550},
        {'name': 'Mohammed Khan', 'email': 'mohammed.khan@email.com', 'title': 'Professional Painter', 'category': 'painting', 'skills': 'Interior/Exterior Painting, Drywall Repair, Color Consulting', 'exp': 7, 'rate': 400},
        {'name': 'Lakshmi Reddy', 'email': 'lakshmi.reddy@email.com', 'title': 'Certified Welder', 'category': 'welding', 'skills': 'Arc Welding, TIG Welding, Metal Fabrication', 'exp': 9, 'rate': 480},
        {'name': 'Vijay Desai', 'email': 'vijay.desai@email.com', 'title': 'HVAC Technician', 'category': 'hvac', 'skills': 'AC Installation, Repair, Maintenance, Refrigeration', 'exp': 6, 'rate': 420},
        {'name': 'Anita Verma', 'email': 'anita.verma@email.com', 'title': 'Mason Expert', 'category': 'masonry', 'skills': 'Bricklaying, Stone Work, Concrete Work, Plastering', 'exp': 11, 'rate': 380},
    ]
    
    workers = []
    for worker_data in workers_data:
        location = random.choice(indian_cities)
        user = User(
            name=worker_data['name'],
            email=worker_data['email'],
            user_type='worker',
            phone=f'+91-{random.randint(7000000000, 9999999999)}',
            city=location['city'],
            state=location['state'],
            country='India',
            is_verified=True,
            bio=f'Experienced {worker_data["title"]} with passion for quality work'
        )
        user.set_password('password123')
        db.session.add(user)
        db.session.flush()
        
        profile = WorkerProfile(
            user_id=user.id,
            title=worker_data['title'],
            professional_headline=f'{worker_data["exp"]}+ years of professional experience in India',
            skills=worker_data['skills'],
            primary_category=worker_data['category'],
            experience_years=worker_data['exp'],
            experience_level='Senior' if worker_data['exp'] > 10 else 'Mid',
            hourly_rate=worker_data['rate'],
            location=f'{location["city"]}, {location["state"]}',
            bio=f'Dedicated {worker_data["title"]} with {worker_data["exp"]} years of experience serving clients across {location["state"]}.',
            availability='available',
            work_preference='on-site',
            rating=round(random.uniform(4.2, 5.0), 1),
            jobs_completed=random.randint(15, 150),
            response_rate=round(random.uniform(90, 100), 1),
            on_time_delivery=round(random.uniform(92, 100), 1),
            verified=True,
            top_rated=worker_data['exp'] > 10
        )
        db.session.add(profile)
        workers.append(user)
    
    db.session.commit()
    print(f"Created {len(workers)} worker profiles")
    
    jobs_data = [
        {'title': 'Senior Electrician Needed', 'category': 'electrical', 'type': 'full-time', 'salary': '₹40,000 - ₹60,000/month', 'min': 40000, 'max': 60000},
        {'title': 'Construction Site Manager', 'category': 'construction', 'type': 'full-time', 'salary': '₹50,000 - ₹80,000/month', 'min': 50000, 'max': 80000},
        {'title': 'Licensed Plumber', 'category': 'plumbing', 'type': 'contract', 'salary': '₹35,000 - ₹55,000/month', 'min': 35000, 'max': 55000},
        {'title': 'Master Carpenter', 'category': 'carpentry', 'type': 'full-time', 'salary': '₹38,000 - ₹58,000/month', 'min': 38000, 'max': 58000},
        {'title': 'Interior Painter', 'category': 'painting', 'type': 'part-time', 'salary': '₹25,000 - ₹45,000/month', 'min': 25000, 'max': 45000},
        {'title': 'Certified Welder', 'category': 'welding', 'type': 'full-time', 'salary': '₹35,000 - ₹50,000/month', 'min': 35000, 'max': 50000},
        {'title': 'HVAC Technician', 'category': 'hvac', 'type': 'contract', 'salary': '₹30,000 - ₹48,000/month', 'min': 30000, 'max': 48000},
        {'title': 'Mason Worker', 'category': 'masonry', 'type': 'full-time', 'salary': '₹28,000 - ₹42,000/month', 'min': 28000, 'max': 42000},
    ]
    
    for i, job_data in enumerate(jobs_data):
        employer = employers[i % len(employers)]
        location = random.choice(indian_cities)
        job = Job(
            employer_id=employer.id,
            title=job_data['title'],
            company=employer.employer_profile.company_name,
            category=job_data['category'],
            location=f'{location["city"]}, {location["state"]}',
            city=location['city'],
            state=location['state'],
            country='India',
            job_type=job_data['type'],
            work_mode='on-site',
            salary_range=job_data['salary'],
            salary_min=job_data['min'],
            salary_max=job_data['max'],
            salary_currency='INR',
            description='Looking for experienced professional to join our team in India.',
            responsibilities='Perform assigned duties and maintain quality standards according to Indian regulations.',
            requirements='Valid license and minimum experience required. Knowledge of local building codes preferred.',
            skills_required='Technical Skills, Safety, Problem Solving, Hindi/English',
            experience_required=random.randint(2, 10),
            benefits='PF, ESI, Health Insurance, Paid Leave',
            urgent=random.choice([True, False]),
            featured=random.choice([True, False]),
            remote_ok=False,
            status='active',
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        db.session.add(job)
    
    db.session.commit()
    print(f"Created {len(jobs_data)} job postings")
    
    print("="*50)
    print("DATABASE SEEDING COMPLETED!")
    print("="*50)
    print("\nSample Login Credentials:")
    print("Employers: hr@buildtech.in | password123")
    print("Workers: rajesh.kumar@email.com | password123")
    print("="*50 + "\n")

# ==================== INITIALIZE ====================

with app.app_context():
    print("\n" + "="*50)
    print("INITIALIZING SKILLCONNECT INDIA DATABASE")
    print("="*50 + "\n")
    
    db.create_all()
    print("Database tables created successfully!\n")
    
    seed_indian_data()

# ==================== RUN APPLICATION ====================

if __name__ == '__main__':
    print("\n" + "="*70)
    print(" "*15 + "SKILLCONNECT INDIA BACKEND SERVER")
    print("="*70)
    print("\nServer Status: RUNNING")
    print(f"Server URL: http://localhost:5000")
    print(f"API Base: http://localhost:5000/api/")
    print(f"Health Check: http://localhost:5000/api/health")
    print("\nKey Features:")
    print("  - Indian names, locations and currency (₹)")
    print("  - View job and worker details without login")
    print("  - No messaging feature")
    print("="*70 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000) back_populates='employer_profile')
    company_reviews = db.relationship('CompanyReview', back_populates='company', cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'company_size': self.company_size,
            'industry': self.industry,
            'founded_year': self.founded_year,
            'website': self.website,
            'location': self.location,
            'description': self.description,
            'logo': self.logo,
            'rating': self.rating,
            'total_hires': self.total_hires,
            'verified_company': self.verified_company,
            'featured': self.featured
        }

class WorkerProfile(db.Model):
    """Comprehensive worker profile with all professional details"""
    __tablename__ = 'worker_profiles'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    title = db.Column(db.String(100), nullable=False)
    professional_headline = db.Column(db.String(200))
    skills = db.Column(db.Text, nullable=False)
    primary_category = db.Column(db.String(50))
    secondary_categories = db.Column(db.String(200))
    experience_years = db.Column(db.Integer, nullable=False)
    experience_level = db.Column(db.String(50))
    hourly_rate = db.Column(db.Float, nullable=False)
    hourly_rate_min = db.Column(db.Float)
    hourly_rate_max = db.Column(db.Float)
    location = db.Column(db.String(100), nullable=False)
    willing_to_relocate = db.Column(db.Boolean, default=False)
    travel_willingness = db.Column(db.String(50))
    bio = db.Column(db.Text)
    portfolio_url = db.Column(db.String(255))
    resume_url = db.Column(db.String(255))
    video_intro_url = db.Column(db.String(255))
    availability = db.Column(db.String(50), default='available')
    availability_date = db.Column(db.Date)
    work_preference = db.Column(db.String(50))
    rating = db.Column(db.Float, default=0.0)
    jobs_completed = db.Column(db.Integer, default=0)
    jobs_in_progress = db.Column(db.Integer, default=0)
    total_earnings = db.Column(db.Float, default=0.0)
    success_rate = db.Column(db.Float, default=100.0)
    response_rate = db.Column(db.Float, default=100.0)
    response_time = db.Column(db.Integer)
    on_time_delivery = db.Column(db.Float, default=100.0)
    rehire_rate = db.Column(db.Float, default=0.0)
    verified = db.Column(db.Boolean, default=False)
    background_checked = db.Column(db.Boolean, default=False)
    identity_verified = db.Column(db.Boolean, default=False)
    featured = db.Column(db.Boolean, default=False)
    top_rated = db.Column(db.Boolean, default=False)
    languages = db.Column(db.String(200))
    education_level = db.Column(db.String(100))
    union_member = db.Column(db.Boolean, default=False)
    insurance_coverage = db.Column(db.Boolean, default=False)
    licenses = db.Column(db.Text)
    awards = db.Column(db.Text)
    specializations = db.Column(db.Text)
    tools_equipment = db.Column(db.Text)
    safety_certifications = db.Column(db.Text)
    preferred_project_size = db.Column(db.String(50))
    minimum_project_budget = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User',