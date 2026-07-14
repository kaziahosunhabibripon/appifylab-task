from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.config import settings

try:
    import cloudinary
    import cloudinary.uploader
except ImportError:
    cloudinary = None


UPLOAD_DIR = Path("uploads")
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}


def _cloudinary_configured() -> bool:
    cloud_name = settings.CLOUDINARY_CLOUD_NAME
    api_key = settings.CLOUDINARY_API_KEY
    api_secret = settings.CLOUDINARY_API_SECRET

    if not cloudinary or not cloud_name or not api_key or not api_secret:
        return False

    cloudinary.config(
        cloud_name=cloud_name,
        api_key=api_key,
        api_secret=api_secret,
        secure=True,
    )
    return True


def _upload_to_cloudinary(file: UploadFile) -> str | None:
    if not _cloudinary_configured():
        return None

    file.file.seek(0)
    try:
        result = cloudinary.uploader.upload(
            file.file,
            folder="appifylab/posts",
            resource_type="image",
        )
    except Exception:
        return None

    return result.get("secure_url")


def save_upload_file(file: UploadFile | None) -> str | None:
    if file is None or not file.filename:
        return None

    cloudinary_url = _upload_to_cloudinary(file)
    if cloudinary_url:
        return cloudinary_url

    file.file.seek(0)
    extension = Path(file.filename).suffix.lower()
    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        extension = ".jpg"

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{uuid4().hex}{extension}"
    destination = UPLOAD_DIR / filename

    with destination.open("wb") as output:
        output.write(file.file.read())

    return f"/uploads/{filename}"
