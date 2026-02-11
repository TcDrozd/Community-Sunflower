"""Authentication routes."""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlparse
from datetime import datetime

from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, RequestPasswordResetForm, ResetPasswordForm
from app.models import User, Sunflower


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration."""
    if current_user.is_authenticated:
        return redirect(url_for('journal.my_journal'))
    
    form = RegistrationForm()
    
    if form.validate_on_submit():
        # Create user
        user = User(
            email=form.email.data.lower(),
            display_name=form.display_name.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()  # Get user.id
        
        # Create sunflower journal for user
        sunflower = Sunflower(
            user_id=user.id,
            name='My Sunflower',
            planted_date=datetime.utcnow().date()
        )
        db.session.add(sunflower)
        db.session.commit()
        
        flash('Welcome to the Sunflower Community! Your journal is ready.', 'success')
        login_user(user)
        return redirect(url_for('journal.my_journal'))
    
    return render_template('auth/register.html', form=form)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login."""
    if current_user.is_authenticated:
        return redirect(url_for('journal.my_journal'))
    
    form = LoginForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            
            # Redirect to next page or journal
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('journal.my_journal')
            
            flash(f'Welcome back, {user.display_name}!', 'success')
            return redirect(next_page)
        else:
            flash('Invalid email or password. Please try again.', 'error')
    
    return render_template('auth/login.html', form=form)


@bp.route('/logout')
def logout():
    """User logout."""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@bp.route('/reset-password-request', methods=['GET', 'POST'])
def reset_password_request():
    """Request password reset."""
    if current_user.is_authenticated:
        return redirect(url_for('journal.my_journal'))
    
    form = RequestPasswordResetForm()
    
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.lower()).first()
        
        if user:
            # TODO: Send password reset email
            # For now, just show a message
            flash('Password reset instructions have been sent to your email.', 'info')
        else:
            # Don't reveal that email doesn't exist (security)
            flash('Password reset instructions have been sent to your email.', 'info')
        
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html', form=form)


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token."""
    if current_user.is_authenticated:
        return redirect(url_for('journal.my_journal'))
    
    # TODO: Verify token and get user
    # For MVP, this is a placeholder
    
    form = ResetPasswordForm()
    
    if form.validate_on_submit():
        # TODO: Update user password
        flash('Your password has been reset.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password.html', form=form)
