import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Download, Check, Loader2, FileDown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { downloadClip } from "@/lib/api";
import { cn } from "@/lib/utils";

/**
 * Download button component with loading state
 */
export function DownloadButton({ jobId, clipIndex, className }) {
  const [status, setStatus] = useState("idle"); // idle, downloading, success, error

  const handleDownload = async () => {
    try {
      setStatus("downloading");
      await downloadClip(jobId, clipIndex);
      setStatus("success");
      
      // Reset after 2 seconds
      setTimeout(() => setStatus("idle"), 2000);
    } catch (error) {
      console.error("Download error:", error);
      setStatus("error");
      setTimeout(() => setStatus("idle"), 3000);
    }
  };

  return (
    <Button
      onClick={handleDownload}
      disabled={status === "downloading"}
      variant={status === "success" ? "default" : "gradient"}
      className={cn("gap-2 min-w-[140px]", className)}
    >
      <AnimatePresence mode="wait">
        {status === "idle" && (
          <motion.span
            key="idle"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center gap-2"
          >
            <Download className="h-4 w-4" />
            Download
          </motion.span>
        )}
        
        {status === "downloading" && (
          <motion.span
            key="downloading"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center gap-2"
          >
            <Loader2 className="h-4 w-4 animate-spin" />
            Downloading...
          </motion.span>
        )}
        
        {status === "success" && (
          <motion.span
            key="success"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center gap-2"
          >
            <Check className="h-4 w-4" />
            Downloaded!
          </motion.span>
        )}
        
        {status === "error" && (
          <motion.span
            key="error"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="flex items-center gap-2 text-red-400"
          >
            Failed - Retry
          </motion.span>
        )}
      </AnimatePresence>
    </Button>
  );
}

/**
 * Download all button for batch downloading
 */
export function DownloadAllButton({ jobId, clips, className }) {
  const [downloading, setDownloading] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleDownloadAll = async () => {
    try {
      setDownloading(true);
      setProgress(0);
      
      for (let i = 0; i < clips.length; i++) {
        await downloadClip(jobId, clips[i].index);
        setProgress(((i + 1) / clips.length) * 100);
        
        // Small delay between downloads
        await new Promise(resolve => setTimeout(resolve, 500));
      }
      
      setDownloading(false);
    } catch (error) {
      console.error("Download all error:", error);
      setDownloading(false);
    }
  };

  return (
    <Button
      onClick={handleDownloadAll}
      disabled={downloading || clips.length === 0}
      variant="glow"
      size="lg"
      className={cn("gap-2 relative overflow-hidden", className)}
    >
      {downloading && (
        <motion.div
          className="absolute inset-0 bg-primary/30"
          initial={{ width: "0%" }}
          animate={{ width: `${progress}%` }}
          transition={{ ease: "linear" }}
        />
      )}
      
      <span className="relative z-10 flex items-center gap-2">
        {downloading ? (
          <>
            <Loader2 className="h-5 w-5 animate-spin" />
            Downloading {Math.round(progress)}%
          </>
        ) : (
          <>
            <FileDown className="h-5 w-5" />
            Download All ({clips.length} clips)
          </>
        )}
      </span>
    </Button>
  );
}

export default DownloadButton;
