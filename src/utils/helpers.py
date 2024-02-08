import os
import hashlib
from django.utils import timezone


def generate_dated_filepath(filename):
    current_timestamp = timezone.now()
    date = current_timestamp.strftime("%Y/%m/%d")
    return f"{date}/{current_timestamp.timestamp()}_{filename}"

def hash_filename(filename: str) -> str:
    filename, extension = os.path.splitext(filename)
    hashed_name = hashlib.sha256(filename.encode("utf-8")).hexdigest()
    return f"{hashed_name}{extension}"
