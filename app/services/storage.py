import os
import uuid
from werkzeug.utils import secure_filename

ALLOWED_EXTS = {"mp3", "wav"}

class LocalStorageDriver:
    def __init__(self, base_dir="uploads"):
        self.base_dir = base_dir

    def save(self, file_storage):
        filename = secure_filename(file_storage.filename or "")
        ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        if ext not in ALLOWED_EXTS:
            raise ValueError("허용되지 않는 확장자 (mp3, wav만 가능)")
        os.makedirs(self.base_dir, exist_ok=True)
        new_name = f"{uuid.uuid4().hex}.{ext}"
        path = os.path.join(self.base_dir, new_name)
        file_storage.save(path)
        return path

    def public_url(self, stored_path):
        rel = os.path.basename(stored_path)
        return f"/media/{rel}"
