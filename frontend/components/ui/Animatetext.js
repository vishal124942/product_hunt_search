"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useEffect, useState } from "react";

const searchExamples = [
  "AI tools that launched this week...",
  "Productivity apps built by indie hackers...",
  "Open source dev tools trending today...",
  "Startups revolutionizing remote work...",
  "Early-stage AI agents getting traction...",
];

export default function AnimatedText() {
  const [index, setIndex] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((prev) => (prev + 1) % searchExamples.length);
    }, 3000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="h-10 flex items-center text-lg font-medium text-red-400 text-center animate">
      <AnimatePresence mode="wait">
        <motion.span
          key={searchExamples[index]}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ duration: 0.5 }}
          className="absolute"
        >
          {searchExamples[index]}
        </motion.span>
      </AnimatePresence>
    </div>
  );
}
