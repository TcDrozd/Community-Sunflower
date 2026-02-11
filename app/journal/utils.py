"""Utilities for journal functionality."""
import os
from uuid import uuid4
from pathlib import Path
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']


def save_photo(photo_file):
    """
    Save and process uploaded photo.
    
    Args:
        photo_file: FileStorage object from request.files
    
    Returns:
        str: Filename of saved photo, or None if save failed
    """
    if not photo_file or not allowed_file(photo_file.filename):
        return None
    
    # Generate unique filename
    ext = secure_filename(photo_file.filename).rsplit('.', 1)[1].lower()
    filename = f"{uuid4().hex}.{ext}"
    filepath = current_app.config['UPLOAD_FOLDER'] / filename
    
    try:
        # Open and process image
        image = Image.open(photo_file)
        
        # Remove EXIF data for privacy
        image_data = list(image.getdata())
        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(image_data)
        
        # Resize if too large
        max_dim = current_app.config['MAX_IMAGE_DIMENSION']
        if max(image_without_exif.size) > max_dim:
            image_without_exif.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
        
        # Save
        image_without_exif.save(filepath, optimize=True, quality=85)
        
        return filename
    except Exception as e:
        current_app.logger.error(f"Error saving photo: {e}")
        return None


def delete_photo(filename):
    """
    Delete photo file.
    
    Args:
        filename: Name of file to delete
    """
    if not filename:
        return
    
    filepath = current_app.config['UPLOAD_FOLDER'] / filename
    
    try:
        if filepath.exists():
            filepath.unlink()
    except Exception as e:
        current_app.logger.error(f"Error deleting photo: {e}")
