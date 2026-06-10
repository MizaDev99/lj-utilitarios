import uuid
import os
from django.core.files.storage import Storage
from django.conf import settings


class SupabaseStorage(Storage):
    """Custom Django storage backend para Supabase Storage."""

    def __init__(self, bucket='produtos'):
        self.bucket = bucket
        self._client = None

    def _get_client(self):
        if self._client is None:
            from supabase import create_client
            self._client = create_client(settings.SUPABASE_URL, settings.SUPABASE_SERVICE_KEY)
        return self._client

    def _save(self, name, content):
        ext = os.path.splitext(name)[1].lower()
        filename = f"{uuid.uuid4()}{ext}"
        data = content.read()
        content_type = getattr(content, 'content_type', 'application/octet-stream')
        client = self._get_client()
        client.storage.from_(self.bucket).upload(
            filename, data, {'content-type': content_type}
        )
        return filename

    def url(self, name):
        if not name:
            return ''
        return f"{settings.SUPABASE_URL}/storage/v1/object/public/{self.bucket}/{name}"

    def exists(self, name):
        return False

    def delete(self, name):
        try:
            self._get_client().storage.from_(self.bucket).remove([name])
        except Exception:
            pass

    def size(self, name):
        return 0
