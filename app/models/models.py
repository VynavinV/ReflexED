"""
Database models for ReflexED application.
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import db
import uuid


class User(db.Model):
    """User model for authentication and profile management."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # User type: 'student', 'teacher', 'admin'
    role = db.Column(db.String(20), nullable=False, default='student')
    
    # Profile information
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    native_language = db.Column(db.String(10), default='en')
    learning_languages = db.Column(db.JSON, default=list)  # List of language codes
    
    # Account status
    is_active = db.Column(db.Boolean, default=True)
    is_verified = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    translation_sessions = db.relationship('TranslationSession', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    progress_records = db.relationship('UserProgress', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if password matches hash."""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self, include_email=False):
        """Convert user to dictionary."""
        data = {
            'id': self.id,
            'username': self.username,
            'role': self.role,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'native_language': self.native_language,
            'learning_languages': self.learning_languages,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }
        if include_email:
            data['email'] = self.email
        return data
    
    def __repr__(self):
        return f'<User {self.username}>'


class TranslationSession(db.Model):
    """Track individual translation practice sessions."""
    
    __tablename__ = 'translation_sessions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Translation details
    source_text = db.Column(db.Text, nullable=False)
    source_language = db.Column(db.String(10), nullable=False)
    target_language = db.Column(db.String(10), nullable=False)
    user_translation = db.Column(db.Text)
    
    # AI Analysis
    ai_questions = db.Column(db.JSON)  # List of questions asked by AI
    ai_hints = db.Column(db.JSON)  # Hints provided
    correct_translation = db.Column(db.Text)
    grammar_points = db.Column(db.JSON)  # Grammar concepts identified
    vocabulary_suggestions = db.Column(db.JSON)  # Vocabulary insights
    
    # Scoring
    accuracy_score = db.Column(db.Float)  # 0-100
    grammar_score = db.Column(db.Float)
    vocabulary_score = db.Column(db.Float)
    
    # Session metadata
    difficulty_level = db.Column(db.String(20))  # beginner, intermediate, advanced
    time_spent_seconds = db.Column(db.Integer)
    hints_requested = db.Column(db.Integer, default=0)
    completed = db.Column(db.Boolean, default=False)
    
    # Timestamps
    started_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    completed_at = db.Column(db.DateTime)
    
    def to_dict(self):
        """Convert session to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'source_text': self.source_text,
            'source_language': self.source_language,
            'target_language': self.target_language,
            'user_translation': self.user_translation,
            'ai_questions': self.ai_questions,
            'ai_hints': self.ai_hints,
            'correct_translation': self.correct_translation,
            'grammar_points': self.grammar_points,
            'vocabulary_suggestions': self.vocabulary_suggestions,
            'accuracy_score': self.accuracy_score,
            'grammar_score': self.grammar_score,
            'vocabulary_score': self.vocabulary_score,
            'difficulty_level': self.difficulty_level,
            'time_spent_seconds': self.time_spent_seconds,
            'hints_requested': self.hints_requested,
            'completed': self.completed,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
        }
    
    def __repr__(self):
        return f'<TranslationSession {self.id} - {self.source_language} to {self.target_language}>'


class UserProgress(db.Model):
    """Track user learning progress over time."""
    
    __tablename__ = 'user_progress'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    
    # Progress metrics
    language = db.Column(db.String(10), nullable=False, index=True)
    total_sessions = db.Column(db.Integer, default=0)
    completed_sessions = db.Column(db.Integer, default=0)
    average_accuracy = db.Column(db.Float, default=0.0)
    
    # Skill breakdown
    grammar_level = db.Column(db.String(20), default='beginner')  # beginner, intermediate, advanced
    vocabulary_level = db.Column(db.String(20), default='beginner')
    overall_level = db.Column(db.String(20), default='beginner')
    
    # Learning streaks
    current_streak_days = db.Column(db.Integer, default=0)
    longest_streak_days = db.Column(db.Integer, default=0)
    last_practice_date = db.Column(db.Date)
    
    # Mastered concepts
    mastered_grammar_points = db.Column(db.JSON, default=list)
    mastered_vocabulary = db.Column(db.JSON, default=list)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint: one progress record per user per language
    __table_args__ = (
        db.UniqueConstraint('user_id', 'language', name='unique_user_language_progress'),
    )
    
    def to_dict(self):
        """Convert progress to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'language': self.language,
            'total_sessions': self.total_sessions,
            'completed_sessions': self.completed_sessions,
            'average_accuracy': self.average_accuracy,
            'grammar_level': self.grammar_level,
            'vocabulary_level': self.vocabulary_level,
            'overall_level': self.overall_level,
            'current_streak_days': self.current_streak_days,
            'longest_streak_days': self.longest_streak_days,
            'last_practice_date': self.last_practice_date.isoformat() if self.last_practice_date else None,
            'mastered_grammar_points': self.mastered_grammar_points,
            'mastered_vocabulary': self.mastered_vocabulary,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
    
    def __repr__(self):
        return f'<UserProgress {self.user_id} - {self.language}>'


class TokenBlacklist(db.Model):
    """Store revoked JWT tokens."""
    
    __tablename__ = 'token_blacklist'
    
    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(36), nullable=False, unique=True, index=True)
    token_type = db.Column(db.String(10), nullable=False)  # access or refresh
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    revoked_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    
    def __repr__(self):
        return f'<TokenBlacklist {self.jti}>'


class Assignment(db.Model):
    """Teacher-created assignment/lesson with generated variants."""

    __tablename__ = 'assignments'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    teacher_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=True, index=True)

    title = db.Column(db.String(200), nullable=False, index=True)
    subject = db.Column(db.String(50), nullable=False, index=True)  # math, science, language, history, geography

    # Original content details
    original_content = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(255), nullable=True)

    # Generation status lifecycle
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending|generating|ready|failed
    error_message = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    versions = db.relationship('AssignmentVersion', backref='assignment', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self, include_versions: bool = False):
        data = {
            'id': self.id,
            'teacher_id': self.teacher_id,
            'title': self.title,
            'subject': self.subject,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_versions:
            data['versions'] = [v.to_dict() for v in self.versions.order_by(AssignmentVersion.created_at.asc()).all()]
        return data

    def __repr__(self):
        return f'<Assignment {self.id} - {self.title}>'


class AssignmentVersion(db.Model):
    """AI-generated variant for an assignment (simplified, audio, visual, quiz)."""

    __tablename__ = 'assignment_versions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    assignment_id = db.Column(db.String(36), db.ForeignKey('assignments.id'), nullable=False, index=True)

    # Variant metadata
    variant_type = db.Column(db.String(20), nullable=False, index=True)  # simplified|audio|visual|quiz
    subject = db.Column(db.String(50), nullable=False, index=True)

    # Core content and assets
    content_text = db.Column(db.Text)  # script/simplified/description JSON as text
    assets = db.Column(db.JSON, default=dict)  # file paths: {"audio_mp3": "...", "video_mp4": "...", "captions_vtt": "...", "manim_script": "..."}

    # Generation status
    ready = db.Column(db.Boolean, default=False)
    error_message = db.Column(db.Text)

    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.Index('idx_assignment_variant_unique', 'assignment_id', 'variant_type', unique=True),
    )

    def to_dict(self):
        # Convert file paths to URLs
        assets = self.assets or {}
        url_assets = {}
        for key, path in assets.items():
            if path and isinstance(path, str):
                # Convert absolute path to relative URL
                if '/uploads/' in path:
                    # Extract the part after 'uploads/'
                    url_path = path.split('/uploads/', 1)[-1]
                    url_assets[key] = f'/uploads/{url_path}'
                else:
                    url_assets[key] = path
            else:
                url_assets[key] = path
        
        return {
            'id': self.id,
            'assignment_id': self.assignment_id,
            'variant_type': self.variant_type,
            'subject': self.subject,
            'content_text': self.content_text,
            'assets': url_assets,
            'ready': self.ready,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<AssignmentVersion {self.assignment_id}:{self.variant_type}>'
