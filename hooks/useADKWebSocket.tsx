import { useEffect, useRef, useState, useCallback } from "react";

// Add Web Speech API type definitions
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
  interpretation: any;
}

interface SpeechRecognitionResultList {
  length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
  isFinal: boolean;
  length: number;
  item(index: number): SpeechRecognitionAlternative;
  [index: number]: SpeechRecognitionAlternative;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

interface SpeechRecognitionError extends Event {
  error: string;
  message: string;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: (event: SpeechRecognitionEvent) => void;
  onerror: (event: SpeechRecognitionError) => void;
  onend: () => void;
  start(): void;
  stop(): void;
  abort(): void;
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognition;
  prototype: SpeechRecognition;
}

declare global {
  interface Window {
    SpeechRecognition: SpeechRecognitionConstructor;
    webkitSpeechRecognition: SpeechRecognitionConstructor;
  }
}

interface Props {
  onTextMessage: (textChunk: string, isFinal?: boolean, isPartial?: boolean, role?: "user" | "assistant") => void;
  onAudioMessage?: (audioBuffer: ArrayBuffer) => void;
  onTurnComplete?: () => void;
  isAudioEnabled?: boolean;
  setIsAudioEnabled?: (enabled: boolean) => void;
}

interface Message {
  role: "user" | "assistant";
  content: string;
}

// Helper to safely encode large Uint8Arrays to base64
function uint8ToBase64(uint8: Uint8Array) {
  let result = '';
  const CHUNK_SIZE = 0x4000; // 16k
  for (let i = 0; i < uint8.length; i += CHUNK_SIZE) {
    result += String.fromCharCode.apply(null, uint8.subarray(i, i + CHUNK_SIZE) as any);
  }
  return btoa(result);
}

export function useADKWebSocket({
  onTextMessage,
  onAudioMessage,
  onTurnComplete,
  isAudioEnabled = true,
  setIsAudioEnabled,
}: Props) {
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const currentUtterance = useRef<SpeechSynthesisUtterance | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout>();
  const reconnectAttempts = useRef(0);
  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_DELAY = 1000; // 1 second
  const audioContext = useRef<AudioContext | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [isRecording, setIsRecording] = useState(false);
  const audioContextRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const interimMessageRef = useRef<string>("");
  const stoppedManuallyRef = useRef(false);
  const conversationHistory = useRef<Message[]>([]);
  const bufferedTranscriptRef = useRef<string>("");
  const audioChunksRef = useRef<Int16Array[]>([]);
  const finalTranscriptRef = useRef<string>("");
  const interimTranscriptRef = useRef<string>("");
  const assistantBufferRef = useRef<string>("");

  // Store callbacks in refs to prevent unnecessary reconnections
  const callbacksRef = useRef({
    onTextMessage,
    onAudioMessage,
    onTurnComplete,
    isAudioEnabled,
    setIsAudioEnabled,
  });

  // Update callbacks without triggering reconnection
  useEffect(() => {
    callbacksRef.current = {
      onTextMessage,
      onAudioMessage,
      onTurnComplete,
      isAudioEnabled,
      setIsAudioEnabled,
    };
    console.log("[WS] Audio state updated:", isAudioEnabled);
  }, [onTextMessage, onAudioMessage, onTurnComplete, isAudioEnabled, setIsAudioEnabled]);

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      return;
    }
    const userId = "001"; // You can randomize or parametrize this
    const sessionId = "001"; // You can randomize or parametrize this
    const wsUrl = `ws://localhost:8000/ws/${sessionId}?user_id=${userId}&is_audio=false`;
    
    try {
      const socket = new WebSocket(wsUrl);
      ws.current = socket;

      // Add ping/pong to keep connection alive
      const pingInterval = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ type: "ping" }));
        }
      }, 30000); // Send ping every 30 seconds

      socket.onopen = () => {
        console.log("[WS] Connected.");
        setIsConnected(true);
        reconnectAttempts.current = 0;
        // Send initial conversation history when connecting
        if (conversationHistory.current.length > 0) {
          console.log("0");
          socket.send(JSON.stringify({
            mime_type: "text/plain",
            data: "",
            history: conversationHistory.current
          }));
        }
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("[WS] Received message:", data);

          // Handle text messages first
          if (data.mime_type === "text/plain") {
            // Let the Chat component handle the text display
            onTextMessage(data.data, data.turn_complete, data.is_partial, "assistant");
            
            // If audio is enabled and this message should be spoken
            if (data.is_speech && callbacksRef.current.isAudioEnabled && 'speechSynthesis' in window) {
              // Only speak complete messages, not partial ones
              if (!data.is_partial) {
                console.log("[WS] Speaking text:", data.data);
                // Cancel any ongoing speech
                if (currentUtterance.current) {
                  window.speechSynthesis.cancel();
                }
                
                const utterance = new SpeechSynthesisUtterance(data.data);
                currentUtterance.current = utterance;
                window.speechSynthesis.speak(utterance);
              }
            } else {
              console.log("[WS] Audio disabled or not marked for speech, not speaking");
            }
          } else if (data.mime_type === "text/speech" && callbacksRef.current.isAudioEnabled) {
            // Only handle speech if audio is enabled and we haven't already spoken this text
            if ('speechSynthesis' in window && data.data !== currentUtterance.current?.text) {
              console.log("[WS] Speaking text from speech message:", data.data);
              // Cancel any ongoing speech
              if (currentUtterance.current) {
                window.speechSynthesis.cancel();
              }
              
              const utterance = new SpeechSynthesisUtterance(data.data);
              currentUtterance.current = utterance;
              window.speechSynthesis.speak(utterance);
            }
          } else if (data.mime_type === "audio/pcm") {
            // Only handle audio messages if audio is enabled
            if (callbacksRef.current.isAudioEnabled) {
              console.log("[WS] Playing PCM audio");
              const audioData = atob(data.data);
              const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
              const audioBuffer = audioContext.createBuffer(1, audioData.length, 44100);
              const channelData = audioBuffer.getChannelData(0);
              
              for (let i = 0; i < audioData.length; i++) {
                channelData[i] = (audioData.charCodeAt(i) - 128) / 128.0;
              }
              
              const source = audioContext.createBufferSource();
              source.buffer = audioBuffer;
              source.connect(audioContext.destination);
              source.start();
            } else {
              console.log("[WS] Audio disabled, not playing PCM");
            }
          }

          // Handle turn_complete after processing the message content
          if (data.turn_complete) {
            console.log("[WS] Turn complete");
            setIsProcessing(false);
            onTurnComplete?.();
          }
        } catch (error) {
          console.error("[WS] Error processing message:", error);
        }
      };

      socket.onerror = (err) => {
        console.error("[WS] Error:", err);
        setIsConnected(false);
        clearInterval(pingInterval);
      };

      socket.onclose = () => {
        console.log("[WS] Disconnected.");
        setIsConnected(false);
        clearInterval(pingInterval);
        
        // Only attempt to reconnect if we're not intentionally closing
        if (!isRecording && reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttempts.current += 1;
          console.log(`[WS] Attempting to reconnect (${reconnectAttempts.current}/${MAX_RECONNECT_ATTEMPTS})...`);
          reconnectTimeout.current = setTimeout(connect, RECONNECT_DELAY * reconnectAttempts.current);
        } else {
          console.error("[WS] Max reconnection attempts reached or recording stopped.");
        }
      };
    } catch (err) {
      console.error("[WS] Failed to create WebSocket:", err);
      setIsConnected(false);
    }
  }, []);

  // Clean up on unmount
  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
      if (ws.current) {
        ws.current.close();
      }
      if (audioContext.current) {
        audioContext.current.close();
      }
    };
  }, [connect]);

  // Persist conversation history to localStorage
  useEffect(() => {
    const saveHistory = () => {
      localStorage.setItem('conversationHistory', JSON.stringify(conversationHistory.current));
    };

    // Load history on mount
    const savedHistory = localStorage.getItem('conversationHistory');
    if (savedHistory) {
      try {
        conversationHistory.current = JSON.parse(savedHistory);
      } catch (err) {
        console.error("[WS] Failed to load conversation history:", err);
      }
    }

    // Save history when it changes
    window.addEventListener('beforeunload', saveHistory);
    return () => {
      window.removeEventListener('beforeunload', saveHistory);
      saveHistory(); // Save one last time
    };
  }, []);

  const sendUserMessage = useCallback((text: string) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      // Add user message to conversation history
      conversationHistory.current.push({ role: "user", content: text });
      console.log("[WS] Sending message with history:", conversationHistory.current);
      
      ws.current.send(JSON.stringify({
        mime_type: "text/plain",
        data: text,
        history: conversationHistory.current
      }));
    } else {
      console.error("[WS] Cannot send message: WebSocket is not connected");
    }
  }, []);

  const startListening = useCallback(async () => {
    // Extra safety: reset manual stop flag at the start of every recording session
    stoppedManuallyRef.current = false;
    // Clear any buffered audio chunks and transcripts
    audioChunksRef.current = [];
    finalTranscriptRef.current = "";
    interimTranscriptRef.current = "";
    
    // Stop any ongoing speech synthesis
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
    }

    if (isRecording) {
      // Only allow user to stop recording by pressing the mic button
      return;
    }

    try {
      // Initialize speech recognition
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) {
        throw new Error("Speech recognition not supported in this browser");
      }

      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'en-US';

      recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          } else {
            interimTranscript += transcript;
          }
        }
        
        // Update our refs with the latest transcripts
        if (finalTranscript) {
          finalTranscriptRef.current += finalTranscript.trim() + ' ';
        }
        interimTranscriptRef.current = interimTranscript;
        
        // Only update UI with transcription, don't send to backend yet
        const displayText = (interimTranscriptRef.current + ' ' + finalTranscriptRef.current).trim();
        // Show what user is saying in real-time, but mark as partial
        callbacksRef.current.onTextMessage(displayText, false, true, "user");
      };

      recognition.onerror = (event) => {
        console.error("[Speech] Recognition error:", event.error);
        if (event.error === 'no-speech') {
          // Restart recognition if no speech is detected
          recognition.stop();
          recognition.start();
        }
      };

      recognition.onend = () => {
        // Only send the message if we stopped manually (user pressed stop)
        if (stoppedManuallyRef.current && finalTranscriptRef.current.trim()) {
          const finalText = finalTranscriptRef.current.trim();
          finalTranscriptRef.current = "";
          interimTranscriptRef.current = "";
          stoppedManuallyRef.current = false;
          
          if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            conversationHistory.current = [];
            try {
              // Send the complete transcription as a regular text message
              console.log("[WS] Sending complete transcription:", finalText);
              ws.current.send(JSON.stringify({
                mime_type: "text/plain",
                data: finalText,
                history: conversationHistory.current
              }));
              
              // Remove audio sending since we're treating it as text
              // audioChunksRef.current = [];
            } catch (err) {
              console.error("[WS] Error sending finalText to server with empty history:", err);
            }
          }
        }
        // Always restart recognition if still recording
        if (isRecording) {
          recognition.start();
        }
      };

      recognition.start();

      // Get audio stream
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;
      
      // Create audio context and analyzer
      const audioContext = new AudioContext();
      audioContextRef.current = audioContext;
      const source = audioContext.createMediaStreamSource(stream);
      sourceRef.current = source;
      const processor = audioContext.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;
      
      source.connect(processor);
      processor.connect(audioContext.destination);
      
      processor.onaudioprocess = (e) => {
        const inputData = e.inputBuffer.getChannelData(0);
        // Convert Float32Array to Int16Array (PCM format)
        const pcmData = new Int16Array(inputData.length);
        for (let i = 0; i < inputData.length; i++) {
          pcmData[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7FFF;
        }
        
        // Buffer the audio chunk instead of sending immediately
        audioChunksRef.current.push(pcmData);
      };
      
      setIsRecording(true);
      // Send recording state to server
      if (ws.current?.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({
          mime_type: "audio/state",
          data: "",
          source: "audio",
          is_recording: true
        }));
      }
      console.log("[Audio] Started recording");
    } catch (err) {
      console.error("[Audio] Failed to start recording:", err);
      stopListening(); // Clean up if there's an error
    }
  }, [isRecording, connect, sendUserMessage]);

  const stopListening = useCallback(() => {
    setIsRecording(false);
    stoppedManuallyRef.current = true; // Only set this here, on explicit user action

    // Send recording state to server
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        mime_type: "audio/state",
        data: "",
        source: "audio",
        is_recording: false
      }));

      // Remove audio chunk sending since we're treating it as text
      audioChunksRef.current = [];
    }

    // If recognition is running, stop it and wait for onend to fire
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    }

    // Stop audio processing
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }
    if (sourceRef.current) {
      sourceRef.current.disconnect();
      sourceRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    console.log("[Audio] Stopped recording");
  }, [connect, sendUserMessage]);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      stopListening();
    };
  }, [stopListening]);

  return { 
    sendUserMessage, 
    isConnected, 
    startListening, 
    stopListening, 
    isRecording,
    isAudioEnabled,
    setIsAudioEnabled: setIsAudioEnabled || (() => {}) // Provide a no-op function if not provided
  };
}
