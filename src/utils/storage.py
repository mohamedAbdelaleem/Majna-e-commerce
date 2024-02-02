from datetime import timedelta
from django.conf import settings
from django.core.files import File
from supabase import create_client


class SupabaseStorageService:

    def __init__(self) -> None:
        url = settings.SUPABASE_URL
        key = settings.SUPABASE_KEY
        self.client = create_client(url, key)

    
    def upload(self, file: File, bucket: str, path: str='', file_options=None):
        if not path:
            path = file.name
        with file as f:
            file_content = f.read()
            self.client.storage.from_(bucket).upload(file=file_content, path=path, file_options=file_options)
    
    def get_url(self, bucket, path):
        duration = timedelta(days=2).total_seconds()
        url = self.client.storage.from_(bucket).create_signed_url(path, duration)
        return url



