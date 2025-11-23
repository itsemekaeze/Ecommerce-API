
from fastapi import UploadFile, HTTPException
import shutil
import uuid
from pathlib import Path


UPLOAD_DIR = Path("static")
UPLOAD_DIR.mkdir(exist_ok=True)
PROFILE_IMAGES_DIR = UPLOAD_DIR / "profiles"
PROFILE_IMAGES_DIR.mkdir(exist_ok=True)

PRODUCT_IMAGES_DIR = UPLOAD_DIR / "products"
PRODUCT_IMAGES_DIR.mkdir(exist_ok=True)

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
MAX_FILE_SIZE = 5 * 1024 * 1024 


def validate_image_file(file: UploadFile) -> None:
    
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )
    
    
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE / (1024*1024)}MB"
        )

def save_upload_file(file: UploadFile, directory: Path) -> str:
    file_ext = Path(file.filename).suffix.lower()
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = directory / unique_filename

    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return str(file_path)



