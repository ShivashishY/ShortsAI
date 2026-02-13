"""
URL validation and utility functions
"""

import re
from urllib.parse import urlparse, parse_qs


# YouTube URL patterns
YOUTUBE_PATTERNS = [
    r'(?:https?://)?(?:www\.)?youtube\.com/watch\?v=([a-zA-Z0-9_-]{11})',
    r'(?:https?://)?(?:www\.)?youtube\.com/embed/([a-zA-Z0-9_-]{11})',
    r'(?:https?://)?(?:www\.)?youtube\.com/v/([a-zA-Z0-9_-]{11})',
    r'(?:https?://)?youtu\.be/([a-zA-Z0-9_-]{11})',
    r'(?:https?://)?(?:www\.)?youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
]


def validate_youtube_url(url: str) -> bool:
    """
    Validate if the given URL is a valid YouTube video URL
    
    Args:
        url: The URL to validate
        
    Returns:
        True if valid YouTube URL, False otherwise
    """
    if not url:
        return False
    
    for pattern in YOUTUBE_PATTERNS:
        if re.match(pattern, url):
            return True
    
    return False


def extract_video_id(url: str) -> str:
    """
    Extract the video ID from a YouTube URL
    
    Args:
        url: The YouTube URL
        
    Returns:
        The video ID or None if not found
    """
    if not url:
        return None
    
    # Try each pattern
    for pattern in YOUTUBE_PATTERNS:
        match = re.match(pattern, url)
        if match:
            return match.group(1)
    
    # Try parsing as URL with query string
    try:
        parsed = urlparse(url)
        if 'youtube.com' in parsed.netloc or 'youtu.be' in parsed.netloc:
            # Check query parameters
            query_params = parse_qs(parsed.query)
            if 'v' in query_params:
                video_id = query_params['v'][0]
                if len(video_id) == 11:
                    return video_id
    except:
        pass
    
    return None


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing invalid characters
    
    Args:
        filename: The filename to sanitize
        
    Returns:
        Sanitized filename
    """
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '')
    
    # Limit length
    if len(filename) > 200:
        filename = filename[:200]
    
    return filename.strip()


def format_duration(seconds: float) -> str:
    """
    Format seconds into HH:MM:SS format
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def validate_duration(duration: int) -> bool:
    """
    Validate if the duration is one of the allowed values
    
    Args:
        duration: Duration in seconds
        
    Returns:
        True if valid, False otherwise
    """
    allowed_durations = [3, 5, 8, 10]
    return duration in allowed_durations
