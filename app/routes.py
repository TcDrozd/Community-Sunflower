"""Main application routes."""
from flask import render_template, redirect, url_for
from flask_login import current_user


def init_app(app):
    """Register main routes with app."""
    
    @app.route('/')
    def index():
        """Homepage - redirect based on auth status."""
        if current_user.is_authenticated:
            return redirect(url_for('journal.my_journal'))
        return render_template('index.html')
    
    @app.route('/about')
    def about():
        """About page."""
        return render_template('about.html')
    
    @app.errorhandler(404)
    def not_found(error):
        """404 error handler."""
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 error handler."""
        from app import db
        db.session.rollback()
        return render_template('errors/500.html'), 500
