import React from "react";
import { motion } from "framer-motion";
import { Loader2, Download, Sparkles, Video, CheckCircle2, XCircle } from "lucide-react";
import { Progress } from "@/components/ui/progress";
import { cn } from "@/lib/utils";

const STATUS_CONFIG = {
  queued: {
    icon: Loader2,
    color: "text-muted-foreground",
    bgColor: "bg-muted",
    title: "Queued",
    description: "Your video is in the queue...",
  },
  downloading: {
    icon: Download,
    color: "text-blue-400",
    bgColor: "bg-blue-500/10",
    title: "Downloading",
    description: "Fetching video from YouTube...",
  },
  analyzing: {
    icon: Sparkles,
    color: "text-purple-400",
    bgColor: "bg-purple-500/10",
    title: "Analyzing",
    description: "AI is detecting engaging moments...",
  },
  processing: {
    icon: Video,
    color: "text-pink-400",
    bgColor: "bg-pink-500/10",
    title: "Processing",
    description: "Creating your short clips...",
  },
  completed: {
    icon: CheckCircle2,
    color: "text-green-400",
    bgColor: "bg-green-500/10",
    title: "Complete!",
    description: "Your clips are ready!",
  },
  failed: {
    icon: XCircle,
    color: "text-red-400",
    bgColor: "bg-red-500/10",
    title: "Failed",
    description: "Something went wrong",
  },
};

/**
 * Processing status component with animated progress
 */
export function ProcessingStatus({ status, progress, message, error }) {
  const config = STATUS_CONFIG[status] || STATUS_CONFIG.queued;
  const Icon = config.icon;
  const isLoading = ["queued", "downloading", "analyzing", "processing"].includes(status);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="w-full max-w-md mx-auto"
    >
      <div className={cn(
        "rounded-2xl border p-6 space-y-6",
        config.bgColor,
        "border-border"
      )}>
        {/* Status icon */}
        <div className="flex justify-center">
          <motion.div
            animate={isLoading ? { rotate: 360 } : {}}
            transition={isLoading ? { duration: 2, repeat: Infinity, ease: "linear" } : {}}
            className={cn(
              "w-16 h-16 rounded-full flex items-center justify-center",
              config.bgColor,
              "border-2 border-current",
              config.color
            )}
          >
            <Icon className="w-8 h-8" />
          </motion.div>
        </div>

        {/* Status text */}
        <div className="text-center space-y-2">
          <h3 className={cn("text-xl font-semibold", config.color)}>
            {config.title}
          </h3>
          <p className="text-sm text-muted-foreground">
            {message || config.description}
          </p>
        </div>

        {/* Progress bar */}
        {isLoading && (
          <div className="space-y-2">
            <Progress value={progress} showStripes={true} />
            <p className="text-xs text-center text-muted-foreground">
              {progress}% complete
            </p>
          </div>
        )}

        {/* Error message */}
        {status === "failed" && error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="p-4 rounded-xl bg-red-500/10 border border-red-500/20"
          >
            <p className="text-sm text-red-400">{error}</p>
          </motion.div>
        )}

        {/* Processing animation dots */}
        {isLoading && (
          <div className="flex justify-center gap-1.5">
            {[0, 1, 2].map((i) => (
              <motion.div
                key={i}
                className={cn("w-2 h-2 rounded-full", config.color.replace("text-", "bg-"))}
                animate={{
                  opacity: [0.3, 1, 0.3],
                  scale: [0.8, 1, 0.8],
                }}
                transition={{
                  duration: 1,
                  repeat: Infinity,
                  delay: i * 0.2,
                }}
              />
            ))}
          </div>
        )}
      </div>

      {/* Tips while processing */}
      {isLoading && (
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-xs text-center text-muted-foreground mt-4"
        >
          This may take a few minutes depending on the video length
        </motion.p>
      )}
    </motion.div>
  );
}

export default ProcessingStatus;
