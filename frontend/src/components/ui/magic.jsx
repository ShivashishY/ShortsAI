import React from "react";
import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

/**
 * Animated gradient background orb
 */
export function GradientOrb({ className }) {
  return (
    <motion.div
      className={cn(
        "absolute rounded-full blur-3xl opacity-30",
        className
      )}
      animate={{
        scale: [1, 1.2, 1],
        opacity: [0.3, 0.5, 0.3],
      }}
      transition={{
        duration: 8,
        repeat: Infinity,
        ease: "easeInOut",
      }}
    />
  );
}

/**
 * Animated grid background
 */
export function GridBackground({ className }) {
  return (
    <div className={cn("absolute inset-0 grid-bg", className)}>
      <div className="absolute inset-0 radial-overlay" />
    </div>
  );
}

/**
 * Sparkle effect component
 */
export function Sparkles({ children, className, sparkleCount = 10 }) {
  const sparkles = React.useMemo(() => {
    return Array.from({ length: sparkleCount }, (_, i) => ({
      id: i,
      size: Math.random() * 4 + 2,
      style: {
        top: `${Math.random() * 100}%`,
        left: `${Math.random() * 100}%`,
        animationDelay: `${Math.random() * 2}s`,
        animationDuration: `${Math.random() * 2 + 1}s`,
      },
    }));
  }, [sparkleCount]);

  return (
    <span className={cn("relative inline-block", className)}>
      {sparkles.map((sparkle) => (
        <span
          key={sparkle.id}
          className="absolute inline-block animate-pulse"
          style={{
            ...sparkle.style,
            width: sparkle.size,
            height: sparkle.size,
            borderRadius: "50%",
            backgroundColor: "rgba(139, 92, 246, 0.8)",
            boxShadow: "0 0 4px rgba(139, 92, 246, 0.8)",
          }}
        />
      ))}
      <span className="relative z-10">{children}</span>
    </span>
  );
}

/**
 * Animated border gradient
 */
export function BorderBeam({ className, size = 200, duration = 12, delay = 0 }) {
  return (
    <div
      className={cn(
        "absolute inset-0 rounded-[inherit] overflow-hidden",
        className
      )}
    >
      <motion.div
        className="absolute inset-0"
        style={{
          background: `linear-gradient(90deg, transparent, rgba(139, 92, 246, 0.5), transparent)`,
          width: `${size}px`,
        }}
        animate={{
          left: ["-200px", "calc(100% + 200px)"],
        }}
        transition={{
          duration,
          repeat: Infinity,
          repeatDelay: 0,
          delay,
          ease: "linear",
        }}
      />
    </div>
  );
}

/**
 * Animated text gradient
 */
export function GradientText({ children, className }) {
  return (
    <span className={cn("gradient-text", className)}>
      {children}
    </span>
  );
}

/**
 * Floating animation wrapper
 */
export function Float({ children, className, delay = 0 }) {
  return (
    <motion.div
      className={className}
      animate={{
        y: [0, -10, 0],
      }}
      transition={{
        duration: 3,
        repeat: Infinity,
        ease: "easeInOut",
        delay,
      }}
    >
      {children}
    </motion.div>
  );
}

/**
 * Fade in animation wrapper
 */
export function FadeIn({ children, className, delay = 0, direction = "up" }) {
  const directions = {
    up: { y: 20 },
    down: { y: -20 },
    left: { x: 20 },
    right: { x: -20 },
  };

  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, ...directions[direction] }}
      animate={{ opacity: 1, x: 0, y: 0 }}
      transition={{
        duration: 0.5,
        delay,
        ease: "easeOut",
      }}
    >
      {children}
    </motion.div>
  );
}

/**
 * Scale in animation wrapper
 */
export function ScaleIn({ children, className, delay = 0 }) {
  return (
    <motion.div
      className={className}
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{
        duration: 0.3,
        delay,
        ease: "easeOut",
      }}
    >
      {children}
    </motion.div>
  );
}

/**
 * Glow effect wrapper
 */
export function Glow({ children, className, color = "purple" }) {
  const colors = {
    purple: "rgba(139, 92, 246, 0.5)",
    pink: "rgba(236, 72, 153, 0.5)",
    blue: "rgba(59, 130, 246, 0.5)",
  };

  return (
    <motion.div
      className={cn("relative", className)}
      whileHover={{
        boxShadow: `0 0 30px ${colors[color]}`,
      }}
      transition={{ duration: 0.3 }}
    >
      {children}
    </motion.div>
  );
}
