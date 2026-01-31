# utils.py

from django.core.exceptions import ValidationError

def validate_file_size(file, file_type='video'):
    """
    Validates the uploaded file size.
    - file_type: 'photo' allows up to 1MB
                 'video' allows up to 10MB
    Raises ValidationError if size exceeds the limit.
    """
    max_size_mb = 10 if file_type == 'video' else 5
    max_size_bytes = max_size_mb * 1024 * 1024

    if file.size > max_size_bytes:
        raise ValidationError(f"{file_type.capitalize()} size should not exceed {max_size_mb} MB.")
