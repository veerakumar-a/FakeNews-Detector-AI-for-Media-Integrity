import React from 'react';
import { motion } from 'framer-motion';

export default function MobileNav({ isOpen, setIsOpen }) {
  return (
    <motion.div
      initial={false}
      animate={isOpen ? { x: 0 } : { x: "100%" }}
      transition={{ type: "spring", stiffness: 300, damping: 30 }}
      className="fixed inset-y-0 right-0 w-64 bg-dark-800 shadow-lg z-50 p-4"
    >
      <div className="flex flex-col h-full">
        <button
          onClick={() => setIsOpen(false)}
          className="self-end p-2"
        >
          ✕
        </button>
        
        <nav className="flex flex-col gap-4 mt-8">
          <a href="/" className="nav-link">Home</a>
          <a href="/insights" className="nav-link">Insights</a>
          <a href="/about" className="nav-link">About</a>
        </nav>

        <div className="mt-auto p-4 bg-dark-900/50 rounded-lg">
          <h3 className="font-semibold mb-2">Quick Tips</h3>
          <ul className="text-sm space-y-2 text-gray-400">
            <li>• Paste full article text for best results</li>
            <li>• Check source credibility with URLs</li>
            <li>• Review highlighted suspicious phrases</li>
          </ul>
        </div>
      </div>
    </motion.div>
  );
}