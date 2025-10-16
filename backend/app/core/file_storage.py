"""
File storage utilities for ArchMesh PoC.

This module handles file uploads, storage, and management for documents
used in the workflow system.
"""

import os
import shutil
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import UploadFile
from loguru import logger


class FileStorageManager:
    """
    Manages file storage for uploaded documents.
    
    Handles:
    - File uploads and validation
    - Temporary file storage
    - File cleanup and expiration
    - File metadata tracking
    """
    
    def __init__(self, upload_dir: str = "uploads", max_file_size: int = 10 * 1024 * 1024):
        """
        Initialize file storage manager.
        
        Args:
            upload_dir: Directory to store uploaded files
            max_file_size: Maximum file size in bytes (default: 10MB)
        """
        self.upload_dir = Path(upload_dir)
        self.max_file_size = max_file_size
        self.supported_extensions = {'.txt', '.md', '.rst', '.pdf', '.docx', '.pptx'}
        
        # Create upload directory if it doesn't exist
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.upload_dir / "temp").mkdir(exist_ok=True)
        (self.upload_dir / "processed").mkdir(exist_ok=True)
        
        logger.info(f"File storage manager initialized with upload directory: {self.upload_dir}")

    async def save_uploaded_file(
        self,
        file: UploadFile,
        session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Save an uploaded file to temporary storage.
        
        Args:
            file: FastAPI UploadFile object
            session_id: Optional session ID for organization
            
        Returns:
            Dictionary with file information
            
        Raises:
            ValueError: If file is invalid or too large
            Exception: For other file handling errors
        """
        try:
            # Validate file
            await self._validate_file(file)
            
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_extension = Path(file.filename).suffix.lower() if file.filename else '.txt'
            
            if session_id:
                filename = f"{session_id}_{file_id}{file_extension}"
            else:
                filename = f"{file_id}{file_extension}"
            
            # Save file to temp directory
            temp_path = self.upload_dir / "temp" / filename
            
            with open(temp_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            # Get file metadata
            file_size = temp_path.stat().st_size
            upload_time = datetime.utcnow()
            
            file_info = {
                "file_id": file_id,
                "original_filename": file.filename,
                "stored_filename": filename,
                "file_path": str(temp_path),
                "file_size": file_size,
                "file_extension": file_extension,
                "content_type": file.content_type,
                "session_id": session_id,
                "upload_time": upload_time,
                "status": "uploaded"
            }
            
            logger.info(
                f"File uploaded successfully",
                extra={
                    "file_id": file_id,
                    "original_filename": file.filename,
                    "file_size": file_size,
                    "session_id": session_id
                }
            )
            
            return file_info
            
        except Exception as e:
            logger.error(
                f"Failed to save uploaded file: {str(e)}",
                extra={
                    "filename": file.filename,
                    "session_id": session_id,
                    "error": str(e)
                }
            )
            raise

    async def _validate_file(self, file: UploadFile) -> None:
        """
        Validate uploaded file.
        
        Args:
            file: FastAPI UploadFile object
            
        Raises:
            ValueError: If file is invalid
        """
        # Check if file has a name
        if not file.filename:
            raise ValueError("File must have a filename")
        
        # Check file extension
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in self.supported_extensions:
            raise ValueError(
                f"Unsupported file type: {file_extension}. "
                f"Supported types: {', '.join(self.supported_extensions)}"
            )
        
        # Check file size
        content = await file.read()
        file_size = len(content)
        
        if file_size > self.max_file_size:
            raise ValueError(
                f"File too large: {file_size} bytes. "
                f"Maximum size: {self.max_file_size} bytes"
            )
        
        if file_size == 0:
            raise ValueError("File is empty")
        
        # Reset file pointer
        await file.seek(0)

    def get_file_path(self, file_id: str, session_id: Optional[str] = None) -> Optional[str]:
        """
        Get the file path for a given file ID.
        
        Args:
            file_id: File ID
            session_id: Optional session ID
            
        Returns:
            File path if found, None otherwise
        """
        try:
            if session_id:
                pattern = f"{session_id}_{file_id}*"
            else:
                pattern = f"{file_id}*"
            
            # Search in temp directory
            temp_dir = self.upload_dir / "temp"
            for file_path in temp_dir.glob(pattern):
                if file_path.is_file():
                    return str(file_path)
            
            # Search in processed directory
            processed_dir = self.upload_dir / "processed"
            for file_path in processed_dir.glob(pattern):
                if file_path.is_file():
                    return str(file_path)
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting file path for {file_id}: {str(e)}")
            return None

    def move_to_processed(self, file_id: str, session_id: Optional[str] = None) -> bool:
        """
        Move file from temp to processed directory.
        
        Args:
            file_id: File ID
            session_id: Optional session ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            temp_path = self.get_file_path(file_id, session_id)
            if not temp_path:
                return False
            
            temp_path = Path(temp_path)
            if not temp_path.exists():
                return False
            
            # Create processed filename
            processed_filename = temp_path.name
            processed_path = self.upload_dir / "processed" / processed_filename
            
            # Move file
            shutil.move(str(temp_path), str(processed_path))
            
            logger.info(f"File moved to processed directory: {processed_filename}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to move file to processed: {str(e)}")
            return False

    def delete_file(self, file_id: str, session_id: Optional[str] = None) -> bool:
        """
        Delete a file from storage.
        
        Args:
            file_id: File ID
            session_id: Optional session ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.get_file_path(file_id, session_id)
            if not file_path:
                return False
            
            file_path = Path(file_path)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"File deleted: {file_path.name}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to delete file: {str(e)}")
            return False

    def cleanup_expired_files(self, max_age_hours: int = 24) -> int:
        """
        Clean up expired files from temp directory.
        
        Args:
            max_age_hours: Maximum age of files in hours
            
        Returns:
            Number of files cleaned up
        """
        try:
            temp_dir = self.upload_dir / "temp"
            if not temp_dir.exists():
                return 0
            
            cutoff_time = datetime.utcnow() - timedelta(hours=max_age_hours)
            cleaned_count = 0
            
            for file_path in temp_dir.iterdir():
                if file_path.is_file():
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_mtime < cutoff_time:
                        try:
                            file_path.unlink()
                            cleaned_count += 1
                            logger.debug(f"Cleaned up expired file: {file_path.name}")
                        except Exception as e:
                            logger.warning(f"Failed to delete expired file {file_path.name}: {str(e)}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} expired files")
            
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Error during file cleanup: {str(e)}")
            return 0

    def get_storage_stats(self) -> Dict[str, Any]:
        """
        Get storage statistics.
        
        Returns:
            Dictionary with storage statistics
        """
        try:
            temp_dir = self.upload_dir / "temp"
            processed_dir = self.upload_dir / "processed"
            
            temp_files = list(temp_dir.glob("*")) if temp_dir.exists() else []
            processed_files = list(processed_dir.glob("*")) if processed_dir.exists() else []
            
            temp_size = sum(f.stat().st_size for f in temp_files if f.is_file())
            processed_size = sum(f.stat().st_size for f in processed_files if f.is_file())
            
            return {
                "temp_files_count": len(temp_files),
                "processed_files_count": len(processed_files),
                "temp_size_bytes": temp_size,
                "processed_size_bytes": processed_size,
                "total_size_bytes": temp_size + processed_size,
                "upload_directory": str(self.upload_dir),
                "max_file_size": self.max_file_size,
                "supported_extensions": list(self.supported_extensions)
            }
            
        except Exception as e:
            logger.error(f"Error getting storage stats: {str(e)}")
            return {
                "error": str(e),
                "upload_directory": str(self.upload_dir)
            }

    def get_supported_extensions(self) -> list[str]:
        """
        Get list of supported file extensions.
        
        Returns:
            List of supported file extensions
        """
        return list(self.supported_extensions)


# Global file storage manager instance
file_storage = FileStorageManager()
