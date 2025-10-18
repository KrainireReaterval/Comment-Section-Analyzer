import React, { useState } from 'react';
import HomePage from './components/HomePage';
import LoadingState from './components/LoadingState';
import ReportPage from './components/ReportPage';
import { mockAnalysisData } from './data/mockData';

const App = () => {
  const [state, setState] = useState('home'); // 'home', 'loading', 'report'
  const [data, setData] = useState(null);

  const handleAnalyze = async (url) => {
    setState('loading');
    // Simulate API call
    setTimeout(() => {
      setData(mockAnalysisData);
      setState('report');
    }, 6000);
  };

  const handleBack = () => {
    setState('home');
    setData(null);
  };

  switch (state) {
    case 'loading':
      return <LoadingState />;
    case 'report':
      return <ReportPage data={data} onBack={handleBack} />;
    default:
      return <HomePage onAnalyze={handleAnalyze} />;
  }
};

export default App;