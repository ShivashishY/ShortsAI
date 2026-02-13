"""
Ollama-based content analysis service for intelligent video understanding
Uses vision models (LLaVA) to analyze video frames and detect engaging content
"""

import os
import asyncio
import logging
import base64
import json
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import cv2
import numpy as np

logger = logging.getLogger(__name__)

# Thread pool for Ollama operations
executor = ThreadPoolExecutor(max_workers=2)

# Default Ollama configuration
OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llava")  # Vision model for image analysis
OLLAMA_FALLBACK_MODEL = os.getenv("OLLAMA_FALLBACK_MODEL", "llama3.2")  # Text-only fallback


class OllamaAnalyzer:
    """
    Service for analyzing video content using Ollama's vision models
    
    Features:
    - Frame-by-frame content analysis using LLaVA
    - Engagement scoring based on visual content
    - Scene description and categorization
    - Detection of viral-worthy moments
    """
    
    # Content types that typically perform well in short-form videos
    ENGAGING_CONTENT_KEYWORDS = [
        "action", "reaction", "surprise", "emotional", "funny", "dramatic",
        "exciting", "intense", "climax", "reveal", "transformation",
        "celebration", "victory", "failure", "conflict", "resolution",
        "tutorial", "demonstration", "before and after", "comparison",
        "close-up", "expression", "gesture", "movement", "dance",
        "food", "cooking", "eating", "nature", "animal", "pet",
        "sports", "game", "competition", "music", "performance"
    ]
    
    def __init__(self, host: str = None, model: str = None):
        """
        Initialize the Ollama analyzer
        
        Args:
            host: Ollama server URL (default: http://localhost:11434)
            model: Vision model to use (default: llava)
        """
        self.host = host or OLLAMA_HOST
        self.model = model or OLLAMA_MODEL
        self.fallback_model = OLLAMA_FALLBACK_MODEL
        self._ollama_available = None
        self._client = None
        
    def _init_client(self):
        """Lazy initialization of Ollama client"""
        if self._client is None:
            try:
                import ollama
                self._client = ollama.Client(host=self.host)
                logger.info(f"Ollama client initialized with host: {self.host}")
            except Exception as e:
                logger.error(f"Failed to initialize Ollama client: {e}")
                self._client = None
        return self._client
    
    async def check_availability(self) -> bool:
        """
        Check if Ollama is available and the model is loaded
        
        Returns:
            True if Ollama is ready, False otherwise
        """
        if self._ollama_available is not None:
            return self._ollama_available
            
        try:
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(executor, self._check_ollama_sync)
            self._ollama_available = result
            return result
        except Exception as e:
            logger.warning(f"Ollama availability check failed: {e}")
            self._ollama_available = False
            return False
    
    def _check_ollama_sync(self) -> bool:
        """Synchronous check for Ollama availability"""
        try:
            client = self._init_client()
            if client is None:
                return False
            
            # List available models
            models = client.list()
            model_names = [m.get('name', '').split(':')[0] for m in models.get('models', [])]
            
            # Check if our vision model is available
            if self.model.split(':')[0] in model_names:
                logger.info(f"Ollama model '{self.model}' is available")
                return True
            
            # Try to pull the model
            logger.info(f"Attempting to pull Ollama model: {self.model}")
            client.pull(self.model)
            return True
            
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    async def analyze_video(
        self,
        video_path: str,
        sample_interval: int = 5,
        max_frames: int = 30
    ) -> Dict[float, Dict]:
        """
        Analyze video frames using Ollama vision model
        
        Args:
            video_path: Path to the video file
            sample_interval: Seconds between sampled frames
            max_frames: Maximum number of frames to analyze
            
        Returns:
            Dict mapping timestamp -> analysis results
        """
        if not await self.check_availability():
            logger.warning("Ollama not available, skipping content analysis")
            return {}
        
        try:
            loop = asyncio.get_event_loop()
            results = await loop.run_in_executor(
                executor,
                self._analyze_video_sync,
                video_path,
                sample_interval,
                max_frames
            )
            return results
        except Exception as e:
            logger.error(f"Video analysis error: {e}")
            return {}
    
    def _analyze_video_sync(
        self,
        video_path: str,
        sample_interval: int,
        max_frames: int
    ) -> Dict[float, Dict]:
        """Synchronous video analysis"""
        results = {}
        
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                logger.error("Failed to open video file")
                return results
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            duration = total_frames / fps if fps > 0 else 0
            
            # Calculate frame sampling
            frame_interval = int(fps * sample_interval)
            frames_to_analyze = min(max_frames, int(duration / sample_interval))
            
            logger.info(f"Analyzing {frames_to_analyze} frames from video ({duration:.1f}s)")
            
            frame_idx = 0
            analyzed_count = 0
            
            while analyzed_count < frames_to_analyze:
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                timestamp = frame_idx / fps
                
                # Analyze this frame
                analysis = self._analyze_frame(frame, timestamp)
                if analysis:
                    results[timestamp] = analysis
                    analyzed_count += 1
                    logger.debug(f"Frame {analyzed_count}/{frames_to_analyze} at {timestamp:.1f}s: score={analysis.get('score', 0)}")
                
                frame_idx += frame_interval
            
            cap.release()
            logger.info(f"Ollama analysis complete: {len(results)} frames analyzed")
            
        except Exception as e:
            logger.error(f"Video analysis error: {e}")
        
        return results
    
    def _analyze_frame(self, frame: np.ndarray, timestamp: float) -> Optional[Dict]:
        """
        Analyze a single frame using Ollama vision model
        
        Args:
            frame: OpenCV frame (BGR format)
            timestamp: Frame timestamp in seconds
            
        Returns:
            Analysis dictionary with score, description, and content tags
        """
        try:
            client = self._init_client()
            if client is None:
                return None
            
            # Convert frame to base64
            _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
            image_base64 = base64.b64encode(buffer).decode('utf-8')
            
            # Create analysis prompt
            prompt = """Analyze this video frame for short-form video potential.

Rate the ENGAGEMENT SCORE from 0-100 based on:
- Visual interest and composition
- Action or movement present
- Emotional content (reactions, expressions)
- Viral potential for platforms like TikTok/YouTube Shorts

Respond in this exact JSON format only:
{
    "score": <0-100>,
    "description": "<brief 10-word description>",
    "content_type": "<action|reaction|tutorial|entertainment|other>",
    "has_person": <true|false>,
    "has_text": <true|false>,
    "mood": "<exciting|funny|emotional|informative|calm>",
    "viral_potential": "<high|medium|low>"
}"""

            # Call Ollama with vision
            response = client.chat(
                model=self.model,
                messages=[{
                    'role': 'user',
                    'content': prompt,
                    'images': [image_base64]
                }],
                options={
                    'temperature': 0.3,  # Lower temperature for consistent scoring
                    'num_predict': 300
                }
            )
            
            # Parse response
            response_text = response['message']['content']
            analysis = self._parse_analysis_response(response_text, timestamp)
            
            return analysis
            
        except Exception as e:
            logger.warning(f"Frame analysis error at {timestamp:.1f}s: {e}")
            return None
    
    def _parse_analysis_response(self, response_text: str, timestamp: float) -> Dict:
        """
        Parse Ollama's response into structured analysis
        
        Args:
            response_text: Raw response from Ollama
            timestamp: Frame timestamp
            
        Returns:
            Parsed analysis dictionary
        """
        try:
            # Try to extract JSON from response
            # Handle cases where response might have extra text
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
                
                # Validate and normalize score
                score = data.get('score', 50)
                if isinstance(score, str):
                    score = int(score)
                score = max(0, min(100, score))
                
                # Apply viral potential bonus
                viral_bonus = {
                    'high': 15,
                    'medium': 5,
                    'low': 0
                }.get(data.get('viral_potential', 'low'), 0)
                
                # Apply content type bonus
                content_bonus = {
                    'action': 10,
                    'reaction': 12,
                    'tutorial': 8,
                    'entertainment': 10,
                    'other': 0
                }.get(data.get('content_type', 'other'), 0)
                
                final_score = min(100, score + viral_bonus + content_bonus)
                
                return {
                    'timestamp': timestamp,
                    'score': final_score,
                    'raw_score': score,
                    'description': data.get('description', 'Unknown content'),
                    'content_type': data.get('content_type', 'other'),
                    'has_person': data.get('has_person', False),
                    'has_text': data.get('has_text', False),
                    'mood': data.get('mood', 'calm'),
                    'viral_potential': data.get('viral_potential', 'low')
                }
                
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse JSON from Ollama response: {e}")
        except Exception as e:
            logger.warning(f"Error parsing analysis response: {e}")
        
        # Return default analysis if parsing fails
        return {
            'timestamp': timestamp,
            'score': 50,
            'raw_score': 50,
            'description': 'Analysis unavailable',
            'content_type': 'other',
            'has_person': False,
            'has_text': False,
            'mood': 'calm',
            'viral_potential': 'low'
        }
    
    def get_content_scores(self, analysis_results: Dict[float, Dict]) -> Dict[float, float]:
        """
        Extract engagement scores from analysis results
        
        Args:
            analysis_results: Dict from analyze_video()
            
        Returns:
            Dict mapping timestamp -> score (0-100)
        """
        scores = {}
        for timestamp, analysis in analysis_results.items():
            scores[timestamp] = analysis.get('score', 0)
        return scores
    
    def get_viral_segments(
        self,
        analysis_results: Dict[float, Dict],
        threshold: float = 70
    ) -> List[Dict]:
        """
        Get segments with high viral potential
        
        Args:
            analysis_results: Dict from analyze_video()
            threshold: Minimum score threshold
            
        Returns:
            List of high-potential segments
        """
        viral_segments = []
        
        for timestamp, analysis in analysis_results.items():
            if analysis.get('score', 0) >= threshold:
                viral_segments.append({
                    'timestamp': timestamp,
                    'score': analysis['score'],
                    'reason': f"{analysis.get('content_type', 'content').title()}: {analysis.get('description', 'Engaging content')}",
                    'viral_potential': analysis.get('viral_potential', 'medium')
                })
        
        # Sort by score descending
        viral_segments.sort(key=lambda x: x['score'], reverse=True)
        
        return viral_segments


# Singleton instance for reuse
_analyzer_instance = None

def get_ollama_analyzer() -> OllamaAnalyzer:
    """Get or create singleton OllamaAnalyzer instance"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = OllamaAnalyzer()
    return _analyzer_instance
