"""
AI-powered video analysis service for detecting engaging moments
Uses multiple detection methods: audio analysis, scene detection, face detection, motion analysis,
and Ollama-based content understanding for intelligent clip selection
"""

import os
import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import cv2

from services.ollama_analyzer import get_ollama_analyzer, OllamaAnalyzer

logger = logging.getLogger(__name__)

# Thread pool for CPU-intensive operations
executor = ThreadPoolExecutor(max_workers=4)


class AIDetector:
    """
    AI service for analyzing videos and detecting engaging moments
    Combines multiple signals:
    - Audio peaks and energy levels
    - Scene changes and visual interest
    - Face detection and close-ups
    - Motion intensity
    - Ollama-powered content analysis (LLaVA vision model)
    """
    
    def __init__(self, use_ollama: bool = True):
        """Initialize the AI detector with various models
        
        Args:
            use_ollama: Whether to use Ollama for content analysis (default: True)
        """
        self.face_cascade = None
        self.min_segment_gap = 2.0  # Minimum gap between segments in seconds
        self.use_ollama = use_ollama
        self.ollama_analyzer: Optional[OllamaAnalyzer] = None
        
        if use_ollama:
            self.ollama_analyzer = get_ollama_analyzer()
        
    def _init_face_detector(self):
        """Lazy initialization of face detector"""
        if self.face_cascade is None:
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            self.face_cascade = cv2.CascadeClassifier(cascade_path)
    
    async def analyze(self, video_path: str) -> List[Dict]:
        """
        Analyze video and return list of engaging segments with scores
        
        Args:
            video_path: Path to the video file
            
        Returns:
            List of segment dictionaries with start time, score, and reasons
        """
        try:
            logger.info(f"Starting video analysis: {video_path}")
            
            # Run all analysis methods in parallel
            loop = asyncio.get_event_loop()
            
            # Get video properties first
            video_info = await loop.run_in_executor(
                executor, self._get_video_info, video_path
            )
            
            if not video_info:
                logger.error("Failed to get video info")
                return []
            
            duration = video_info['duration']
            fps = video_info['fps']
            
            # Run analysis methods
            audio_scores = await loop.run_in_executor(
                executor, self._analyze_audio, video_path, duration
            )
            
            scene_scores = await loop.run_in_executor(
                executor, self._analyze_scenes, video_path, fps
            )
            
            motion_scores = await loop.run_in_executor(
                executor, self._analyze_motion, video_path, fps
            )
            
            face_scores = await loop.run_in_executor(
                executor, self._analyze_faces, video_path, fps
            )
            
            # Run Ollama content analysis if available
            content_scores = {}
            ollama_analysis = {}
            if self.use_ollama and self.ollama_analyzer:
                logger.info("Running Ollama content analysis...")
                ollama_analysis = await self.ollama_analyzer.analyze_video(
                    video_path,
                    sample_interval=3,  # Analyze every 3 seconds
                    max_frames=50  # Max 50 frames to analyze
                )
                content_scores = self.ollama_analyzer.get_content_scores(ollama_analysis)
                logger.info(f"Ollama analyzed {len(content_scores)} frames")
            
            # Combine all scores
            segments = self._combine_scores(
                duration=duration,
                audio_scores=audio_scores,
                scene_scores=scene_scores,
                motion_scores=motion_scores,
                face_scores=face_scores,
                content_scores=content_scores,
                ollama_analysis=ollama_analysis
            )
            
            logger.info(f"Analysis complete. Found {len(segments)} engaging segments")
            return segments
            
        except Exception as e:
            logger.error(f"Analysis error: {e}")
            return []
    
    def _get_video_info(self, video_path: str) -> Optional[Dict]:
        """Get basic video information"""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                'fps': fps,
                'frame_count': frame_count,
                'width': width,
                'height': height,
                'duration': duration
            }
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return None
    
    def _analyze_audio(self, video_path: str, duration: float) -> Dict[float, float]:
        """
        Analyze audio for peaks, energy levels, and interesting moments
        Returns dict mapping timestamp -> score (0-100)
        """
        scores = {}
        
        try:
            import librosa
            
            # Load audio from video
            y, sr = librosa.load(video_path, sr=22050, mono=True)
            
            # Calculate RMS energy for each second
            hop_length = sr  # 1 second windows
            frame_length = sr
            
            rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
            
            # Normalize to 0-100
            if len(rms) > 0:
                rms_normalized = (rms - rms.min()) / (rms.max() - rms.min() + 1e-6) * 100
                
                for i, score in enumerate(rms_normalized):
                    timestamp = i  # Each frame is 1 second
                    if timestamp < duration:
                        scores[timestamp] = float(score)
            
            # Also detect onset strength (beats, impacts)
            onset_env = librosa.onset.onset_strength(y=y, sr=sr)
            onset_times = librosa.times_like(onset_env, sr=sr)
            
            # Normalize onset strength
            onset_normalized = (onset_env - onset_env.min()) / (onset_env.max() - onset_env.min() + 1e-6) * 50
            
            # Add onset bonus to existing scores
            for i, (time, strength) in enumerate(zip(onset_times, onset_normalized)):
                time_key = int(time)
                if time_key in scores:
                    scores[time_key] = min(100, scores[time_key] + strength)
                elif time_key < duration:
                    scores[time_key] = strength
            
            logger.info(f"Audio analysis complete: {len(scores)} timestamps scored")
            
        except Exception as e:
            logger.warning(f"Audio analysis error: {e}")
            # Return empty scores, other methods will still work
        
        return scores
    
    def _analyze_scenes(self, video_path: str, fps: float) -> Dict[float, float]:
        """
        Detect scene changes and visual interest points
        Returns dict mapping timestamp -> score (0-100)
        """
        scores = {}
        
        try:
            # Use simpler scene detection without PySceneDetect for reliability
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return scores
            
            prev_frame = None
            frame_idx = 0
            sample_rate = max(1, int(fps / 2))  # Sample every 0.5 seconds
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % sample_rate == 0:
                    # Convert to grayscale for comparison
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray = cv2.resize(gray, (160, 90))
                    
                    if prev_frame is not None:
                        # Calculate frame difference
                        diff = cv2.absdiff(prev_frame, gray)
                        score = np.mean(diff) / 255 * 100  # Normalize to 0-100
                        
                        timestamp = frame_idx / fps
                        scores[timestamp] = float(score)
                    
                    prev_frame = gray
                
                frame_idx += 1
            
            cap.release()
            logger.info(f"Scene analysis complete: {len(scores)} timestamps scored")
            
        except Exception as e:
            logger.warning(f"Scene analysis error: {e}")
        
        return scores
    
    def _analyze_motion(self, video_path: str, fps: float) -> Dict[float, float]:
        """
        Analyze motion intensity using optical flow
        Returns dict mapping timestamp -> score (0-100)
        """
        scores = {}
        
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return scores
            
            prev_gray = None
            frame_idx = 0
            sample_rate = max(1, int(fps / 2))  # Sample every 0.5 seconds
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % sample_rate == 0:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    gray = cv2.resize(gray, (320, 180))
                    
                    if prev_gray is not None:
                        # Calculate optical flow
                        flow = cv2.calcOpticalFlowFarneback(
                            prev_gray, gray, None,
                            pyr_scale=0.5, levels=3, winsize=15,
                            iterations=3, poly_n=5, poly_sigma=1.2, flags=0
                        )
                        
                        # Calculate magnitude
                        mag, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                        motion_score = np.mean(mag) * 10  # Scale factor
                        motion_score = min(100, motion_score)  # Cap at 100
                        
                        timestamp = frame_idx / fps
                        scores[timestamp] = float(motion_score)
                    
                    prev_gray = gray
                
                frame_idx += 1
            
            cap.release()
            logger.info(f"Motion analysis complete: {len(scores)} timestamps scored")
            
        except Exception as e:
            logger.warning(f"Motion analysis error: {e}")
        
        return scores
    
    def _analyze_faces(self, video_path: str, fps: float) -> Dict[float, float]:
        """
        Detect faces and close-ups
        Returns dict mapping timestamp -> score (0-100)
        """
        scores = {}
        
        try:
            self._init_face_detector()
            
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                return scores
            
            frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            frame_area = frame_width * frame_height
            
            frame_idx = 0
            sample_rate = max(1, int(fps))  # Sample every second
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_idx % sample_rate == 0:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    
                    # Detect faces
                    faces = self.face_cascade.detectMultiScale(
                        gray,
                        scaleFactor=1.1,
                        minNeighbors=5,
                        minSize=(30, 30)
                    )
                    
                    score = 0
                    if len(faces) > 0:
                        # Score based on face count and size
                        total_face_area = sum(w * h for (x, y, w, h) in faces)
                        face_ratio = total_face_area / frame_area
                        
                        # Bigger faces (close-ups) get higher scores
                        score = min(100, face_ratio * 500 + len(faces) * 10)
                    
                    timestamp = frame_idx / fps
                    scores[timestamp] = float(score)
                
                frame_idx += 1
            
            cap.release()
            logger.info(f"Face analysis complete: {len(scores)} timestamps scored")
            
        except Exception as e:
            logger.warning(f"Face analysis error: {e}")
        
        return scores
    
    def _combine_scores(
        self,
        duration: float,
        audio_scores: Dict[float, float],
        scene_scores: Dict[float, float],
        motion_scores: Dict[float, float],
        face_scores: Dict[float, float],
        content_scores: Dict[float, float] = None,
        ollama_analysis: Dict[float, Dict] = None
    ) -> List[Dict]:
        """
        Combine all analysis scores into final segment scores
        
        Weights (with Ollama):
        - Audio: 20%
        - Motion: 20%
        - Scene changes: 15%
        - Faces: 15%
        - Ollama Content: 30%
        
        Weights (without Ollama):
        - Audio: 30%
        - Motion: 25%
        - Scene changes: 20%
        - Faces: 25%
        """
        segments = []
        content_scores = content_scores or {}
        ollama_analysis = ollama_analysis or {}
        
        # Determine weights based on Ollama availability
        has_ollama = len(content_scores) > 0
        
        if has_ollama:
            # Weights with Ollama content analysis
            weights = {
                'audio': 0.20,
                'motion': 0.20,
                'scene': 0.15,
                'faces': 0.15,
                'content': 0.30
            }
        else:
            # Original weights without Ollama
            weights = {
                'audio': 0.30,
                'motion': 0.25,
                'scene': 0.20,
                'faces': 0.25,
                'content': 0.0
            }
        
        # Create timeline with 1-second granularity
        for t in range(int(duration)):
            timestamp = float(t)
            
            # Get scores with defaults
            audio = audio_scores.get(timestamp, audio_scores.get(t, 0))
            motion = self._get_nearest_score(motion_scores, timestamp)
            scene = self._get_nearest_score(scene_scores, timestamp)
            faces = self._get_nearest_score(face_scores, timestamp)
            content = self._get_nearest_score(content_scores, timestamp) if has_ollama else 0
            
            # Get Ollama analysis details for this timestamp
            ollama_details = self._get_nearest_ollama_analysis(ollama_analysis, timestamp)
            
            # Weighted combination
            combined_score = (
                audio * weights['audio'] +
                motion * weights['motion'] +
                scene * weights['scene'] +
                faces * weights['faces'] +
                content * weights['content']
            )
            
            # Build reasons list
            reasons = []
            if audio > 60:
                reasons.append("High audio energy")
            if motion > 50:
                reasons.append("High motion")
            if scene > 40:
                reasons.append("Visual interest")
            if faces > 30:
                reasons.append("Face detected")
            
            # Add Ollama-based reasons
            if ollama_details:
                if ollama_details.get('viral_potential') == 'high':
                    reasons.append(f"High viral potential: {ollama_details.get('description', 'Engaging content')}")
                elif ollama_details.get('score', 0) > 70:
                    reasons.append(f"AI detected: {ollama_details.get('content_type', 'engaging')} content")
                if ollama_details.get('mood') in ['exciting', 'funny', 'emotional']:
                    reasons.append(f"{ollama_details.get('mood', 'engaging').title()} moment")
            
            segment_data = {
                'start': timestamp,
                'score': round(combined_score, 2),
                'reasons': reasons,
                'details': {
                    'audio': round(audio, 2),
                    'motion': round(motion, 2),
                    'scene': round(scene, 2),
                    'faces': round(faces, 2),
                    'content': round(content, 2) if has_ollama else None
                }
            }
            
            # Add Ollama insights if available
            if ollama_details:
                segment_data['ai_insights'] = {
                    'description': ollama_details.get('description'),
                    'content_type': ollama_details.get('content_type'),
                    'mood': ollama_details.get('mood'),
                    'viral_potential': ollama_details.get('viral_potential'),
                    'has_person': ollama_details.get('has_person'),
                    'has_text': ollama_details.get('has_text')
                }
            
            segments.append(segment_data)
        
        # Sort by score descending
        segments.sort(key=lambda x: x['score'], reverse=True)
        
        return segments
    
    def _get_nearest_ollama_analysis(self, analysis: Dict[float, Dict], timestamp: float) -> Optional[Dict]:
        """Get Ollama analysis nearest to timestamp"""
        if not analysis:
            return None
        
        # Check exact match first
        if timestamp in analysis:
            return analysis[timestamp]
        
        # Find nearest within 5 seconds
        nearest_time = min(analysis.keys(), key=lambda t: abs(t - timestamp))
        if abs(nearest_time - timestamp) <= 5.0:
            return analysis[nearest_time]
        
        return None
    
    def _get_nearest_score(self, scores: Dict[float, float], timestamp: float) -> float:
        """Get score nearest to timestamp"""
        if not scores:
            return 0
        
        # Check exact match first
        if timestamp in scores:
            return scores[timestamp]
        
        # Find nearest
        nearest_time = min(scores.keys(), key=lambda t: abs(t - timestamp))
        if abs(nearest_time - timestamp) <= 1.0:  # Within 1 second
            return scores[nearest_time]
        
        return 0
    
    def select_best_segments(
        self,
        segments: List[Dict],
        duration: int,
        count: int = 5
    ) -> List[Dict]:
        """
        Select the best non-overlapping segments
        
        Args:
            segments: List of scored segments
            duration: Clip duration in seconds
            count: Number of clips to select
            
        Returns:
            List of best non-overlapping segments
        """
        selected = []
        
        for segment in segments:
            if len(selected) >= count:
                break
            
            start = segment['start']
            end = start + duration
            
            # Check for overlap with already selected segments
            overlaps = False
            for sel in selected:
                sel_start = sel['start']
                sel_end = sel_start + duration
                
                # Check overlap with gap
                gap = self.min_segment_gap
                if not (end + gap <= sel_start or start >= sel_end + gap):
                    overlaps = True
                    break
            
            if not overlaps:
                selected.append(segment)
        
        # Sort by start time for chronological order
        selected.sort(key=lambda x: x['start'])
        
        return selected
