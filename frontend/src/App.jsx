// src/App.jsx
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import Home from './pages/Home';
import Admin from './pages/Admin';

function Navbar() {
  return (
    <nav className="fixed top-0 left-0 right-0 z-50 bg-dark-900/80 backdrop-blur-lg border-b border-dark-700/50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-primary-600">
              🧠 FakeNews AI
            </Link>
          </div>
          <div className="hidden md:block">
            <div className="ml-10 flex items-baseline space-x-4">
              <Link to="/" className="nav-link">Home</Link>
              <Link to="/insights" className="nav-link">Insights</Link>
              <Link to="/about" className="nav-link">About</Link>
              <Link to="/admin" className="nav-link">Admin</Link>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}

function InsightsPage() {
  return (
    <div className="pt-20 p-6">
      <h2 className="text-2xl font-bold mb-4">Insights</h2>
      <p>Coming soon: Trends and statistics about fake news detection.</p>
    </div>
  );
}

function AboutPage() {
  return (
    <div className="pt-20 p-6">
      <h2 className="text-2xl font-bold mb-4">About</h2>
      <p>Powered by advanced NLP models and machine learning techniques.</p>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <div className="min-h-screen bg-dark-900 text-gray-100">
        <Navbar />
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
        >
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/insights" element={<InsightsPage />} />
            <Route path="/about" element={<AboutPage />} />
            <Route path="/admin" element={<Admin />} />
          </Routes>
        </motion.div>
      </div>
    </Router>
  );
}
