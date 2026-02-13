import React, { useState } from "react";
import { motion } from "framer-motion";
import { Link2, AlertCircle, Check, Youtube } from "lucide-react";
import { Input } from "@/components/ui/input";
import { isValidYouTubeUrl, extractVideoId, getYouTubeThumbnail } from "@/lib/utils";
import { cn } from "@/lib/utils";

/**
 * YouTube URL input component with validation
 */
export function URLInput({ value, onChange, disabled }) {
  const [isFocused, setIsFocused] = useState(false);
  const isValid = value ? isValidYouTubeUrl(value) : null;
  const videoId = isValid ? extractVideoId(value) : null;

  return (
    <div className="space-y-3">
      <label className="text-sm font-medium text-foreground">
        YouTube Video URL
      </label>
      
      <div className="relative">
        <div
          className={cn(
            "absolute left-4 top-1/2 -translate-y-1/2 transition-colors",
            isFocused ? "text-primary" : "text-muted-foreground"
          )}
        >
          <Youtube className="h-5 w-5" />
        </div>
        
        <Input
          type="url"
          placeholder="https://www.youtube.com/watch?v=..."
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          disabled={disabled}
          className={cn(
            "pl-12 pr-12 h-14 text-base",
            isValid === true && "border-green-500/50 focus-visible:ring-green-500/30",
            isValid === false && "border-red-500/50 focus-visible:ring-red-500/30"
          )}
        />
        
        {value && (
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            className="absolute right-4 top-1/2 -translate-y-1/2"
          >
            {isValid ? (
              <Check className="h-5 w-5 text-green-500" />
            ) : (
              <AlertCircle className="h-5 w-5 text-red-500" />
            )}
          </motion.div>
        )}
      </div>
      
      {/* Validation message */}
      {value && !isValid && (
        <motion.p
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-sm text-red-400 flex items-center gap-2"
        >
          <AlertCircle className="h-4 w-4" />
          Please enter a valid YouTube URL
        </motion.p>
      )}
      
      {/* Thumbnail preview */}
      {videoId && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-4 rounded-xl overflow-hidden border border-border"
        >
          <img
            src={getYouTubeThumbnail(videoId, 'mqdefault')}
            alt="Video thumbnail"
            className="w-full h-auto"
            onError={(e) => {
              e.target.src = getYouTubeThumbnail(videoId, 'default');
            }}
          />
        </motion.div>
      )}
    </div>
  );
}

export default URLInput;
