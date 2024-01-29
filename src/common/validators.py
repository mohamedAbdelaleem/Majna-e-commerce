
from django.conf import settings
from django.core.exceptions import ValidationError

def max_file_size(file):
    limit = settings.FILE_UPLOAD_MAX_MEMORY_SIZE
    if file.size > limit:
        raise ValidationError(f"File size must be nor more than {limit/1024/1024}MB")

def pdf_format(file):
    file_ext = file.name.split('.')[-1].lower()
    if file_ext != 'pdf':
        raise ValidationError("File must be pdf")
