"""Journal routes."""
from flask import render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app import db
from app.journal import bp
from app.journal.forms import JournalEntryForm, SunflowerSettingsForm
from app.journal.utils import save_photo, delete_photo
from app.models import JournalEntry


@bp.route('/my-journal')
@login_required
def my_journal():
    """View user's journal timeline."""
    sunflower = current_user.sunflower
    
    if not sunflower:
        flash('Error loading your journal. Please contact support.', 'error')
        return redirect(url_for('index'))
    
    # Get all entries, ordered by date descending
    entries = sunflower.entries.all()
    
    return render_template('journal/my_journal.html', sunflower=sunflower, entries=entries)


@bp.route('/entry/new', methods=['GET', 'POST'])
@login_required
def new_entry():
    """Create new journal entry."""
    sunflower = current_user.sunflower
    
    if not sunflower:
        abort(404)
    
    form = JournalEntryForm()
    
    if form.validate_on_submit():
        # Handle photo upload
        photo_filename = None
        if form.photo.data:
            photo_filename = save_photo(form.photo.data)
            if not photo_filename:
                flash('Error uploading photo. Please try again.', 'error')
                return render_template('journal/entry_form.html', form=form, title='New Entry')
        
        # Create entry
        entry = JournalEntry(
            sunflower_id=sunflower.id,
            date=form.date.data,
            note=form.note.data,
            height_cm=form.height_cm.data,
            photo_path=photo_filename,
            is_public=True  # Default public for MVP
        )
        
        db.session.add(entry)
        db.session.commit()
        
        flash('Entry added to your journal!', 'success')
        return redirect(url_for('journal.my_journal'))
    
    return render_template('journal/entry_form.html', form=form, title='New Entry')


@bp.route('/entry/<int:entry_id>')
@login_required
def view_entry(entry_id):
    """View single entry detail."""
    entry = JournalEntry.query.get_or_404(entry_id)
    
    # Check ownership
    if entry.sunflower.user_id != current_user.id:
        abort(403)
    
    return render_template('journal/entry_detail.html', entry=entry)


@bp.route('/entry/<int:entry_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_entry(entry_id):
    """Edit journal entry."""
    entry = JournalEntry.query.get_or_404(entry_id)
    
    # Check ownership
    if entry.sunflower.user_id != current_user.id:
        abort(403)
    
    form = JournalEntryForm(obj=entry)
    
    if form.validate_on_submit():
        # Handle photo upload
        if form.photo.data:
            # Delete old photo if exists
            if entry.photo_path:
                delete_photo(entry.photo_path)
            
            photo_filename = save_photo(form.photo.data)
            if photo_filename:
                entry.photo_path = photo_filename
            else:
                flash('Error uploading photo. Entry saved without new photo.', 'warning')
        
        # Update entry
        entry.date = form.date.data
        entry.note = form.note.data
        entry.height_cm = form.height_cm.data
        
        db.session.commit()
        
        flash('Entry updated!', 'success')
        return redirect(url_for('journal.my_journal'))
    
    return render_template('journal/entry_form.html', form=form, title='Edit Entry', entry=entry)


@bp.route('/entry/<int:entry_id>/delete', methods=['POST'])
@login_required
def delete_entry(entry_id):
    """Delete journal entry."""
    entry = JournalEntry.query.get_or_404(entry_id)
    
    # Check ownership
    if entry.sunflower.user_id != current_user.id:
        abort(403)
    
    # Delete photo if exists
    if entry.photo_path:
        delete_photo(entry.photo_path)
    
    db.session.delete(entry)
    db.session.commit()
    
    flash('Entry deleted.', 'info')
    return redirect(url_for('journal.my_journal'))


@bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """Edit sunflower settings."""
    sunflower = current_user.sunflower
    
    if not sunflower:
        abort(404)
    
    form = SunflowerSettingsForm(obj=sunflower)
    
    if form.validate_on_submit():
        sunflower.name = form.name.data
        sunflower.planted_date = form.planted_date.data
        
        db.session.commit()
        
        flash('Settings saved!', 'success')
        return redirect(url_for('journal.my_journal'))
    
    return render_template('journal/settings.html', form=form, sunflower=sunflower)
