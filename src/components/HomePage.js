import React, { useState } from 'react';
import { Play, TrendingUp, Brain, Zap, AlertCircle } from 'lucide-react';

const HomePage = ({ onAnalyze }) => {
  const [url, setUrl] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = () => {
    setError('');
    const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com\/watch\?v=|youtu\.be\/)[\w-]+/;
    if (!youtubeRegex.test(url)) {
      setError('Please enter a valid YouTube URL');
      return;
    }
    onAnalyze(url);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 via-purple-700 to-purple-500">
      {/* Header */}
      <header className="bg-purple-950 shadow-lg sticky top-0 z-50">
        {/* ... (same as original) */}
      </header>

      {/* Main content */}
      <main className="max-w-6xl mx-auto px-4 py-16">
        {/* ... (same as original) */}
      </main>

      {/* Footer */}
      <footer className="bg-purple-950 text-purple-200 py-8 mt-16">
        <div className="max-w-6xl mx-auto px-4 text-center">
          <p>&copy; 2025 YouTube Comment Analyzer. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;