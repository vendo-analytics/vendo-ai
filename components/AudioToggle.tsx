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
          : 'bg-gray-500 hover:bg-gray-600'
      }`}
      title={isEnabled ? 'Disable text-to-speech' : 'Enable text-to-speech'}
    >
      {isEnabled ? (
        // Clean TTS enabled icon - speaker with sound waves
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 24 24">
          <path d="M3 9v6h4l5 5V4L7 9H3z"/>
          <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02z"/>
          <path d="M14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z"/>
        </svg>
      ) : (
        // Clean TTS disabled icon - speaker with slash
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-white" fill="currentColor" viewBox="0 0 24 24">
          <path d="M3 9v6h4l5 5V4L7 9H3z"/>
          <path d="M16.5 12c0-1.77-1.02-3.29-2.5-4.03v2.21l2.45 2.45c.03-.2.05-.41.05-.63z"/>
          <path d="M19 12c0 .94-.2 1.82-.54 2.64l1.51 1.51C20.63 14.91 21 13.5 21 12c0-4.28-2.99-7.86-7-8.77v2.06c2.89.86 5 3.54 5 6.71z"/>
          <path d="M4.27 3L3 4.27l9 9v.28c0 .55-.45 1-1 1s-1-.45-1-1V7.73L16.25 14c-.29.15-.6.25-.92.31v2.06c.58-.08 1.12-.23 1.64-.46l1.51 1.51L19.73 21 21 19.73 4.27 3z"/>
        </svg>
      )}
    </button>
  );
}; 