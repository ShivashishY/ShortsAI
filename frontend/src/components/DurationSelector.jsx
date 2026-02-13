import React from "react";
import { motion } from "framer-motion";
import { Clock } from "lucide-react";
import { cn } from "@/lib/utils";

const DURATION_OPTIONS = [
  { value: 30, label: "30s", description: "Quick short" },
  { value: 60, label: "60s", description: "Standard" },
  { value: 90, label: "90s", description: "Extended" },
  { value: 120, label: "2 min", description: "Long clip" },
  { value: 180, label: "3 min", description: "Maximum" },
];

/**
 * Duration selector component with visual options
 */
export function DurationSelector({ value, onChange, disabled }) {
  return (
    <div className="space-y-3">
      <label className="text-sm font-medium text-foreground flex items-center gap-2">
        <Clock className="h-4 w-4 text-primary" />
        Clip Duration
      </label>
      
      <div className="grid grid-cols-5 gap-2 sm:gap-3">
        {DURATION_OPTIONS.map((option) => (
          <motion.button
            key={option.value}
            type="button"
            disabled={disabled}
            onClick={() => onChange(option.value)}
            className={cn(
              "relative p-3 sm:p-4 rounded-xl border-2 transition-all duration-200",
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
                layoutId="duration-selector"
                className="absolute inset-0 rounded-xl border-2 border-primary"
                transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
              />
            )}
            
            <div className="relative z-10 text-center">
              <span
                className={cn(
                  "text-lg sm:text-xl font-bold block",
                  value === option.value ? "text-primary" : "text-foreground"
                )}
              >
                {option.label}
              </span>
              <span className="text-[10px] sm:text-xs text-muted-foreground mt-1 block">
                {option.description}
              </span>
            </div>
          </motion.button>
        ))}
      </div>
      
      <p className="text-xs text-muted-foreground">
        Choose how long each generated clip should be
      </p>
    </div>
  );
}

export default DurationSelector;
