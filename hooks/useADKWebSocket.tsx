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
  onTextMessage: (textChunk: string, isFinal?: boolean, role?: "user" | "assistant") => void;
  onAudioMessage?: (audioBuffer: ArrayBuffer) => void;
  onTurnComplete?: () => void;
  isAudioEnabled?: boolean;
  setIsAudioEnabled?: (enabled: boolean) => void;
}

interface Message {
  role: "user" | "assistant";
  content: string;
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

    const sessionId = "001"; // You can randomize or parametrize this
    const wsUrl = `ws://localhost:8000/ws/${sessionId}?is_audio=false`; // Always start in text mode
    
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

          // Handle turn completion first
          if (data.turn_complete) {
            console.log("[WS] Turn complete");
            setIsProcessing(false);
            onTurnComplete?.();
            return;
          }

          // Ensure message has mime_type
          if (!data.mime_type) {
            console.warn("[WS] Message missing mime_type:", data);
            return;
          }

          if (data.mime_type === "text/plain") {
            // Let the Chat component handle the text display
            onTextMessage(data.data, data.turn_complete);
            
            // If audio is enabled, also speak the text
            if (callbacksRef.current.isAudioEnabled && 'speechSynthesis' in window) {
              console.log("[WS] Speaking text:", data.data);
              // Cancel any ongoing speech
              if (currentUtterance.current) {
                window.speechSynthesis.cancel();
              }
              
              const utterance = new SpeechSynthesisUtterance(data.data);
              currentUtterance.current = utterance;
              window.speechSynthesis.speak(utterance);
            } else {
              console.log("[WS] Audio disabled, not speaking");
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
    if (isRecording) {
      stopListening();
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

        // Only update the UI with interim results as assistant message
        if (interimTranscript && interimTranscript !== interimMessageRef.current) {
          interimMessageRef.current = interimTranscript;
          // Show interim results as assistant message with isFinal=false
          callbacksRef.current.onTextMessage(interimTranscript, false, "assistant");
        }

        // Store the final transcript
        if (finalTranscript) {
          const finalText = finalTranscript.trim();
          if (finalText) {
            interimMessageRef.current = finalText;
          }
        }
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
        // Only send the message if we stopped manually
        if (stoppedManuallyRef.current && interimMessageRef.current) {
          const finalText = interimMessageRef.current;
          interimMessageRef.current = "";
          stoppedManuallyRef.current = false;
          
          // Add user message to conversation history
          conversationHistory.current.push({ role: "user", content: finalText });
          
          // Clear any existing messages before sending
          callbacksRef.current.onTextMessage("", true);
          
          if (ws.current?.readyState === WebSocket.OPEN) {
            // For audio messages, send with special flag and source
            ws.current.send(JSON.stringify({
              mime_type: "text/plain",
              data: finalText,
              history: conversationHistory.current,
              source: "audio",  // Indicate this is from audio input
              is_audio: true,   // Legacy flag for backward compatibility
              is_final: true    // Indicate this is the final transcript
            }));
          } else {
            // If WebSocket is not open, try to reconnect and send
            connect();
            setTimeout(() => {
              if (ws.current?.readyState === WebSocket.OPEN) {
                ws.current.send(JSON.stringify({
                  mime_type: "text/plain",
                  data: finalText,
                  history: conversationHistory.current,
                  source: "audio",  // Indicate this is from audio input
                  is_audio: true,   // Legacy flag for backward compatibility
                  is_final: true    // Indicate this is the final transcript
                }));
              }
            }, 1000);
          }
        }
        // Only restart recognition if we're still recording
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
        
        if (ws.current?.readyState === WebSocket.OPEN) {
          const base64 = btoa(String.fromCharCode(...new Uint8Array(pcmData.buffer)));
          
          ws.current.send(JSON.stringify({
            mime_type: "audio/pcm",
            data: base64,
          }));
        }
      };
      
      setIsRecording(true);
      console.log("[Audio] Started recording");
    } catch (err) {
      console.error("[Audio] Failed to start recording:", err);
      stopListening(); // Clean up if there's an error
    }
  }, [isRecording, connect, sendUserMessage]);

  const stopListening = useCallback(() => {
    setIsRecording(false);
    stoppedManuallyRef.current = true;

    // If recognition is running, stop it and wait for onend to fire
    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    } else {
      // If recognition is already ended (due to silence), do NOT send the transcript
      // Only send if the user manually stops recording by pressing the mic button
      if (interimMessageRef.current) {
        const finalText = interimMessageRef.current;
        interimMessageRef.current = "";
        stoppedManuallyRef.current = false;
        if (ws.current?.readyState === WebSocket.OPEN) {
          sendUserMessage(finalText);
        } else {
          connect();
          setTimeout(() => {
            if (ws.current?.readyState === WebSocket.OPEN) {
              sendUserMessage(finalText);
            }
          }, 1000);
        }
      }
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
