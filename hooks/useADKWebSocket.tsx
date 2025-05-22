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
  const currentUtterance = useRef<HTMLAudioElement | null>(null);
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

  // Add handler for assistant messages
  const handleAssistantMessage = useCallback((message: string) => {
    console.log("[WS] handleAssistantMessage called with:", message);
    if (message.trim()) {
      const assistantMessage: Message = { role: "assistant", content: message };
      console.log("[WS] Adding assistant message to history:", assistantMessage);
      console.log("[WS] Previous history:", conversationHistory.current);
      conversationHistory.current = [...conversationHistory.current, assistantMessage];
      console.log("[WS] Updated history:", conversationHistory.current);
    }
  }, []);

  // Update socket.onmessage to use handleAssistantMessage
  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      console.log("[WS] Already connected, skipping connect");
      return;
    }

    const userId = "001"; // You can randomize or parametrize this
    const sessionId = "001"; // You can randomize or parametrize this
    const wsUrl = `ws://localhost:8000/ws/${sessionId}?user_id=${userId}`;
    
    console.log("[WS] Attempting to connect to:", wsUrl);
    
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
        console.log("[WS] Connected successfully");
        setIsConnected(true);
        reconnectAttempts.current = 0;
      };

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          console.log("[WS] Received message:", data);

          if (data.mime_type === "text/plain") {
            console.log("[WS] Processing text message:", data);
            onTextMessage(data.data, data.turn_complete, data.is_partial, "assistant");
            
            // Only add complete messages to history
            if (data.turn_complete && !data.is_partial) {
              console.log("[WS] Adding complete message to history:", data.data);
              handleAssistantMessage(data.data);
            }
            
            if (data.is_speech && callbacksRef.current.isAudioEnabled && 'speechSynthesis' in window) {
              if (!data.is_partial) {
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
        clearInterval(pingInterval);
      };

      socket.onclose = (event) => {
        console.log("[WS] Disconnected with code:", event.code, "reason:", event.reason);
        setIsConnected(false);
        clearInterval(pingInterval);
        
        // Only attempt to reconnect if we're not intentionally closing
        if (reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttempts.current += 1;
          console.log(`[WS] Attempting to reconnect (${reconnectAttempts.current}/${MAX_RECONNECT_ATTEMPTS})...`);
          reconnectTimeout.current = setTimeout(connect, RECONNECT_DELAY * reconnectAttempts.current);
        } else {
          console.error("[WS] Max reconnection attempts reached.");
        }
      };
    } catch (err) {
      console.error("[WS] Failed to create WebSocket:", err);
      setIsConnected(false);
    }
  }, [handleAssistantMessage]);

  const sendMessage = useCallback((message: any) => {
    console.log("[WS] Attempting to send message:", message);
    console.log("[WS] Current WebSocket state:", ws.current?.readyState);
    console.log("[WS] Current conversation history:", conversationHistory.current);

    if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
      console.log("[WS] Socket not ready, attempting reconnect before send");
      connect();
      // Queue the message to be sent after connection
      setTimeout(() => {
        if (ws.current?.readyState === WebSocket.OPEN) {
          console.log("[WS] Sending queued message:", message);
          ws.current.send(JSON.stringify(message));
        } else {
          console.error("[WS] Failed to send message - socket still not ready, state:", ws.current?.readyState);
        }
      }, 1000);
      return;
    }
    
    try {
      console.log("[WS] Sending message through WebSocket");
      ws.current.send(JSON.stringify(message));
      console.log("[WS] Message sent successfully");
    } catch (err) {
      console.error("[WS] Error sending message:", err);
    }
  }, [connect]);

  const sendUserMessage = useCallback((text: string) => {
    console.log("[WS] sendUserMessage called with:", text);
    // Add user message to conversation history
    const userMessage: Message = { role: "user", content: text };
    console.log("[WS] Adding message to history:", userMessage);
    console.log("[WS] Previous history:", conversationHistory.current);
    
    const updatedHistory = [...conversationHistory.current, userMessage];
    console.log("[WS] Updated history to send:", updatedHistory);
    
    sendMessage({
      mime_type: "text/plain",
      data: text,
      history: updatedHistory
    });
    
    // Only update history after successful send
    conversationHistory.current = updatedHistory;
    console.log("[WS] History updated:", conversationHistory.current);
  }, [sendMessage]);

  // Clean up on unmount
  useEffect(() => {
    console.log("[WS] Initial connect");
    connect();

    return () => {
      console.log("[WS] Cleaning up WebSocket connection");
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
