// src/pages/Home.jsx
import React, { useState } from 'react';
import { motion } from 'framer-motion';
import axios from 'axios';
import ResultView from '../components/ResultView';
import { FiUpload, FiAlertCircle, FiInfo } from 'react-icons/fi';

export default function Home() {
  const [text, setText] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showGuide, setShowGuide] = useState(true);

  async function analyze() {
    setLoading(true);
    try {
      const res = await axios.post('http://127.0.0.1:8000/analyze', { text });
      setResult(res.data);
    } catch (e) {
      alert('API error: ' + (e?.message || e));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen p-6 md:p-12">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-7xl mx-auto"
      >
        <header className="flex items-center justify-between mb-12">
          <h1 className="text-4xl font-bold flex items-center gap-3">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-primary-600">
              🧠 FakeNews AI
            </span>
          </h1>
        </header>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Input Card */}
          <motion.div
            className="glassmorphism rounded-xl p-6"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
          >
            <h2 className="text-2xl font-semibold mb-4">Analyze Content</h2>
            <div className="space-y-4">
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder="Paste article text or URL..."
                className="w-full h-48 p-4 rounded-lg bg-dark-900/50 border border-dark-700/50 text-gray-100 placeholder-gray-500 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <div className="flex items-center gap-4">
                <button
                  onClick={analyze}
                  disabled={loading}
                  className="button-glow"
                >
                  <span className="relative">
                    {loading ? 'Analyzing...' : 'Check Credibility'}
                  </span>
                </button>
                <button className="p-3 rounded-lg border border-dark-700/50 hover:bg-dark-700/50 transition-colors">
                  <FiUpload className="w-5 h-5" />
                </button>
              </div>
            </div>
          </motion.div>

          {/* Result Card */}
          {result && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
            >
              <ResultView result={result} />
            </motion.div>
          )}
        </div>
      </motion.div>
    </div>
  );
}
