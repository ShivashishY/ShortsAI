"""
Video processing service for creating short-form vertical clips
Uses FFmpeg for video manipulation
"""

import os
import asyncio
import subprocess
import logging
from typing import Dict, Optional, Tuple
import json

logger = logging.getLogger(__name__)


class VideoProcessor:
    """
    Service for processing videos into short-form clips
    - Extracts segments at specified timestamps
    - Converts to vertical 9:16 aspect ratio
    - Optimizes for mobile playback
    """
    
    # Output dimensions for vertical video (9:16 aspect ratio)
    OUTPUT_WIDTH = 1080
    OUTPUT_HEIGHT = 1920
    
    # Alternative lower resolution
    OUTPUT_WIDTH_LOW = 720
    OUTPUT_HEIGHT_LOW = 1280
    
    def __init__(self, temp_dir: str, high_quality: bool = True):
        """
        Initialize video processor
        
        Args:
            temp_dir: Base directory for temporary files
            high_quality: Use 1080x1920 (True) or 720x1280 (False)
        """
        self.temp_dir = temp_dir
        
        if high_quality:
            self.width = self.OUTPUT_WIDTH
            self.height = self.OUTPUT_HEIGHT
        else:
            self.width = self.OUTPUT_WIDTH_LOW
            self.height = self.OUTPUT_HEIGHT_LOW
    
    async def create_short(
        self,
        input_path: str,
        output_path: str,
        start_time: float,
        duration: int,
        score: float = 0
    ) -> Optional[Dict]:
        """
        Create a short-form clip from input video
        
        Args:
            input_path: Path to input video
            output_path: Path for output clip
            start_time: Start time in seconds
            duration: Duration in seconds
            score: Engagement score for metadata
            
        Returns:
            Clip info dictionary or None if failed
        """
        try:
            # Get input video dimensions
            input_info = await self._get_video_info(input_path)
            if not input_info:
                logger.error("Failed to get input video info")
                return None
            
            input_width = input_info['width']
            input_height = input_info['height']
            
            # Calculate crop/scale parameters for 9:16 output
            filter_complex = self._build_filter(input_width, input_height)
            
            # Build FFmpeg command
            cmd = [
                'ffmpeg',
                '-y',  # Overwrite output
                '-ss', str(start_time),  # Seek before input (faster)
                '-i', input_path,
                '-t', str(duration),
                '-vf', filter_complex,
                '-c:v', 'libx264',
                '-preset', 'medium',
                '-crf', '23',  # Good quality
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',  # Enable streaming
                '-pix_fmt', 'yuv420p',  # Compatibility
                output_path
            ]
            
            # Run FFmpeg
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._run_ffmpeg, cmd)
            
            if not result:
                logger.error("FFmpeg processing failed")
                return None
            
            # Verify output exists
            if not os.path.exists(output_path):
                logger.error("Output file not created")
                return None
            
            # Get output file info
            output_info = await self._get_video_info(output_path)
            file_size = os.path.getsize(output_path)
            
            return {
                'path': output_path,
                'start_time': start_time,
                'duration': duration,
                'score': score,
                'width': output_info.get('width', self.width),
                'height': output_info.get('height', self.height),
                'file_size': file_size,
                'file_size_mb': round(file_size / (1024 * 1024), 2)
            }
            
        except Exception as e:
            logger.error(f"Error creating short: {e}")
            return None
    
    def _build_filter(self, input_width: int, input_height: int) -> str:
        """
        Build FFmpeg filter string for cropping/scaling to 9:16
        
        Strategy:
        1. If input is wider than 9:16, crop sides and center
        2. If input is taller than 9:16, crop top/bottom (keeps center)
        3. Scale to output dimensions
        """
        input_ratio = input_width / input_height
        output_ratio = 9 / 16  # 0.5625
        
        if input_ratio > output_ratio:
            # Input is wider - crop sides (common case for landscape videos)
            # Calculate new width to match 9:16 ratio
            new_width = int(input_height * output_ratio)
            crop_x = (input_width - new_width) // 2
            filter_str = f"crop={new_width}:{input_height}:{crop_x}:0,scale={self.width}:{self.height}"
        else:
            # Input is taller - crop top/bottom
            new_height = int(input_width / output_ratio)
            crop_y = (input_height - new_height) // 2
            filter_str = f"crop={input_width}:{new_height}:0:{crop_y},scale={self.width}:{self.height}"
        
        return filter_str
    
    def _run_ffmpeg(self, cmd: list) -> bool:
        """
        Run FFmpeg command
        
        Args:
            cmd: FFmpeg command as list
            
        Returns:
            True if successful
        """
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode != 0:
                logger.error(f"FFmpeg error: {result.stderr}")
                return False
            
            return True
            
        except subprocess.TimeoutExpired:
            logger.error("FFmpeg timeout")
            return False
        except Exception as e:
            logger.error(f"FFmpeg exception: {e}")
            return False
    
    async def _get_video_info(self, video_path: str) -> Optional[Dict]:
        """
        Get video information using ffprobe
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary with video info
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'quiet',
                '-print_format', 'json',
                '-show_format',
                '-show_streams',
                video_path
            ]
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(cmd, capture_output=True, text=True)
            )
            
            if result.returncode != 0:
                return None
            
            data = json.loads(result.stdout)
            
            # Find video stream
            for stream in data.get('streams', []):
                if stream.get('codec_type') == 'video':
                    return {
                        'width': stream.get('width', 0),
                        'height': stream.get('height', 0),
                        'fps': eval(stream.get('r_frame_rate', '30/1')),
                        'duration': float(data.get('format', {}).get('duration', 0)),
                        'codec': stream.get('codec_name', 'unknown')
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None
    
    async def add_captions(
        self,
        video_path: str,
        output_path: str,
        captions: list
    ) -> bool:
        """
        Add captions/subtitles to video (optional feature)
        
        Args:
            video_path: Input video path
            output_path: Output video path
            captions: List of caption dictionaries with text, start, end
            
        Returns:
            True if successful
        """
        # This would use FFmpeg drawtext or ASS subtitles
        # Implementation depends on caption format requirements
        pass
    
    async def create_thumbnail(
        self,
        video_path: str,
        output_path: str,
        time_offset: float = 0.5
    ) -> bool:
        """
        Extract thumbnail from video
        
        Args:
            video_path: Input video path
            output_path: Output image path
            time_offset: Time in seconds to extract thumbnail
            
        Returns:
            True if successful
        """
        try:
            cmd = [
                'ffmpeg',
                '-y',
                '-ss', str(time_offset),
                '-i', video_path,
                '-vframes', '1',
                '-vf', f'scale={self.width}:{self.height}',
                output_path
            ]
            
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._run_ffmpeg, cmd)
            
            return result and os.path.exists(output_path)
            
        except Exception as e:
            logger.error(f"Error creating thumbnail: {e}")
            return False
    
    async def compress_video(
        self,
        input_path: str,
        output_path: str,
        target_size_mb: float = 10
    ) -> bool:
        """
        Compress video to target file size
        
        Args:
            input_path: Input video path
            output_path: Output video path
            target_size_mb: Target file size in MB
            
        Returns:
            True if successful
        """
        try:
            # Get video duration
            info = await self._get_video_info(input_path)
            if not info:
                return False
            
            duration = info['duration']
            
            # Calculate target bitrate (bits per second)
            # Reserve 128kbps for audio
            target_bits = target_size_mb * 8 * 1024 * 1024
            audio_bits = 128 * 1024 * duration
            video_bitrate = int((target_bits - audio_bits) / duration)
            
            # Minimum video bitrate
            video_bitrate = max(video_bitrate, 500000)  # 500kbps minimum
            
            cmd = [
                'ffmpeg',
                '-y',
                '-i', input_path,
                '-c:v', 'libx264',
                '-b:v', str(video_bitrate),
                '-maxrate', str(int(video_bitrate * 1.5)),
                '-bufsize', str(int(video_bitrate * 2)),
                '-c:a', 'aac',
                '-b:a', '128k',
                '-movflags', '+faststart',
                output_path
            ]
            
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._run_ffmpeg, cmd)
            
        except Exception as e:
            logger.error(f"Error compressing video: {e}")
            return False
