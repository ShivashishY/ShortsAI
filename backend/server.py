"""
YouTube to Shorts AI Generator - Backend Server
FastAPI server with video processing capabilities
"""

import os
import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, HttpUrl, field_validator
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv

from services.youtube_downloader import YouTubeDownloader
from services.ai_detector import AIDetector
from services.video_processor import VideoProcessor
from utils.validators import validate_youtube_url, extract_video_id
from utils.cleanup import cleanup_old_files

# Load environment variables
load_dotenv()

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

# Job storage (in production, use Redis)
jobs = {}

# Directory for temporary files
TEMP_DIR = os.getenv("TEMP_DIR", "./temp")
MAX_VIDEO_DURATION = int(os.getenv("MAX_VIDEO_DURATION", 10800))  # 180 minutes default

# Ensure temp directory exists
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(os.path.join(TEMP_DIR, "downloads"), exist_ok=True)
os.makedirs(os.path.join(TEMP_DIR, "outputs"), exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown events"""
    # Startup: Clean old files
    cleanup_old_files(TEMP_DIR, hours=24)
    yield
    # Shutdown: Final cleanup
    cleanup_old_files(TEMP_DIR, hours=0)


app = FastAPI(
    title="YouTube to Shorts AI Generator",
    description="Generate engaging short-form clips from YouTube videos using AI",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limit error handler
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class VideoRequest(BaseModel):
    """Request model for video processing"""
    url: str
    duration: int = 60  # Default 60 seconds
    clip_count: int = 5  # Default 5 clips
    
    @field_validator('url')
    @classmethod
    def validate_url(cls, v):
        if not validate_youtube_url(v):
            raise ValueError('Invalid YouTube URL')
        return v
    
    @field_validator('duration')
    @classmethod
    def validate_duration(cls, v):
        if v not in [30, 60, 90, 120, 180]:
            raise ValueError('Duration must be 30, 60, 90, 120, or 180 seconds')
        return v
    
    @field_validator('clip_count')
    @classmethod
    def validate_clip_count(cls, v):
        if v not in [5, 10, 15]:
            raise ValueError('Clip count must be 5, 10, or 15')
        return v


class JobStatus(BaseModel):
    """Response model for job status"""
    job_id: str
    status: str
    progress: int
    message: Optional[str] = None
    clips: Optional[list] = None
    error: Optional[str] = None


async def process_video_task(job_id: str, url: str, duration: int, clip_count: int = 5):
    """Background task for video processing"""
    try:
        # Initialize services
        downloader = YouTubeDownloader(TEMP_DIR)
        detector = AIDetector()
        processor = VideoProcessor(TEMP_DIR)
        
        # Extract video ID
        video_id = extract_video_id(url)
        download_path = os.path.join(TEMP_DIR, "downloads", f"{video_id}.mp4")
        
        # Check if video already exists (cache hit)
        if os.path.exists(download_path):
            jobs[job_id]["status"] = "analyzing"
            jobs[job_id]["progress"] = 25
            jobs[job_id]["message"] = "Using cached video, skipping download..."
            video_info = {'path': download_path, 'cached': True}
        else:
            jobs[job_id]["status"] = "downloading"
            jobs[job_id]["progress"] = 10
            jobs[job_id]["message"] = "Downloading video from YouTube..."
            
            # Download video
            video_info = await downloader.download(url, download_path, max_duration=MAX_VIDEO_DURATION)
        
        if not video_info:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = "Failed to download video"
            return
        
        jobs[job_id]["status"] = "analyzing"
        jobs[job_id]["progress"] = 30
        jobs[job_id]["message"] = "Analyzing video for engaging moments..."
        
        # Analyze video with AI
        segments = await detector.analyze(download_path)
        
        if not segments:
            jobs[job_id]["status"] = "failed"
            jobs[job_id]["error"] = "No engaging segments found in video"
            return
        
        jobs[job_id]["status"] = "processing"
        jobs[job_id]["progress"] = 60
        jobs[job_id]["message"] = "Extracting and processing clips..."
        
        # Select top segments based on duration and requested clip count
        top_segments = detector.select_best_segments(segments, duration, count=clip_count)
        
        # Process and create clips
        output_dir = os.path.join(TEMP_DIR, "outputs", job_id)
        os.makedirs(output_dir, exist_ok=True)
        
        clips = []
        for i, segment in enumerate(top_segments):
            jobs[job_id]["progress"] = 60 + (i + 1) * 8
            jobs[job_id]["message"] = f"Processing clip {i + 1} of {len(top_segments)}..."
            
            output_path = os.path.join(output_dir, f"clip_{i + 1}.mp4")
            clip_info = await processor.create_short(
                input_path=download_path,
                output_path=output_path,
                start_time=segment["start"],
                duration=duration,
                score=segment["score"]
            )
            
            if clip_info:
                clips.append({
                    "index": i + 1,
                    "start_time": segment["start"],
                    "end_time": segment["start"] + duration,
                    "score": segment["score"],
                    "filename": f"clip_{i + 1}.mp4",
                    "reasons": segment.get("reasons", [])
                })
        
        # Keep downloaded video for caching (don't delete)
        # Videos will be cleaned up by the scheduled cleanup task after 24 hours
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["message"] = f"Successfully generated {len(clips)} clips!"
        jobs[job_id]["clips"] = clips
        jobs[job_id]["completed_at"] = datetime.utcnow().isoformat()
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["progress"] = 0


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "healthy", "service": "YouTube to Shorts AI Generator"}


@app.post("/api/process-video", response_model=dict)
@limiter.limit("5/hour")
async def process_video(request: Request, video_request: VideoRequest, background_tasks: BackgroundTasks):
    """
    Start video processing job
    Rate limited to 5 requests per hour per IP
    """
    job_id = str(uuid.uuid4())
    
    jobs[job_id] = {
        "job_id": job_id,
        "status": "queued",
        "progress": 0,
        "message": "Job queued for processing",
        "url": video_request.url,
        "duration": video_request.duration,
        "created_at": datetime.utcnow().isoformat(),
        "clips": None,
        "error": None
    }
    
    # Start background processing
    background_tasks.add_task(
        process_video_task,
        job_id,
        video_request.url,
        video_request.duration,
        video_request.clip_count
    )
    
    return {"jobId": job_id, "status": "queued"}


@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    """Get the status of a processing job"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return {
        "jobId": job_id,
        "status": job["status"],
        "progress": job["progress"],
        "message": job.get("message"),
        "clips": job.get("clips"),
        "error": job.get("error")
    }


@app.get("/api/download/{job_id}/{clip_index}")
async def download_clip(job_id: str, clip_index: int):
    """Download a generated clip"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    if job["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed yet")
    
    clip_path = os.path.join(TEMP_DIR, "outputs", job_id, f"clip_{clip_index}.mp4")
    
    if not os.path.exists(clip_path):
        raise HTTPException(status_code=404, detail="Clip not found")
    
    return FileResponse(
        clip_path,
        media_type="video/mp4",
        filename=f"short_clip_{clip_index}.mp4"
    )


@app.get("/api/preview/{job_id}/{clip_index}")
async def preview_clip(job_id: str, clip_index: int):
    """Stream a clip for preview"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    clip_path = os.path.join(TEMP_DIR, "outputs", job_id, f"clip_{clip_index}.mp4")
    
    if not os.path.exists(clip_path):
        raise HTTPException(status_code=404, detail="Clip not found")
    
    return FileResponse(clip_path, media_type="video/mp4")


@app.delete("/api/job/{job_id}")
async def delete_job(job_id: str):
    """Delete a job and its associated files"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Delete output files
    output_dir = os.path.join(TEMP_DIR, "outputs", job_id)
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
    
    # Remove from jobs dict
    del jobs[job_id]
    
    return {"message": "Job deleted successfully"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
