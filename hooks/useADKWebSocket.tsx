import { useEffect, useRef, useState, useCallback } from "react";
import { useConnectionId } from "@/lib/connection-context";

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
  onTextMessage: (
    textChunk: string,
    isFinal?: boolean,
    isPartial?: boolean,
    role?: "user" | "assistant",
    traceId?: string
  ) => void;
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
  let binary = "";
  for (let i = 0; i < uint8.length; i++) {
    binary += String.fromCharCode(uint8[i]);
  }
  return btoa(binary);
}

export function useADKWebSocket({
  onTextMessage,
  onAudioMessage,
  onTurnComplete,
  isAudioEnabled = false,
  setIsAudioEnabled,
}: Props) {
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const currentUtterance = useRef<HTMLAudioElement | null>(null);
  const reconnectTimeout = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_DELAY = 2000; // 2 seconds
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

  // Get the selected connection ID from global context
  const connectionId = useConnectionId();
  
  // Update callbacksRef to use current props
  const callbacksRef = useRef({
    onTextMessage,
    onAudioMessage,
    onTurnComplete,
    isAudioEnabled,
    setIsAudioEnabled,
  });

  // Keep callbacks updated
  useEffect(() => {
    callbacksRef.current = {
      onTextMessage,
      onAudioMessage,
      onTurnComplete,
      isAudioEnabled,
      setIsAudioEnabled,
    };
  }, [onTextMessage, onAudioMessage, onTurnComplete, isAudioEnabled, setIsAudioEnabled]);

  // Add handler for assistant messages
  const handleAssistantMessage = useCallback((message: string) => {
    console.log("[WS] Adding assistant message to history:", message);
    const assistantMessage: Message = { role: "assistant", content: message };
    conversationHistory.current = [...conversationHistory.current, assistantMessage];
    console.log("[WS] Updated conversation history:", conversationHistory.current);
  }, []);

  // Add ref for ping interval
  const pingIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Generate a new session ID
  const generateSessionId = () => {
    const timestamp = new Date().toISOString()
      .replace(/[-:]/g, '')  // Remove dashes and colons
      .split('.')[0];        // Remove milliseconds
    const randomHex = Array.from(crypto.getRandomValues(new Uint8Array(2)))
      .map(b => b.toString(16).padStart(2, '0'))
      .join('');
    return `${timestamp}_${randomHex}`;
  };

  // Initialize with a new session ID
  const [sessionId, setSessionId] = useState(() => generateSessionId());

  const isConnectingRef = useRef(false);

  const connect = useCallback(() => {
    if (isConnectingRef.current) {
      console.log("[WS] Skipping connect: already connecting");
      return;
    }
    if (ws.current?.readyState === WebSocket.OPEN) {
      console.log("[WS] Already connected, skipping connect");
      return;
    }
    isConnectingRef.current = true;

    const wsUrl = `ws://localhost:8000/ws/${sessionId}?connection_id=${connectionId}`;
    console.log("[WS] Attempting to connect to:", wsUrl);
    
    try {
      const socket = new WebSocket(wsUrl);
      ws.current = socket;

      socket.onopen = () => {
        console.log("[WS] Connected successfully with session:", sessionId);
        socket.send(JSON.stringify({
          type: "init",
          data: "Hello from client!"
        }));
        setIsConnected(true);
        reconnectAttempts.current = 0;
        
        
        // Setup ping interval
        pingIntervalRef.current = setInterval(() => {
          if (socket.readyState === WebSocket.OPEN) {
            socket.send(JSON.stringify({ type: "ping" }));
          }
        }, 30000);
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("[WS] Received message:", data);

          if (data.mime_type === "text/plain") {
            console.log("[WS] Processing text message:", data);
            
            // Stop any ongoing TTS when receiving a new message
            stopTTS();
            
            onTextMessage(
              data.data,
              data.turn_complete,
              data.is_partial,
              "assistant",
              data.traceId
            );
            
            // Only add complete messages to history
            if (data.turn_complete && !data.is_partial) {
              console.log("[WS] Adding complete message to history:", data.data);
              handleAssistantMessage(data.data);
            }
            
            if (data.is_speech && callbacksRef.current.isAudioEnabled && 'speechSynthesis' in window) {
              if (!data.is_partial) {
                console.log("[WS] Fetching TTS from server:", data.data);
                fetch("http://localhost:8000/speak", {
                  method: "POST",
                  headers: {
                    "Content-Type": "application/json",
                  },
                  body: JSON.stringify({ text: data.data }),
                })
                  .then((res) => {
                    if (!res.ok) throw new Error("TTS failed");
                    return res.blob();
                  })
                  .then((blob) => {
                    const audioUrl = URL.createObjectURL(blob);
                    const audio = new Audio(audioUrl);
                    currentUtterance.current = audio;
                    audio.play();
                  })
                  .catch((err) => {
                    console.error("TTS playback error:", err);
                  });
              }
            }
          }

          if (data.turn_complete) {
            console.log("[WS] Turn complete, processing state:", isProcessing);
            setIsProcessing(false);
            onTurnComplete?.();
          }
        } catch (error) {
          console.error("[WS] Error processing message:", error);
        }
      };

      socket.onerror = (err) => {
        console.error("[WS] WebSocket error:", err);
        setIsConnected(false);
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }
      };

      socket.onclose = (event) => {
        console.log("[WS] Connection closed:", event);
        setIsConnected(false);
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }
        
        // Attempt to reconnect
        if (reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttempts.current += 1;
          setTimeout(() => {
            console.log(`[WS] Attempting to reconnect (${reconnectAttempts.current}/${MAX_RECONNECT_ATTEMPTS})`);
            connect();
          }, RECONNECT_DELAY);
        }
      };
    } catch (error) {
      console.error("[WS] Failed to create WebSocket:", error);
      setIsConnected(false);
    }
  }, [connectionId, sessionId, onTextMessage, onAudioMessage, onTurnComplete]);
  const waitForSocketOpen = (socket: WebSocket): Promise<void> => {
    return new Promise((resolve, reject) => {
      if (socket.readyState === WebSocket.OPEN) {
        resolve();
      } else {
        socket.addEventListener("open", () => resolve(), { once: true });
        socket.addEventListener("error", reject, { once: true });
      }
    });
  };
  const sendMessage = useCallback(async (message: any) => {
    const socket = ws.current;
    console.log("[WS] Attempting to send message:", message);
    console.log("[WS] Current WebSocket state:", socket?.readyState);
  
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      console.warn("[WS] Socket not ready, waiting for open...");
  
      try {
        await waitForSocketOpen(socket!);
        console.log("[WS] Socket now open, sending...");
        socket!.send(JSON.stringify(message));
      } catch (err) {
        console.error("[WS] Failed to send, socket did not open:", err);
      }
  
      return;
    }
  
    // ✅ Socket is open, send immediately
    socket.send(JSON.stringify(message));
  }, []);

  // Add function to stop TTS
  const stopTTS = useCallback(() => {
    // Stop current audio playback
    if (currentUtterance.current) {
      currentUtterance.current.pause();
      currentUtterance.current.currentTime = 0; // Reset to beginning
      currentUtterance.current = null;
    }
  }, []);

  // Watch for audio enabled changes and stop TTS when disabled
  useEffect(() => {
    if (!callbacksRef.current.isAudioEnabled) {
      stopTTS();
    }
  }, [callbacksRef.current.isAudioEnabled, stopTTS]);

  const sendUserMessage = useCallback(async (message: string) => {
    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
      console.error("[WS] WebSocket not connected");
      return;
    }

    // Stop any ongoing TTS when sending a new message
    stopTTS();

    try {
      const messageData = {
        mime_type: "text/plain",
        data: message,
        source: "user"
      };
      
      // Add message to conversation history
      const userMessage: Message = { role: "user", content: message };
    console.log("[WS] Adding message to history:", userMessage);
    console.log("[WS] Previous history:", conversationHistory.current);
    
    const updatedHistory = [...conversationHistory.current, userMessage];
    console.log("[WS] Updated history to send:", updatedHistory);
    
      // Send the message
      ws.current.send(JSON.stringify(messageData));
    
    // Only update history after successful send
    conversationHistory.current = updatedHistory;
    console.log("[WS] History updated:", conversationHistory.current);
    } catch (error) {
      console.error("[WS] Failed to send message:", error);
    }
  }, [stopTTS]);

  // Connect when component mounts or when sessionId/connectionId changes
  useEffect(() => {
    connect();
    return () => {
      if (pingIntervalRef.current) {
        clearInterval(pingIntervalRef.current);
      }
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [connect, sessionId, connectionId]);

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
            console.log("[Speech] Added to final transcript:", finalTranscript.trim());
        }
        interimTranscriptRef.current = interimTranscript;
        console.log("[Speech] Current interim transcript:", interimTranscript);
        
        // Only update UI with transcription, don't send to backend yet
        const displayText = (interimTranscriptRef.current + ' ' + finalTranscriptRef.current).trim();
        console.log("[Speech] Display text:", displayText);
        // Show what user is saying in real-time, but mark as partial
        callbacksRef.current.onTextMessage(displayText, false, true, "user");
      };

      recognition.onerror = (event) => {
        console.error("[Speech] Recognition error:", event.error);
        if (event.error === 'no-speech') {
          console.log("[Speech] No speech detected, restarting recognition");
          // Restart recognition if no speech is detected
          recognition.stop();
          recognition.start();
        }
      };

      recognition.onend = () => {
        console.log("[Speech] Recognition ended");
        console.log("[Speech] Manual stop:", stoppedManuallyRef.current);
        console.log("[Speech] Final transcript:", finalTranscriptRef.current);
        
        // Only send the message if we stopped manually (user pressed stop)
        if (stoppedManuallyRef.current && finalTranscriptRef.current.trim()) {
            const finalText = finalTranscriptRef.current.trim();
            finalTranscriptRef.current = "";
            interimTranscriptRef.current = "";
            stoppedManuallyRef.current = false;
            
            // Use sendUserMessage instead of sendMessage
            sendUserMessage(finalText);
        } else {
            console.log("[Speech] Not sending - Manual stop:", stoppedManuallyRef.current, "Final transcript:", finalTranscriptRef.current);
        }
        
        // Always restart recognition if still recording
        if (isRecording) {
            console.log("[Speech] Still recording, restarting recognition");
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
      
      setIsRecording(true);
      
      // Send recording state to server using sendMessage instead of direct ws access
      sendMessage({
        mime_type: "audio/state",
        data: "",
        source: "audio",
        is_recording: true
      });
      
      console.log("[Audio] Started recording");
    } catch (err) {
      console.error("[Audio] Failed to start recording:", err);
      stopListening(); // Clean up if there's an error
    }
  }, [isRecording, sendMessage, sendUserMessage]);

  const stopListening = useCallback(() => {
    setIsRecording(false);
    stoppedManuallyRef.current = true; // Only set this here, on explicit user action

    // Send recording state to server using sendMessage
    sendMessage({
      mime_type: "audio/state",
      data: "",
      source: "audio",
      is_recording: false
    });

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
  }, [sendMessage]);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      stopListening();
    };
  }, [stopListening]);

  // Function to start a new session
  const startNewSession = useCallback(() => {
    const newSessionId = generateSessionId();
    setSessionId(newSessionId);
    localStorage.setItem(`currentSession_${connectionId}`, newSessionId);
    
    // Clear conversation history for new session
    conversationHistory.current = [];
    localStorage.removeItem('conversationHistory');
    
    // Reconnect with new session
    if (ws.current) {
      ws.current.close();
    }
  }, [connectionId, connect, generateSessionId]);

  return { 
    sendUserMessage, 
    isConnected, 
    startListening, 
    stopListening, 
    isRecording,
    isAudioEnabled,
    setIsAudioEnabled: setIsAudioEnabled || (() => {}),
    stopTTS,
    sessionId,
    startNewSession
  };
}
