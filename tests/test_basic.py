"""Basic tests for Sunflower Journal."""
import pytest
from app import create_app, db
from app.models import User, Sunflower


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
