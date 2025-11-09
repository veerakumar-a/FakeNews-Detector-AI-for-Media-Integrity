import React from 'react';
import { motion } from 'framer-motion';

export default function LoadingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 bg-dark-900/80 backdrop-blur-sm flex items-center justify-center z-50"
    >
      <div className="text-center">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            rotate: [0, 360]
          }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          className="w-16 h-16 border-4 border-primary-500 border-t-transparent rounded-full mb-4"
        />
        <p className="text-primary-400 text-lg">Analyzing content...</p>
      </div>
    </motion.div>
  );
}