from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='Estudiante') # Super-Admin, Admin, Asesor, Estudiante
    
    profile = db.relationship('Profile', backref='user', uselist=False, cascade='all, delete-orphan')
    
    # For Asesor
    sessions_given = db.relationship('TutoringSession', backref='asesor', cascade='all, delete-orphan')
    reviews_received = db.relationship('Review', foreign_keys='Review.asesor_id', backref='asesor_reviewed', cascade='all, delete-orphan')
    
    # For Estudiante
    enrollments = db.relationship('Enrollment', backref='student', cascade='all, delete-orphan')
    reviews_given = db.relationship('Review', foreign_keys='Review.student_id', backref='student_reviewer', cascade='all, delete-orphan')

    def __repr__(self):
        return f"User('{self.username}', '{self.role}')"

class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    strengths = db.Column(db.String(200), nullable=True) # e.g. "matemáticas, programación"
    focus_areas = db.Column(db.String(200), nullable=True) # e.g. "álgebra, base de datos sql"
    rating_avg = db.Column(db.Float, default=0.0) # Calculated average for Asesores
    
    def __repr__(self):
        return f"Profile('{self.full_name}')"

class TutoringSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    asesor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    topic = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    session_type = db.Column(db.String(20), nullable=False, default='Individual') # Individual, Grupal
    capacity = db.Column(db.Integer, default=1)
    
    enrollments = db.relationship('Enrollment', backref='session', cascade='all, delete-orphan')
    reviews = db.relationship('Review', foreign_keys='Review.session_id', backref='session_reviewed', cascade='all, delete-orphan')

    def __repr__(self):
        return f"TutoringSession('{self.topic}', '{self.date}')"

class Enrollment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('tutoring_session.id'), nullable=False)
    status = db.Column(db.String(20), default='Inscrito') # Inscrito, Cancelado

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('tutoring_session.id'), nullable=False)
    asesor_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False) # 1 to 5
    comment = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class RoleRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='Pendiente') # Pendiente, Aprobado, Rechazado
    reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    user_rel = db.relationship('User', backref=db.backref('role_requests', lazy=True))
