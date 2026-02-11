"""Community routes."""
from flask import render_template, request
from flask_login import login_required

from app.community import bp
from app.models import JournalEntry, Sunflower, User


@bp.route('/')
@login_required
def feed():
    """Community feed of public journal entries."""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Query public entries from all users, ordered by date
    pagination = JournalEntry.query \
        .filter_by(is_public=True) \
        .join(Sunflower) \
        .join(User) \
        .order_by(JournalEntry.date.desc(), JournalEntry.created_at.desc()) \
        .paginate(page=page, per_page=per_page, error_out=False)
    
    entries = pagination.items
    
    return render_template('community/feed.html', 
                         entries=entries, 
                         pagination=pagination)
