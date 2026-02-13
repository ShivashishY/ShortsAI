import React from "react";
import { motion } from "framer-motion";
import { Film } from "lucide-react";
import { cn } from "@/lib/utils";

const CLIP_COUNT_OPTIONS = [
  { value: 5, label: "5 clips", description: "Quick batch" },
  { value: 10, label: "10 clips", description: "Standard" },
  { value: 15, label: "15 clips", description: "Maximum" },
];

/**
 * Clip count selector component with visual options
 */
export function ClipCountSelector({ value, onChange, disabled }) {
  return (
    <div className="space-y-3">
      <label className="text-sm font-medium text-foreground flex items-center gap-2">
        <Film className="h-4 w-4 text-primary" />
        Number of Clips
      </label>
      
      <div className="grid grid-cols-3 gap-3">
        {CLIP_COUNT_OPTIONS.map((option) => (
          <motion.button
            key={option.value}
            type="button"
            disabled={disabled}
            onClick={() => onChange(option.value)}
            className={cn(
              "relative p-4 rounded-xl border-2 transition-all duration-200",
              "hover:border-primary/50 hover:bg-primary/5",
              "disabled:opacity-50 disabled:cursor-not-allowed",
              value === option.value
                ? "border-primary bg-primary/10 shadow-lg shadow-primary/10"
                : "border-border bg-card"
            )}
            whileHover={{ scale: disabled ? 1 : 1.02 }}
            whileTap={{ scale: disabled ? 1 : 0.98 }}
          >
            {/* Selection indicator */}
            {value === option.value && (
              <motion.div
                layoutId="clip-count-selector"
                className="absolute inset-0 rounded-xl border-2 border-primary"
                transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
              />
            )}
            
            <div className="relative z-10 text-center">
              <span
                className={cn(
                  "text-2xl font-bold block",
                  value === option.value ? "text-primary" : "text-foreground"
                )}
              >
                {option.value}
              </span>
              <span className="text-xs text-muted-foreground mt-1 block">
                {option.description}
              </span>
            </div>
          </motion.button>
        ))}
      </div>
      
      <p className="text-xs text-muted-foreground">
        Choose how many clips to generate from your video
      </p>
    </div>
  );
}

export default ClipCountSelector;
