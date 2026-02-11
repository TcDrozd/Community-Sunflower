"""Admin routes."""
from functools import wraps
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app import db
from app.admin import bp
from app.models import User, Sunflower, JournalEntry


def admin_required(f):
    """Decorator to require admin access."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


@bp.route('/')
@login_required
@admin_required
def dashboard():
    """Admin dashboard."""
    # Get counts
    user_count = User.query.count()
    entry_count = JournalEntry.query.count()
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    recent_entries = JournalEntry.query \
        .order_by(JournalEntry.created_at.desc()) \
        .limit(10).all()
    
    return render_template('admin/dashboard.html',
                         user_count=user_count,
                         entry_count=entry_count,
                         recent_users=recent_users,
                         recent_entries=recent_entries)


@bp.route('/users')
@login_required
@admin_required
def users():
    """List all users."""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    pagination = User.query \
        .order_by(User.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/users.html', 
                         users=pagination.items,
                         pagination=pagination)


@bp.route('/entries')
@login_required
@admin_required
def entries():
    """List all journal entries for moderation."""
    page = request.args.get('page', 1, type=int)
    per_page = 50
    
    pagination = JournalEntry.query \
        .order_by(JournalEntry.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/entries.html',
                         entries=pagination.items,
                         pagination=pagination)


@bp.route('/entry/<int:entry_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_entry(entry_id):
    """Delete entry (moderation)."""
    entry = JournalEntry.query.get_or_404(entry_id)
    
    # Delete photo if exists
    from app.journal.utils import delete_photo
    if entry.photo_path:
        delete_photo(entry.photo_path)
    
    db.session.delete(entry)
    db.session.commit()
    
    flash('Entry deleted.', 'info')
    return redirect(url_for('admin.entries'))


@bp.route('/user/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    """Toggle admin status for user."""
    user = User.query.get_or_404(user_id)
    
    # Prevent removing own admin status
    if user.id == current_user.id:
        flash('Cannot modify your own admin status.', 'error')
        return redirect(url_for('admin.users'))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = 'granted' if user.is_admin else 'revoked'
    flash(f'Admin access {status} for {user.display_name}.', 'info')
    
    return redirect(url_for('admin.users'))


@bp.route('/user/<int:user_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """Delete user account (with all data)."""
    user = User.query.get_or_404(user_id)
    
    # Prevent self-deletion
    if user.id == current_user.id:
        flash('Cannot delete your own account from admin panel.', 'error')
        return redirect(url_for('admin.users'))
    
    # Delete all photos for user's entries
    from app.journal.utils import delete_photo
    if user.sunflower:
        for entry in user.sunflower.entries:
            if entry.photo_path:
                delete_photo(entry.photo_path)
    
    db.session.delete(user)
    db.session.commit()
    
    flash(f'User {user.display_name} and all associated data deleted.', 'info')
    return redirect(url_for('admin.users'))
