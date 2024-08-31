
from typing import List
from django.core.exceptions import ValidationError
from django.conf import settings


def validate_file_size(file):
    max_size = settings.FILE_UPLOAD_MAX_MEMORY_SIZE
    if file.size > max_size:
        raise ValidationError(f"File size must be nor more than {max_size/1024/1024}MB")

def validate_file_format(file, allowed_formats: List[str]):
    file_ext = file.name.split('.')[-1].lower()
    if file_ext not in allowed_formats:
        raise ValidationError(f"File must be either: {', '.join(allowed_formats)}")
    

def validate_max_filename_length(filename):
    if len(filename) > 200:
        raise ValidationError("File name is large, it can't be more that 200 character")
