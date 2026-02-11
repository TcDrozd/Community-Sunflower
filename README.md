# Sunflower Journal

A friendly, community-focused web app where neighbors can sign up and create their own Sunflower Journal to track a sunflower from seed to bloom.

## Features

### MVP (Current)
- User accounts with email/password authentication
- One sunflower journal per user
- Journal entries with:
  - Date (defaults to today)
  - Text notes
  - Optional photo upload
  - Optional height tracking (cm)
- Personal journal timeline view
- Community feed showing public entries
- Admin moderation tools
- Mobile-first responsive design

## Tech Stack

**Backend:**
- Flask 3.x + Jinja2
- SQLAlchemy 2.x (ORM)
- SQLite (dev) / PostgreSQL (production)
- Flask-Login (authentication)
- Argon2 (password hashing)
- Pillow (image processing)

**Frontend:**
- Pico CSS (semantic, classless styling)
- HTMX 2.x (dynamic updates)
- Minimal JavaScript

## Setup

### Prerequisites
- Python 3.9+
- pip

### Installation

1. **Clone the repository**
   ```bash
   cd sunflower-journal
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set:
   - `SECRET_KEY` (generate with `python -c "import secrets; print(secrets.token_hex(32))"`)
   - Email settings (optional for MVP - defaults to console logging)

5. **Initialize database**
   ```bash
   python run.py
   ```
   The database will be created automatically on first run.

6. **Create admin user** (optional)
   ```python
   # In Python shell
   from app import create_app, db
   from app.models import User, Sunflower
   from datetime import datetime
   
   app = create_app()
   with app.app_context():
       user = User(email='admin@example.com', display_name='Admin')
       user.set_password('your-secure-password')
       user.is_admin = True
       db.session.add(user)
       db.session.flush()
       
       sunflower = Sunflower(user_id=user.id, name='Admin Sunflower')
       db.session.add(sunflower)
       db.session.commit()
   ```

### Running the App

**Development:**
```bash
python run.py
```
Visit http://localhost:5000

**Production:**
```bash
gunicorn -w 4 -b 0.0.0.0:8000 'app:create_app()'
```

## Project Structure

```
sunflower-journal/
├── app/
│   ├── __init__.py          # App factory
│   ├── models.py            # Database models
│   ├── routes.py            # Main routes
│   ├── auth/                # Authentication
│   │   ├── routes.py
│   │   └── forms.py
│   ├── journal/             # Journal features
│   │   ├── routes.py
│   │   ├── forms.py
│   │   └── utils.py
│   ├── community/           # Community feed
│   │   └── routes.py
│   ├── admin/               # Admin tools
│   │   └── routes.py
│   ├── static/
│   │   └── uploads/         # User photos
│   └── templates/           # Jinja2 templates
├── config.py                # Configuration
├── requirements.txt         # Dependencies
├── run.py                   # Dev server
└── README.md
```

## Database Schema

**User**
- id, email, display_name, password_hash, is_admin, created_at
- One-to-one: Sunflower

**Sunflower**
- id, user_id, name, planted_date, theme, created_at
- One-to-many: JournalEntry

**JournalEntry**
- id, sunflower_id, date, note, height_cm, photo_path, is_public, created_at, updated_at

## File Uploads

**Storage:**
- Development: Local filesystem (`app/static/uploads/`)
- Production: S3-compatible (interface ready, not yet implemented)

**Processing:**
- Max size: 5MB
- Allowed formats: JPG, JPEG, PNG, GIF
- Auto-resize: 1200px max dimension
- EXIF removal: For privacy

## Security Features

- Argon2 password hashing (auto-rehashing on login)
- CSRF protection on all forms
- Secure session cookies (production)
- File upload validation
- EXIF data removal from photos
- Admin-only routes
- SQL injection protection (SQLAlchemy ORM)

## Admin Features

Access admin dashboard at `/admin` (requires admin flag on user)

**Available tools:**
- View user statistics
- List all users
- Toggle admin status
- Delete users (with all data)
- View all entries
- Delete entries (moderation)

## Development Workflow

1. Make changes to code
2. Flask auto-reloads on file changes
3. Database migrations (if schema changes):
   ```bash
   flask db migrate -m "Description"
   flask db upgrade
   ```

## Testing

```bash
pytest
pytest --cov=app  # With coverage
```

## Deployment Checklist

- [ ] Set strong `SECRET_KEY` in production
- [ ] Configure production database (PostgreSQL)
- [ ] Set up email service (SendGrid, Mailgun, etc.)
- [ ] Configure S3 or equivalent for photo storage
- [ ] Enable HTTPS
- [ ] Set session cookie security flags
- [ ] Configure proper logging
- [ ] Set up backups
- [ ] Monitor error rates

## Future Enhancements

- Per-entry privacy toggle (public/private)
- Password reset email flow
- Email notifications
- Profile customization (themes, badges)
- Advanced search/filtering
- Growth charts and statistics
- S3 photo storage integration
- Mobile apps (PWA or native)

## Contact

Trevor Drozd
trcharlesd@gmail.com
