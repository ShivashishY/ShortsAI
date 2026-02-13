"""
File cleanup utilities for temporary storage management
"""

import os
import shutil
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


def cleanup_old_files(temp_dir: str, hours: int = 24) -> int:
    """
    Remove files and directories older than specified hours
    
    Args:
        temp_dir: Base temporary directory
        hours: Age threshold in hours (0 means delete all)
        
    Returns:
        Number of items deleted
    """
    deleted_count = 0
    
    if not os.path.exists(temp_dir):
        return 0
    
    threshold = datetime.utcnow() - timedelta(hours=hours)
    
    # Clean downloads directory
    downloads_dir = os.path.join(temp_dir, "downloads")
    if os.path.exists(downloads_dir):
        for filename in os.listdir(downloads_dir):
            filepath = os.path.join(downloads_dir, filename)
            try:
                file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
                if hours == 0 or file_time < threshold:
                    os.remove(filepath)
                    deleted_count += 1
                    logger.info(f"Deleted old download: {filename}")
            except Exception as e:
                logger.error(f"Error deleting {filepath}: {e}")
    
    # Clean outputs directory
    outputs_dir = os.path.join(temp_dir, "outputs")
    if os.path.exists(outputs_dir):
        for job_id in os.listdir(outputs_dir):
            job_dir = os.path.join(outputs_dir, job_id)
            try:
                if os.path.isdir(job_dir):
                    dir_time = datetime.fromtimestamp(os.path.getmtime(job_dir))
                    if hours == 0 or dir_time < threshold:
                        shutil.rmtree(job_dir)
                        deleted_count += 1
                        logger.info(f"Deleted old job directory: {job_id}")
            except Exception as e:
                logger.error(f"Error deleting {job_dir}: {e}")
    
    return deleted_count


def get_storage_usage(temp_dir: str) -> dict:
    """
    Get storage usage statistics for temporary directory
    
    Args:
        temp_dir: Base temporary directory
        
    Returns:
        Dictionary with storage statistics
    """
    total_size = 0
    file_count = 0
    
    for dirpath, dirnames, filenames in os.walk(temp_dir):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
                file_count += 1
            except:
                pass
    
    return {
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "file_count": file_count
    }


def ensure_temp_directories(temp_dir: str):
    """
    Ensure all required temporary directories exist
    
    Args:
        temp_dir: Base temporary directory
    """
    directories = [
        temp_dir,
        os.path.join(temp_dir, "downloads"),
        os.path.join(temp_dir, "outputs"),
        os.path.join(temp_dir, "cache")
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
