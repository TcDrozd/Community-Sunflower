"""Database models."""
from datetime import datetime
from flask_login import UserMixin
from argon2 import PasswordHasher
from app import db

ph = PasswordHasher()


class User(UserMixin, db.Model):
    """User account model."""
    
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    display_name = db.Column(db.String(80), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    sunflower = db.relationship('Sunflower', backref='user', uselist=False, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password."""
        self.password_hash = ph.hash(password)
    
    def check_password(self, password):
        """Verify password against hash."""
        try:
            ph.verify(self.password_hash, password)
            # Rehash if needed (Argon2 parameters changed)
            if ph.check_needs_rehash(self.password_hash):
                self.password_hash = ph.hash(password)
                db.session.commit()
            return True
        except:
            return False
    
    def __repr__(self):
        return f'<User {self.email}>'


class Sunflower(db.Model):
    """User's sunflower journal."""
    
    __tablename__ = 'sunflowers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)
    name = db.Column(db.String(50), nullable=False, default='My Sunflower')
    planted_date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    theme = db.Column(db.String(20), default='yellow')  # For future customization
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    entries = db.relationship('JournalEntry', backref='sunflower', lazy='dynamic',
                             cascade='all, delete-orphan', order_by='JournalEntry.date.desc()')
    
    def __repr__(self):
        return f'<Sunflower {self.name} (User {self.user_id})>'


class JournalEntry(db.Model):
    """Individual journal entry for a sunflower."""
    
    __tablename__ = 'journal_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    sunflower_id = db.Column(db.Integer, db.ForeignKey('sunflowers.id'), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow, index=True)
    note = db.Column(db.Text, nullable=True)
    height_cm = db.Column(db.Float, nullable=True)
    photo_path = db.Column(db.String(255), nullable=True)
    is_public = db.Column(db.Boolean, default=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<JournalEntry {self.id} for Sunflower {self.sunflower_id}>'
    
    @property
    def photo_url(self):
        """Get URL for photo if it exists."""
        if self.photo_path:
            return f'/static/uploads/{self.photo_path}'
        return None
