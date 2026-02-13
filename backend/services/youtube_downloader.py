"""
YouTube video downloader service using yt-dlp
"""

import os
import asyncio
import logging
from typing import Optional, Dict
import yt_dlp

logger = logging.getLogger(__name__)


class YouTubeDownloader:
    """
    Service for downloading YouTube videos using yt-dlp
    """
    
    def __init__(self, temp_dir: str):
        """
        Initialize the downloader
        
        Args:
            temp_dir: Base directory for temporary files
        """
        self.temp_dir = temp_dir
        self.downloads_dir = os.path.join(temp_dir, "downloads")
        os.makedirs(self.downloads_dir, exist_ok=True)
    
    async def download(
        self, 
        url: str, 
        output_path: str, 
        max_duration: int = 1800
    ) -> Optional[Dict]:
        """
        Download a YouTube video
        
        Args:
            url: YouTube video URL
            output_path: Path to save the downloaded video
            max_duration: Maximum allowed video duration in seconds
            
        Returns:
            Dictionary with video info or None if failed
        """
        try:
            # First, get video info without downloading
            info = await self._get_video_info(url)
            
            if not info:
                logger.error("Failed to get video info")
                return None
            
            # Check duration
            duration = info.get('duration', 0)
            if duration > max_duration:
                logger.error(f"Video too long: {duration}s > {max_duration}s")
                raise ValueError(f"Video is too long ({duration}s). Maximum allowed is {max_duration}s ({max_duration//60} minutes)")
            
            # Check if video is available
            if info.get('is_live'):
                raise ValueError("Cannot process live streams")
            
            # Download the video
            await self._download_video(url, output_path)
            
            if not os.path.exists(output_path):
                logger.error("Download completed but file not found")
                return None
            
            return {
                'title': info.get('title', 'Unknown'),
                'duration': duration,
                'thumbnail': info.get('thumbnail'),
                'channel': info.get('channel', 'Unknown'),
                'view_count': info.get('view_count', 0),
                'upload_date': info.get('upload_date'),
                'path': output_path
            }
            
        except Exception as e:
            logger.error(f"Download error: {e}")
            raise
    
    async def _get_video_info(self, url: str) -> Optional[Dict]:
        """
        Get video information without downloading
        
        Args:
            url: YouTube video URL
            
        Returns:
            Video info dictionary or None
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        def extract():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(None, extract)
        
        return info
    
    async def _download_video(self, url: str, output_path: str):
        """
        Download video with best quality settings
        
        Args:
            url: YouTube video URL
            output_path: Path to save the video
        """
        # Remove extension from output path for yt-dlp
        output_template = output_path.rsplit('.', 1)[0]
        
        ydl_opts = {
            'format': 'bestvideo[ext=mp4][height<=1080]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'outtmpl': output_template + '.%(ext)s',
            'merge_output_format': 'mp4',
            'quiet': True,
            'no_warnings': True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
            # Add these options for better compatibility
            'writesubtitles': False,
            'writeautomaticsub': False,
            'noplaylist': True,
        }
        
        def download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, download)
        
        # Rename if extension is different
        expected_path = output_template + '.mp4'
        if os.path.exists(expected_path) and expected_path != output_path:
            os.rename(expected_path, output_path)
    
    async def get_thumbnail(self, url: str) -> Optional[str]:
        """
        Get thumbnail URL for a video
        
        Args:
            url: YouTube video URL
            
        Returns:
            Thumbnail URL or None
        """
        info = await self._get_video_info(url)
        if info:
            return info.get('thumbnail')
        return None
    
    def cleanup_download(self, filepath: str) -> bool:
        """
        Remove a downloaded file
        
        Args:
            filepath: Path to the file to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
        except Exception as e:
            logger.error(f"Cleanup error: {e}")
        return False
