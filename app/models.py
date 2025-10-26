from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

class User(UserMixin, db.Model):
    """User model for both students and admins."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False)  # 'admin' or 'student'
    
    # For students, link to their results
    results = db.relationship('Result', backref='student', lazy='dynamic', 
                            foreign_keys='Result.student_id')
    
    def set_password(self, password):
        """Set password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check password against hash."""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin."""
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username} - {self.role}>'

class Result(db.Model):
    """Student result model."""
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, index=True)
    subject = db.Column(db.String(100), nullable=False, index=True)
    marks = db.Column(db.Integer, nullable=False)
    
    # Ensure unique constraint for student_id and subject combination
    __table_args__ = (db.UniqueConstraint('student_id', 'subject', name='unique_student_subject'),)
    
    def __repr__(self):
        return f'<Result {self.student_id} - {self.subject}: {self.marks}>'

@login_manager.user_loader
def load_user(id):
    """Flask-Login user loader callback."""
    return User.query.get(int(id))