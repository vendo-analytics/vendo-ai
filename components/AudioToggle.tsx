import React from 'react';

interface AudioToggleProps {
  isEnabled?: boolean;
  onToggle: () => void;
}

export const AudioToggle: React.FC<AudioToggleProps> = ({ isEnabled = false, onToggle }) => {
  console.log("[AudioToggle] Rendering with isEnabled:", isEnabled);

  const handleToggle = () => {
    console.log("[AudioToggle] Button clicked, current state:", isEnabled);
    if (typeof onToggle === 'function') {
      console.log("[AudioToggle] Calling onToggle function");
      onToggle();
    } else {
      console.error("[AudioToggle] onToggle is not a function:", onToggle);
    }
  };

  return (
    <button
      onClick={handleToggle}
      className={`p-2 rounded-full transition-colors ${
        isEnabled 
          ? 'bg-green-500 hover:bg-green-600' 
          : 'bg-red-500 hover:bg-red-600'
      }`}
      title={isEnabled ? 'Disable audio responses' : 'Enable audio responses'}
    >
      {isEnabled ? (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.536 8.464a5 5 0 010 7.072m2.828-9.9a9 9 0 010 12.728M5.586 15.536a5 5 0 001.414 1.414m2.828-9.9a9 9 0 012.728-2.728" />
        </svg>
      ) : (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.586 15.536a5 5 0 001.414 1.414m2.828-9.9a9 9 0 012.728-2.728" />
        </svg>
      )}
    </button>
  );
}; 