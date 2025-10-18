import React, { useState, useEffect } from 'react';

const LoadingState = () => {
  const [step, setStep] = useState(1);

  useEffect(() => {
    const timer = setInterval(() => {
      setStep(s => (s < 3 ? s + 1 : s));
    }, 2000);
    return () => clearInterval(timer);
  }, []);

  return (
    <div className="min-h-screen bg-gradient-to-br from-purple-900 to-purple-600 flex items-center justify-center">
      {/* ... (same as original) */}
    </div>
  );
};

export default LoadingState;