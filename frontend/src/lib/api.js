/**
 * API service for communicating with the backend
 */

const API_BASE = '/api';

/**
 * Start video processing
 * @param {string} url - YouTube URL
 * @param {number} duration - Clip duration (30, 60, 90, 120, or 180 seconds)
 * @param {number} clipCount - Number of clips to generate (5, 10, or 15)
 * @returns {Promise<{jobId: string}>}
 */
export async function processVideo(url, duration, clipCount = 5) {
  const response = await fetch(`${API_BASE}/process-video`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ url, duration, clip_count: clipCount }),
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to start processing');
  }
  
  return response.json();
}

/**
 * Get job status
 * @param {string} jobId - Job ID
 * @returns {Promise<{status: string, progress: number, message?: string, clips?: Array, error?: string}>}
 */
export async function getJobStatus(jobId) {
  const response = await fetch(`${API_BASE}/status/${jobId}`);
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to get status');
  }
  
  return response.json();
}

/**
 * Get clip preview URL
 * @param {string} jobId - Job ID
 * @param {number} clipIndex - Clip index
 * @returns {string}
 */
export function getPreviewUrl(jobId, clipIndex) {
  return `${API_BASE}/preview/${jobId}/${clipIndex}`;
}

/**
 * Get clip download URL
 * @param {string} jobId - Job ID
 * @param {number} clipIndex - Clip index
 * @returns {string}
 */
export function getDownloadUrl(jobId, clipIndex) {
  return `${API_BASE}/download/${jobId}/${clipIndex}`;
}

/**
 * Download a clip
 * @param {string} jobId - Job ID
 * @param {number} clipIndex - Clip index
 */
export async function downloadClip(jobId, clipIndex) {
  const url = getDownloadUrl(jobId, clipIndex);
  
  // Create temporary link and trigger download
  const a = document.createElement('a');
  a.href = url;
  a.download = `short_clip_${clipIndex}.mp4`;
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}

/**
 * Delete a job
 * @param {string} jobId - Job ID
 */
export async function deleteJob(jobId) {
  const response = await fetch(`${API_BASE}/job/${jobId}`, {
    method: 'DELETE',
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Failed to delete job');
  }
  
  return response.json();
}
