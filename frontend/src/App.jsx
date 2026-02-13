import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Sparkles, 
  Zap, 
  Clock, 
  Video, 
  ArrowRight, 
  Github, 
  RefreshCw,
  AlertTriangle
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { GradientOrb, GridBackground, FadeIn, GradientText, Float } from "@/components/ui/magic";
import URLInput from "@/components/URLInput";
import DurationSelector from "@/components/DurationSelector";
import ClipCountSelector from "@/components/ClipCountSelector";
import VideoPreview from "@/components/VideoPreview";
import { DownloadButton, DownloadAllButton } from "@/components/DownloadButton";
import ProcessingStatus from "@/components/ProcessingStatus";
import { processVideo, getJobStatus } from "@/lib/api";
import { isValidYouTubeUrl, cn, delay } from "@/lib/utils";

const FEATURES = [
  {
    icon: Sparkles,
    title: "AI-Powered Detection",
    description: "Uses advanced AI to find the most engaging moments in your video",
  },
  {
    icon: Video,
    title: "Vertical Format",
    description: "Automatically crops and formats videos for YouTube Shorts (9:16)",
  },
  {
    icon: Clock,
    title: "Flexible Durations",
    description: "Choose between 30 seconds to 3 minutes for your clips",
  },
  {
    icon: Zap,
    title: "Fast Processing",
    description: "Get your shorts ready in minutes, not hours",
  },
];

function App() {
  // Form state
  const [url, setUrl] = useState("");
  const [duration, setDuration] = useState(60);
  const [clipCount, setClipCount] = useState(5);
  
  // Processing state
  const [jobId, setJobId] = useState(null);
  const [status, setStatus] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  
  // Results state
  const [clips, setClips] = useState([]);
  const [selectedClip, setSelectedClip] = useState(null);
  
  // Error state
  const [error, setError] = useState(null);

  // Poll for job status
  const pollJobStatus = useCallback(async (id) => {
    try {
      const result = await getJobStatus(id);
      setStatus(result);
      
      if (result.status === "completed") {
        setClips(result.clips || []);
        setIsProcessing(false);
        if (result.clips && result.clips.length > 0) {
          setSelectedClip(result.clips[0].index);
        }
      } else if (result.status === "failed") {
        setError(result.error || "Processing failed");
        setIsProcessing(false);
      } else {
        // Continue polling
        await delay(2000);
        pollJobStatus(id);
      }
    } catch (err) {
      console.error("Status poll error:", err);
      setError("Lost connection to server");
      setIsProcessing(false);
    }
  }, []);

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!isValidYouTubeUrl(url)) {
      setError("Please enter a valid YouTube URL");
      return;
    }
    
    try {
      setError(null);
      setIsProcessing(true);
      setClips([]);
      setStatus({ status: "queued", progress: 0 });
      
      const result = await processVideo(url, duration, clipCount);
      setJobId(result.jobId);
      
      // Start polling
      pollJobStatus(result.jobId);
    } catch (err) {
      console.error("Submit error:", err);
      setError(err.message || "Failed to start processing");
      setIsProcessing(false);
    }
  };

  // Reset to initial state
  const handleReset = () => {
    setUrl("");
    setDuration(60);
    setClipCount(5);
    setJobId(null);
    setStatus(null);
    setIsProcessing(false);
    setClips([]);
    setSelectedClip(null);
    setError(null);
  };

  const showResults = clips.length > 0 && !isProcessing;

  return (
    <div className="min-h-screen bg-background relative overflow-hidden">
      {/* Background effects */}
      <GridBackground />
      <GradientOrb className="w-[600px] h-[600px] bg-purple-600 -top-40 -left-40" />
      <GradientOrb className="w-[500px] h-[500px] bg-pink-600 -bottom-40 -right-40" />
      
      {/* Header */}
      <header className="relative z-10 border-b border-border/50 backdrop-blur-xl">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Float>
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-purple-600 to-pink-600 flex items-center justify-center shadow-lg shadow-purple-500/20">
                <Video className="w-5 h-5 text-white" />
              </div>
            </Float>
            <span className="font-bold text-lg">
              <GradientText>ShortsAI</GradientText>
            </span>
          </div>
          
          <a
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
            className="text-muted-foreground hover:text-foreground transition-colors"
          >
            <Github className="w-5 h-5" />
          </a>
        </div>
      </header>

      {/* Main content */}
      <main className="relative z-10 container mx-auto px-4 py-8 md:py-16">
        <AnimatePresence mode="wait">
          {!showResults ? (
            <motion.div
              key="input"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="max-w-3xl mx-auto space-y-12"
            >
              {/* Hero section */}
              <FadeIn className="text-center space-y-6">
                <h1 className="text-4xl md:text-6xl font-bold tracking-tight">
                  Transform YouTube Videos into{" "}
                  <GradientText>Viral Shorts</GradientText>
                </h1>
                <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
                  Powered by AI, our tool automatically detects the most engaging moments 
                  in your videos and creates perfect short-form content for YouTube Shorts.
                </p>
              </FadeIn>

              {/* Input form */}
              <FadeIn delay={0.1}>
                <Card className="glass border-border/50">
                  <CardContent className="p-6 md:p-8 space-y-6">
                    <form onSubmit={handleSubmit} className="space-y-6">
                      <URLInput
                        value={url}
                        onChange={setUrl}
                        disabled={isProcessing}
                      />
                      
                      <DurationSelector
                        value={duration}
                        onChange={setDuration}
                        disabled={isProcessing}
                      />

                      <ClipCountSelector
                        value={clipCount}
                        onChange={setClipCount}
                        disabled={isProcessing}
                      />

                      {/* Error message */}
                      {error && !isProcessing && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="p-4 rounded-xl bg-red-500/10 border border-red-500/20 flex items-start gap-3"
                        >
                          <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
                          <p className="text-sm text-red-400">{error}</p>
                        </motion.div>
                      )}

                      {/* Submit button */}
                      {!isProcessing ? (
                        <Button
                          type="submit"
                          variant="gradient"
                          size="xl"
                          className="w-full gap-2"
                          disabled={!isValidYouTubeUrl(url)}
                        >
                          <Sparkles className="w-5 h-5" />
                          Generate Shorts
                          <ArrowRight className="w-5 h-5" />
                        </Button>
                      ) : (
                        <ProcessingStatus
                          status={status?.status || "queued"}
                          progress={status?.progress || 0}
                          message={status?.message}
                          error={status?.error}
                        />
                      )}
                    </form>
                  </CardContent>
                </Card>
              </FadeIn>

              {/* Features grid */}
              {!isProcessing && (
                <FadeIn delay={0.2}>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {FEATURES.map((feature, index) => (
                      <motion.div
                        key={feature.title}
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: 0.1 * index }}
                        className="p-5 rounded-xl bg-card/50 border border-border/50 backdrop-blur-sm card-hover"
                      >
                        <div className="flex items-start gap-4">
                          <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center flex-shrink-0">
                            <feature.icon className="w-5 h-5 text-primary" />
                          </div>
                          <div>
                            <h3 className="font-semibold mb-1">{feature.title}</h3>
                            <p className="text-sm text-muted-foreground">
                              {feature.description}
                            </p>
                          </div>
                        </div>
                      </motion.div>
                    ))}
                  </div>
                </FadeIn>
              )}
            </motion.div>
          ) : (
            <motion.div
              key="results"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="space-y-8"
            >
              {/* Results header */}
              <FadeIn className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h2 className="text-2xl md:text-3xl font-bold">
                    Your Shorts are Ready! 🎉
                  </h2>
                  <p className="text-muted-foreground mt-1">
                    We found {clips.length} engaging moments in your video
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <Button
                    variant="outline"
                    onClick={handleReset}
                    className="gap-2"
                  >
                    <RefreshCw className="w-4 h-4" />
                    New Video
                  </Button>
                  <DownloadAllButton jobId={jobId} clips={clips} />
                </div>
              </FadeIn>

              {/* Clips grid */}
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-6">
                {clips.map((clip, index) => (
                  <FadeIn key={clip.index} delay={index * 0.1}>
                    <div className="space-y-3">
                      <VideoPreview
                        jobId={jobId}
                        clip={clip}
                        isSelected={selectedClip === clip.index}
                        onSelect={setSelectedClip}
                      />
                      <DownloadButton
                        jobId={jobId}
                        clipIndex={clip.index}
                        className="w-full"
                      />
                    </div>
                  </FadeIn>
                ))}
              </div>

              {/* Tips section */}
              <FadeIn delay={0.5}>
                <Card className="glass border-border/50">
                  <CardContent className="p-6">
                    <h3 className="font-semibold mb-3 flex items-center gap-2">
                      <Zap className="w-5 h-5 text-yellow-500" />
                      Pro Tips
                    </h3>
                    <ul className="text-sm text-muted-foreground space-y-2">
                      <li>• Download all clips and choose the best performing ones for your channel</li>
                      <li>• Add captions and trending music to increase engagement</li>
                      <li>• Post at peak hours (12-3 PM and 7-9 PM) for maximum visibility</li>
                      <li>• Use relevant hashtags like #Shorts #Viral #Trending</li>
                    </ul>
                  </CardContent>
                </Card>
              </FadeIn>
            </motion.div>
          )}
        </AnimatePresence>
      </main>

      {/* Footer */}
      <footer className="relative z-10 border-t border-border/50 mt-16">
        <div className="container mx-auto px-4 py-6 text-center text-sm text-muted-foreground">
          <p>
            Made with ❤️ using AI • Please use responsibly and respect copyright
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
