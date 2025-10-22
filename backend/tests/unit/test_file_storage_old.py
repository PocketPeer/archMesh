"""
Unit tests for the File Storage module.

This module tests the FileStorageManager functionality including:
- File upload and validation
- File storage and retrieval
- File cleanup and expiration
- File metadata tracking
- Error handling
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta
import uuid

from app.core.file_storage import FileStorageManager


class TestFileStorageManager:
    """Test cases for the FileStorageManager class."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def file_storage_manager(self, temp_dir):
        """Create a FileStorageManager instance for testing."""
        return FileStorageManager(upload_dir=temp_dir, max_file_size=1024 * 1024)  # 1MB

    @pytest.fixture
    def mock_upload_file(self):
        """Create a mock UploadFile for testing."""
        mock_file = Mock()
        mock_file.filename = "test.txt"
        mock_file.content_type = "text/plain"
        mock_file.size = 100
        mock_file.read = AsyncMock(return_value=b"Test file content")
        mock_file.seek = AsyncMock()  # Add seek method as AsyncMock
        return mock_file

    def test_initialization(self, temp_dir):
        """Test FileStorageManager initialization."""
        manager = FileStorageManager(upload_dir=temp_dir, max_file_size=2048)
        
        assert manager.upload_dir == Path(temp_dir)
        assert manager.max_file_size == 2048
        assert manager.supported_extensions == {'.txt', '.md', '.rst', '.pdf', '.docx', '.pptx'}
        
        # Check that directories were created
        assert (Path(temp_dir) / "temp").exists()
        assert (Path(temp_dir) / "processed").exists()

    def test_initialization_with_defaults(self, temp_dir):
        """Test FileStorageManager initialization with default values."""
        manager = FileStorageManager()
        
        assert manager.upload_dir == Path("uploads")
        assert manager.max_file_size == 10 * 1024 * 1024  # 10MB
        assert manager.supported_extensions == {'.txt', '.md', '.rst', '.pdf', '.docx', '.pptx'}

    @pytest.mark.asyncio
    async def test_save_uploaded_file_success(self, file_storage_manager, mock_upload_file):
        """Test successful file upload and save."""
        result = await file_storage_manager.save_uploaded_file(mock_upload_file, "test-project")
        
        assert "file_id" in result
        assert "file_path" in result
        assert "original_filename" in result
        assert "file_size" in result
        assert "project_id" in result
        assert "uploaded_at" in result
        
        assert result["original_filename"] == "test.txt"
        assert result["file_size"] == 100
        assert result["project_id"] == "test-project"
        
        # Check that file was actually saved
        file_path = Path(result["file_path"])
        assert file_path.exists()
        assert file_path.read_text() == "Test file content"

    @pytest.mark.asyncio
    async def test_save_uploaded_file_without_project(self, file_storage_manager, mock_upload_file):
        """Test file upload without project ID."""
        result = await file_storage_manager.save_uploaded_file(mock_upload_file, None)
        
        assert result["project_id"] is None

    @pytest.mark.asyncio
    async def test_save_uploaded_file_invalid_extension(self, file_storage_manager):
        """Test file upload with invalid extension."""
        mock_file = Mock()
        mock_file.filename = "test.exe"
        mock_file.content_type = "application/octet-stream"
        mock_file.size = 100
        mock_file.read = AsyncMock(return_value=b"Test content")
        
        with pytest.raises(ValueError, match="Unsupported file type"):
            await file_storage_manager.save_uploaded_file(mock_file, "test-project")

    @pytest.mark.asyncio
    async def test_save_uploaded_file_no_filename(self, file_storage_manager):
        """Test file upload without filename."""
        mock_file = Mock()
        mock_file.filename = None
        mock_file.content_type = "text/plain"
        mock_file.size = 100
        mock_file.read = AsyncMock(return_value=b"Test content")
        
        with pytest.raises(ValueError, match="File must have a filename"):
            await file_storage_manager.save_uploaded_file(mock_file, "test-project")

    @pytest.mark.asyncio
    async def test_save_uploaded_file_too_large(self, temp_dir):
        """Test file upload with file too large."""
        manager = FileStorageManager(upload_dir=temp_dir, max_file_size=50)  # 50 bytes max
        
        mock_file = Mock()
        mock_file.filename = "test.txt"
        mock_file.content_type = "text/plain"
        mock_file.size = 100  # Larger than 50 bytes
        mock_file.read = AsyncMock(return_value=b"x" * 100)
        
        with pytest.raises(ValueError, match="File too large"):
            await manager.save_uploaded_file(mock_file, "test-project")

    @pytest.mark.asyncio
    async def test_save_uploaded_file_read_error(self, file_storage_manager):
        """Test file upload with read error."""
        mock_file = Mock()
        mock_file.filename = "test.txt"
        mock_file.content_type = "text/plain"
        mock_file.size = 100
        mock_file.read = AsyncMock(side_effect=Exception("Read error"))
        
        with pytest.raises(Exception, match="Read error"):
            await file_storage_manager.save_uploaded_file(mock_file, "test-project")


    def test_get_file_path_nonexistent_file(self, file_storage_manager):
        """Test getting file path for non-existent file."""
        result = file_storage_manager.get_file_path("nonexistent-id")
        assert result is None

    def test_get_file_path_existing_file(self, file_storage_manager, temp_dir):
        """Test getting file path for existing file."""
        # Create a test file
        test_file_id = str(uuid.uuid4())
        test_file_path = file_storage_manager.upload_dir / "temp" / f"{test_file_id}.txt"
        test_file_path.write_text("Test content")
        
        result = file_storage_manager.get_file_path(test_file_id)
        
        assert result is not None
        assert result == str(test_file_path)

    def test_get_file_path_nonexistent_file(self, file_storage_manager):
        """Test getting file path for non-existent file."""
        result = file_storage_manager.get_file_path("nonexistent-id")
        assert result is None

    def test_move_to_processed_success(self, file_storage_manager, temp_dir):
        """Test moving file to processed directory."""
        # Create a test file
        test_file_id = str(uuid.uuid4())
        test_file_path = file_storage_manager.upload_dir / "temp" / f"{test_file_id}.txt"
        test_file_path.write_text("Test content")
        
        # Create metadata file
        metadata = {
            "file_id": test_file_id,
            "original_filename": "test.txt",
            "file_size": 12,
            "project_id": "test-project",
            "uploaded_at": datetime.utcnow().isoformat()
        }
        metadata_path = file_storage_manager.upload_dir / "temp" / f"{test_file_id}.json"
        import json
        metadata_path.write_text(json.dumps(metadata))
        
        result = file_storage_manager.move_to_processed(test_file_id)
        
        assert result is True
        
        # Check that file was moved
        processed_file_path = file_storage_manager.upload_dir / "processed" / f"{test_file_id}.txt"
        assert processed_file_path.exists()
        assert not test_file_path.exists()
        
        # Check that metadata was moved
        processed_metadata_path = file_storage_manager.upload_dir / "processed" / f"{test_file_id}.json"
        assert processed_metadata_path.exists()
        assert not metadata_path.exists()

    def test_move_to_processed_nonexistent_file(self, file_storage_manager):
        """Test moving non-existent file to processed directory."""
        result = file_storage_manager.move_to_processed("nonexistent-id")
        assert result is False

    def test_delete_file_success(self, file_storage_manager, temp_dir):
        """Test deleting file successfully."""
        # Create a test file
        test_file_id = str(uuid.uuid4())
        test_file_path = file_storage_manager.upload_dir / "temp" / f"{test_file_id}.txt"
        test_file_path.write_text("Test content")
        
        # Create metadata file
        metadata = {
            "file_id": test_file_id,
            "original_filename": "test.txt",
            "file_size": 12,
            "project_id": "test-project",
            "uploaded_at": datetime.utcnow().isoformat()
        }
        metadata_path = file_storage_manager.upload_dir / "temp" / f"{test_file_id}.json"
        import json
        metadata_path.write_text(json.dumps(metadata))
        
        result = file_storage_manager.delete_file(test_file_id)
        
        assert result is True
        assert not test_file_path.exists()
        assert not metadata_path.exists()

    def test_delete_file_nonexistent_file(self, file_storage_manager):
        """Test deleting non-existent file."""
        result = file_storage_manager.delete_file("nonexistent-id")
        assert result is False

    def test_cleanup_expired_files(self, file_storage_manager, temp_dir):
        """Test cleaning up expired files."""
        # Create an expired file
        expired_file_id = str(uuid.uuid4())
        expired_file_path = file_storage_manager.upload_dir / "temp" / f"{expired_file_id}.txt"
        expired_file_path.write_text("Expired content")
        
        # Create expired metadata
        expired_metadata = {
            "file_id": expired_file_id,
            "original_filename": "expired.txt",
            "file_size": 15,
            "project_id": "test-project",
            "uploaded_at": (datetime.utcnow() - timedelta(hours=25)).isoformat()  # 25 hours ago
        }
        expired_metadata_path = file_storage_manager.upload_dir / "temp" / f"{expired_file_id}.json"
        import json
        expired_metadata_path.write_text(json.dumps(expired_metadata))
        
        # Create a non-expired file
        current_file_id = str(uuid.uuid4())
        current_file_path = file_storage_manager.upload_dir / "temp" / f"{current_file_id}.txt"
        current_file_path.write_text("Current content")
        
        current_metadata = {
            "file_id": current_file_id,
            "original_filename": "current.txt",
            "file_size": 14,
            "project_id": "test-project",
            "uploaded_at": datetime.utcnow().isoformat()  # Now
        }
        current_metadata_path = file_storage_manager.upload_dir / "temp" / f"{current_file_id}.json"
        current_metadata_path.write_text(json.dumps(current_metadata))
        
        # Run cleanup
        result = file_storage_manager.cleanup_expired_files()

        assert result == 1
        
        # Check that expired file was deleted
        assert not expired_file_path.exists()
        
        # Check that current file still exists
        assert current_file_path.exists()
        assert current_metadata_path.exists()

    def test_cleanup_expired_files_no_expired_files(self, file_storage_manager, temp_dir):
        """Test cleanup when no files are expired."""
        # Create a current file
        current_file_id = str(uuid.uuid4())
        current_file_path = file_storage_manager.upload_dir / "temp" / f"{current_file_id}.txt"
        current_file_path.write_text("Current content")
        
        current_metadata = {
            "file_id": current_file_id,
            "original_filename": "current.txt",
            "file_size": 14,
            "project_id": "test-project",
            "uploaded_at": datetime.utcnow().isoformat()
        }
        current_metadata_path = file_storage_manager.upload_dir / "temp" / f"{current_file_id}.json"
        import json
        current_metadata_path.write_text(json.dumps(current_metadata))
        
        # Run cleanup
        result = file_storage_manager.cleanup_expired_files()

        assert result == 0
        
        # Check that current file still exists
        assert current_file_path.exists()


    def test_get_storage_stats(self, file_storage_manager, temp_dir):
        """Test getting storage statistics."""
        # Create test files
        test_file_id1 = str(uuid.uuid4())
        test_file_id2 = str(uuid.uuid4())
        
        test_file_path1 = file_storage_manager.upload_dir / "temp" / f"{test_file_id1}.txt"
        test_file_path2 = file_storage_manager.upload_dir / "processed" / f"{test_file_id2}.txt"
        
        test_file_path1.write_text("Content 1")
        test_file_path2.write_text("Content 2")
        
        # Create metadata files
        metadata1 = {
            "file_id": test_file_id1,
            "original_filename": "test1.txt",
            "file_size": 9,
            "project_id": "project1",
            "uploaded_at": datetime.utcnow().isoformat()
        }
        metadata2 = {
            "file_id": test_file_id2,
            "original_filename": "test2.txt",
            "file_size": 9,
            "project_id": "project2",
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
        metadata_path1 = file_storage_manager.upload_dir / "temp" / f"{test_file_id1}.json"
        metadata_path2 = file_storage_manager.upload_dir / "processed" / f"{test_file_id2}.json"
        
        import json
        metadata_path1.write_text(json.dumps(metadata1))
        metadata_path2.write_text(json.dumps(metadata2))
        
        # Get stats
        result = file_storage_manager.get_storage_stats()
        
        assert "temp_files_count" in result
        assert "total_size_bytes" in result
        assert "processed_files_count" in result
        assert "temp_size_bytes" in result
        assert "processed_size_bytes" in result
        
        assert result["temp_files_count"] == 1
        assert result["processed_files_count"] == 1
        assert result["total_size_bytes"] == 18
        assert result["temp_size_bytes"] == 9
        assert result["processed_size_bytes"] == 9

    def test_get_storage_stats_empty(self, file_storage_manager):
        """Test getting storage statistics for empty storage."""
        result = file_storage_manager.get_storage_stats()

        assert result["temp_files_count"] == 0
        assert result["processed_files_count"] == 0
        assert result["total_size_bytes"] == 0

    @pytest.mark.asyncio
    async def test_validate_file_success(self, file_storage_manager, mock_upload_file):
        """Test successful file validation."""
        # This should not raise an exception
        await file_storage_manager._validate_file(mock_upload_file)

    @pytest.mark.asyncio
    async def test_validate_file_no_filename(self, file_storage_manager):
        """Test file validation with no filename."""
        mock_file = Mock()
        mock_file.filename = None
        
        with pytest.raises(ValueError, match="File must have a filename"):
            await file_storage_manager._validate_file(mock_file)

    @pytest.mark.asyncio
    async def test_validate_file_invalid_extension(self, file_storage_manager):
        """Test file validation with invalid extension."""
        mock_file = Mock()
        mock_file.filename = "test.exe"
        
        with pytest.raises(ValueError, match="Unsupported file type"):
            await file_storage_manager._validate_file(mock_file)

    @pytest.mark.asyncio
    async def test_validate_file_too_large(self, temp_dir):
        """Test file validation with file too large."""
        manager = FileStorageManager(upload_dir=temp_dir, max_file_size=50)
        
        mock_file = Mock()
        mock_file.filename = "test.txt"
        mock_file.read = AsyncMock(return_value=b"x" * 100)
        
        with pytest.raises(ValueError, match="File too large"):
            await manager._validate_file(mock_file)


    def test_get_file_extension(self, file_storage_manager):
        """Test file extension extraction."""
        assert file_storage_manager._get_file_extension("test.txt") == ".txt"
        assert file_storage_manager._get_file_extension("document.pdf") == ".pdf"
        assert file_storage_manager._get_file_extension("README.md") == ".md"
        assert file_storage_manager._get_file_extension("noextension") == ""
        assert file_storage_manager._get_file_extension("") == ""

    def test_is_file_expired(self, file_storage_manager):
        """Test file expiration check."""
        # Test expired file (25 hours ago)
        expired_time = datetime.utcnow() - timedelta(hours=25)
        assert file_storage_manager._is_file_expired(expired_time) is True
        
        # Test current file (1 hour ago)
        current_time = datetime.utcnow() - timedelta(hours=1)
        assert file_storage_manager._is_file_expired(current_time) is False
        
        # Test future file (should not be expired)
        future_time = datetime.utcnow() + timedelta(hours=1)
        assert file_storage_manager._is_file_expired(future_time) is False

    def test_get_metadata_path(self, file_storage_manager):
        """Test metadata path generation."""
        file_id = "test-file-id"
        expected_path = file_storage_manager.upload_dir / "temp" / f"{file_id}.json"
        
        result = file_storage_manager._get_metadata_path(file_id, "temp")
        assert result == expected_path

    def test_save_metadata(self, file_storage_manager, temp_dir):
        """Test metadata saving."""
        file_id = "test-file-id"
        metadata = {
            "file_id": file_id,
            "original_filename": "test.txt",
            "file_size": 100,
            "project_id": "test-project",
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
        result = file_storage_manager._save_metadata(file_id, metadata, "temp")
        
        assert result is True
        
        # Check that metadata file was created
        metadata_path = file_storage_manager.upload_dir / "temp" / f"{file_id}.json"
        assert metadata_path.exists()
        
        # Check content
        import json
        saved_metadata = json.loads(metadata_path.read_text())
        assert saved_metadata == metadata

    def test_load_metadata(self, file_storage_manager, temp_dir):
        """Test metadata loading."""
        file_id = "test-file-id"
        metadata = {
            "file_id": file_id,
            "original_filename": "test.txt",
            "file_size": 100,
            "project_id": "test-project",
            "uploaded_at": datetime.utcnow().isoformat()
        }
        
        # Save metadata first
        file_storage_manager._save_metadata(file_id, metadata, "temp")
        
        # Load metadata
        result = file_storage_manager._load_metadata(file_id, "temp")
        
        assert result == metadata

    def test_load_metadata_nonexistent(self, file_storage_manager):
        """Test loading non-existent metadata."""
        result = file_storage_manager._load_metadata("nonexistent-id", "temp")
        assert result is None

    def test_load_metadata_invalid_json(self, file_storage_manager, temp_dir):
        """Test loading metadata with invalid JSON."""
        file_id = "test-file-id"
        metadata_path = file_storage_manager.upload_dir / "temp" / f"{file_id}.json"
        metadata_path.write_text("invalid json content")
        
        result = file_storage_manager._load_metadata(file_id, "temp")
        assert result is None


class TestFileStorageManagerEdgeCases:
    """Test edge cases and error conditions for FileStorageManager."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def file_storage_manager(self, temp_dir):
        """Create a FileStorageManager instance for testing."""
        return FileStorageManager(upload_dir=temp_dir, max_file_size=1024)

    def test_initialization_with_nonexistent_parent_directory(self, temp_dir):
        """Test initialization with non-existent parent directory."""
        nonexistent_dir = Path(temp_dir) / "nonexistent" / "uploads"
        
        # This should create the directory structure
        manager = FileStorageManager(upload_dir=str(nonexistent_dir))
        
        assert manager.upload_dir == nonexistent_dir
        assert nonexistent_dir.exists()
        assert (nonexistent_dir / "temp").exists()
        assert (nonexistent_dir / "processed").exists()

    def test_initialization_with_file_instead_of_directory(self, temp_dir):
        """Test initialization when upload_dir is a file instead of directory."""
        file_path = Path(temp_dir) / "not_a_directory"
        file_path.write_text("This is a file")
        
        # This should raise an exception or handle gracefully
        with pytest.raises((OSError, FileExistsError)):
            FileStorageManager(upload_dir=str(file_path))

    @pytest.mark.asyncio
    async def test_save_uploaded_file_with_special_characters_in_filename(self, file_storage_manager):
        """Test file upload with special characters in filename."""
        mock_file = Mock()
        mock_file.filename = "test file with spaces & symbols!.txt"
        mock_file.content_type = "text/plain"
        mock_file.size = 100
        mock_file.read = AsyncMock(return_value=b"Test content")
        
        result = await file_storage_manager.save_uploaded_file(mock_file, "test-project")
        
        assert result["original_filename"] == "test file with spaces & symbols!.txt"
        assert "file_id" in result

    @pytest.mark.asyncio
    async def test_save_uploaded_file_with_very_long_filename(self, file_storage_manager):
        """Test file upload with very long filename."""
        long_filename = "a" * 255 + ".txt"  # Very long filename
        
        mock_file = Mock()
        mock_file.filename = long_filename
        mock_file.content_type = "text/plain"
        mock_file.size = 100
        mock_file.read = AsyncMock(return_value=b"Test content")
        
        result = await file_storage_manager.save_uploaded_file(mock_file, "test-project")
        
        assert result["original_filename"] == long_filename
        assert "file_id" in result

    def test_move_to_processed_with_missing_metadata(self, file_storage_manager, temp_dir):
        """Test moving file to processed when metadata is missing."""
        # Create a test file without metadata
        test_file_id = str(uuid.uuid4())
        test_file_path = file_storage_manager.upload_dir / "temp" / f"{test_file_id}.txt"
        test_file_path.write_text("Test content")
        
        result = file_storage_manager.move_to_processed(test_file_id)
        
        # Should handle gracefully
        assert result is False

    def test_delete_file_with_missing_metadata(self, file_storage_manager, temp_dir):
        """Test deleting file when metadata is missing."""
        # Create a test file without metadata
        test_file_id = str(uuid.uuid4())
        test_file_path = file_storage_manager.upload_dir / "temp" / f"{test_file_id}.txt"
        test_file_path.write_text("Test content")
        
        result = file_storage_manager.delete_file(test_file_id)
        
        # Should still delete the file
        assert result is True
        assert not test_file_path.exists()

    def test_cleanup_with_corrupted_metadata(self, file_storage_manager, temp_dir):
        """Test cleanup with corrupted metadata files."""
        # Create a test file with corrupted metadata
        test_file_id = str(uuid.uuid4())
        test_file_path = file_storage_manager.upload_dir / "temp" / f"{test_file_id}.txt"
        test_file_path.write_text("Test content")
        
        # Create corrupted metadata
        metadata_path = file_storage_manager.upload_dir / "temp" / f"{test_file_id}.json"
        metadata_path.write_text("corrupted json content")
        
        # Run cleanup - should handle gracefully
        result = file_storage_manager.cleanup_expired_files()
        
        # Should not crash and should return valid result
        assert "deleted_count" in result
        assert "deleted_files" in result

    def test_concurrent_file_operations(self, file_storage_manager, temp_dir):
        """Test concurrent file operations."""
        import threading
        import time
        
        results = []
        
        def create_file(file_id):
            test_file_path = file_storage_manager.upload_dir / "temp" / f"{file_id}.txt"
            test_file_path.write_text(f"Content for {file_id}")
            
            metadata = {
                "file_id": file_id,
                "original_filename": f"{file_id}.txt",
                "file_size": len(f"Content for {file_id}"),
                "project_id": "test-project",
                "uploaded_at": datetime.utcnow().isoformat()
            }
            
            metadata_path = file_storage_manager.upload_dir / "temp" / f"{file_id}.json"
            import json
            metadata_path.write_text(json.dumps(metadata))
            
            results.append(file_id)
        
        # Create multiple files concurrently
        threads = []
        for i in range(5):
            file_id = f"concurrent-test-{i}"
            thread = threading.Thread(target=create_file, args=(file_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check that all files were created
        assert len(results) == 5
        
        # List files to verify they all exist
        file_list = file_storage_manager.list_files("temp")
        assert len(file_list) == 5
