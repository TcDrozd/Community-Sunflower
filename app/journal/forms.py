"""Journal forms."""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, DateField, FloatField, SubmitField
from wtforms.validators import DataRequired, Length, Optional, NumberRange
from datetime import date


class SunflowerSettingsForm(FlaskForm):
    """Edit sunflower settings."""
    
    name = StringField('Sunflower Name', validators=[
        DataRequired(),
        Length(min=1, max=50, message='Name must be between 1 and 50 characters')
    ])
    planted_date = DateField('Date Planted', validators=[DataRequired()])
    submit = SubmitField('Save Settings')


class JournalEntryForm(FlaskForm):
    """Create or edit journal entry."""
    
    date = DateField('Date', validators=[DataRequired()], default=date.today)
    note = TextAreaField('Notes', validators=[
        Optional(),
        Length(max=2000, message='Notes must be less than 2000 characters')
    ])
    height_cm = FloatField('Height (cm)', validators=[
        Optional(),
        NumberRange(min=0, max=1000, message='Height must be between 0 and 1000 cm')
    ])
    photo = FileField('Photo', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif'], 'Only image files are allowed')
    ])
    submit = SubmitField('Save Entry')
