"""Basic tests for Sunflower Journal."""
import io
from datetime import date
import pytest
from app import create_app, db
from app.models import User, Sunflower, JournalEntry


@pytest.fixture
def app():
    """Create test app."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()


@pytest.fixture
def auth_client(client):
    """Create authenticated test client."""
    # Create test user
    from app import db
    from app.models import User, Sunflower
    from datetime import datetime
    
    with client.application.app_context():
        user = User(email='test@example.com', display_name='Test User')
        user.set_password('testpass123')
        db.session.add(user)
        db.session.flush()
        
        sunflower = Sunflower(user_id=user.id, name='Test Sunflower')
        db.session.add(sunflower)
        db.session.commit()
    
    # Log in
    client.post('/auth/login', data={
        'email': 'test@example.com',
        'password': 'testpass123',
        'csrf_token': 'test'  # Disabled in testing config
    }, follow_redirects=True)
    
    return client


def test_app_exists(app):
    """Test that app instance exists."""
    assert app is not None


def test_homepage(client):
    """Test homepage loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'Sunflower Journal' in response.data


def test_registration(client):
    """Test user registration."""
    response = client.post('/auth/register', data={
        'email': 'newuser@example.com',
        'display_name': 'New User',
        'password': 'password123',
        'password_confirm': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verify user was created
    with client.application.app_context():
        user = User.query.filter_by(email='newuser@example.com').first()
        assert user is not None
        assert user.display_name == 'New User'
        assert user.sunflower is not None


def test_login(client):
    """Test login."""
    # Create user first
    with client.application.app_context():
        user = User(email='login@example.com', display_name='Login Test')
        user.set_password('testpass')
        db.session.add(user)
        db.session.flush()
        
        sunflower = Sunflower(user_id=user.id)
        db.session.add(sunflower)
        db.session.commit()
    
    # Test login
    response = client.post('/auth/login', data={
        'email': 'login@example.com',
        'password': 'testpass'
    }, follow_redirects=True)
    
    assert response.status_code == 200


def test_password_hashing():
    """Test password hashing."""
    user = User(email='test@test.com', display_name='Test')
    user.set_password('mypassword')
    
    assert user.password_hash != 'mypassword'
    assert user.check_password('mypassword')
    assert not user.check_password('wrongpassword')


def test_protected_journal_route_requires_login(client):
    """Journal pages should require authentication."""
    response = client.get('/my-journal')
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_community_feed_requires_login(client):
    """Community feed should require authentication."""
    response = client.get('/community/')
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_admin_dashboard_forbidden_for_non_admin(auth_client):
    """Authenticated non-admin users cannot access admin area."""
    response = auth_client.get('/admin/')
    assert response.status_code == 403


def test_photo_validation_rejects_invalid_extension(auth_client):
    """Form validation should reject non-image extensions."""
    response = auth_client.post(
        '/entry/new',
        data={
            'date': '2026-02-13',
            'note': 'Trying invalid photo',
            'photo': (io.BytesIO(b'not-an-image'), 'bad.txt')
        },
        content_type='multipart/form-data',
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b'Only image files are allowed' in response.data

    with auth_client.application.app_context():
        assert JournalEntry.query.count() == 0


def test_photo_validation_rejects_invalid_image_bytes(auth_client):
    """Server-side processing should reject bad image content."""
    response = auth_client.post(
        '/entry/new',
        data={
            'date': '2026-02-13',
            'note': 'Trying bad jpg bytes',
            'photo': (io.BytesIO(b'not-a-real-jpeg'), 'bad.jpg')
        },
        content_type='multipart/form-data',
        follow_redirects=True
    )

    assert response.status_code == 200
    assert b'Error uploading photo. Please try again.' in response.data

    with auth_client.application.app_context():
        assert JournalEntry.query.count() == 0


def test_edit_entry_page_renders_with_csrf(auth_client):
    """Editing an existing entry should render without CSRF template errors."""
    with auth_client.application.app_context():
        user = User.query.filter_by(email='test@example.com').first()
        entry = JournalEntry(
            sunflower_id=user.sunflower.id,
            date=date(2026, 2, 13),
            note='Existing entry'
        )
        db.session.add(entry)
        db.session.commit()
        entry_id = entry.id

    response = auth_client.get(f'/entry/{entry_id}/edit')
    assert response.status_code == 200
    assert b'Delete Entry' in response.data
