"""
Secure file handling utilities for medical documents
"""

import hashlib
import mimetypes
import os
import secrets
import shutil
import time
from pathlib import Path
from typing import Optional, Tuple

from fastapi import UploadFile

from app.core.config import settings


class FileHandler:
    """Secure file handling for medical documents"""

    # Allowed MIME types for medical documents
    ALLOWED_MIME_TYPES = {
        # Images
        "image/jpeg", "image/png", "image/gif", "image/tiff", "image/bmp",
        # Documents
        "application/pdf",
        "application/msword",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        # Text files
        "text/plain", "text/csv",
        # Archives
        "application/zip", "application/x-zip-compressed"
    }

    # Maximum file size (10MB)
    MAX_FILE_SIZE = 10 * 1024 * 1024

    @classmethod
    def validate_file(cls, file: UploadFile) -> Tuple[bool, str]:
        """
        Validate uploaded file
        Returns: (is_valid, error_message)
        """
        # Check file size
        if file.size > cls.MAX_FILE_SIZE:
            return False, f"File size {file.size} exceeds maximum allowed size of {cls.MAX_FILE_SIZE} bytes"

        # Check MIME type
        if file.content_type not in cls.ALLOWED_MIME_TYPES:
            return False, f"File type {file.content_type} is not allowed"

        # Additional filename validation
        if not cls._is_safe_filename(file.filename):
            return False, "Filename contains unsafe characters"

        return True, "File is valid"

    @classmethod
    def _is_safe_filename(cls, filename: str) -> bool:
        """Check if filename is safe"""
        if not filename:
            return False

        # Check for dangerous characters
        dangerous_chars = ['/', '\\', '..', '<', '>', ':', '*', '?', '"', '|']
        for char in dangerous_chars:
            if char in filename:
                return False

        return True

    @classmethod
    def generate_secure_filename(cls, original_filename: str) -> str:
        """Generate secure filename with random component"""
        # Get file extension
        _, ext = os.path.splitext(original_filename)

        # Generate random filename
        random_part = secrets.token_hex(16)
        timestamp = str(int(time.time() * 1000000))

        return f"{timestamp}_{random_part}{ext}"

    @classmethod
    def get_file_path(cls, filename: str, visit_id: str) -> Path:
        """Get secure file path for storage"""
        # Create directory structure: uploads/visits/{visit_id}/
        base_dir = Path(settings.UPLOAD_DIR) / "visits" / str(visit_id)
        base_dir.mkdir(parents=True, exist_ok=True)

        return base_dir / filename

    @classmethod
    async def save_file(cls, file: UploadFile, filepath: Path) -> Tuple[bool, str]:
        """
        Save uploaded file securely
        Returns: (success, error_message)
        """
        try:
            # Ensure directory exists
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Save file
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            return True, "File saved successfully"

        except Exception as e:
            return False, f"Failed to save file: {str(e)}"

    @classmethod
    def calculate_file_hash(cls, filepath: Path) -> Optional[str]:
        """Calculate SHA256 hash of file for integrity checking"""
        try:
            hash_sha256 = hashlib.sha256()
            with open(filepath, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return None

    @classmethod
    def get_file_info(cls, filepath: Path) -> dict:
        """Get file information"""
        try:
            stat = filepath.stat()
            return {
                "size": stat.st_size,
                "modified": stat.st_mtime,
                "created": stat.st_ctime,
                "exists": filepath.exists()
            }
        except Exception:
            return {"exists": False}

    @classmethod
    def delete_file(cls, filepath: Path) -> bool:
        """Delete file securely"""
        try:
            if filepath.exists():
                filepath.unlink()
            return True
        except Exception:
            return False

    @classmethod
    def get_mime_type(cls, filename: str) -> str:
        """Get MIME type from filename"""
        mime_type, _ = mimetypes.guess_type(filename)
        return mime_type or "application/octet-stream"

    @classmethod
    def is_image_file(cls, mime_type: str) -> bool:
        """Check if file is an image"""
        return mime_type.startswith("image/")

    @classmethod
    def is_pdf_file(cls, mime_type: str) -> bool:
        """Check if file is a PDF"""
        return mime_type == "application/pdf"

    @classmethod
    def get_file_extension(cls, filename: str) -> str:
        """Get file extension"""
        _, ext = os.path.splitext(filename)
        return ext.lower()

    @classmethod
    def cleanup_temp_files(cls, temp_dir: Path) -> None:
        """Clean up temporary files"""
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        except Exception:
            pass  # Ignore cleanup errors

    @classmethod
    def ensure_upload_directory(cls) -> None:
        """Ensure upload directory exists"""
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        visits_dir = upload_dir / "visits"
        visits_dir.mkdir(exist_ok=True)

        temp_dir = upload_dir / "temp"
        temp_dir.mkdir(exist_ok=True)