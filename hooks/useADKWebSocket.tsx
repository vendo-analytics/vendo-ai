import { useEffect, useRef, useState, useCallback } from "react";

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

type Props = {
  onTextMessage: (textChunk: string, isFinal?: boolean, role?: "user" | "assistant") => void;
  onAudioMessage?: (audioBuffer: ArrayBuffer) => void;
  onTurnComplete?: () => void;
};

interface Message {
  role: "user" | "assistant";
  content: string;
}

function getValidHistory(history: Message[]): Message[] {
  return history
    .filter((m) => m.content && typeof m.content === "string")
    .map((m) => ({
      role: m.role,
      content: m.content.trim(),
    }));
}

export function useADKWebSocket({ onTextMessage, onAudioMessage, onTurnComplete }: Props) {
  const ws = useRef<WebSocket | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const reconnectTimeout = useRef<NodeJS.Timeout>();
  const reconnectAttempts = useRef(0);
  const MAX_RECONNECT_ATTEMPTS = 5;
  const RECONNECT_DELAY = 1000;

  const audioContextRef = useRef<AudioContext | null>(null);
  const processorRef = useRef<ScriptProcessorNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const recognitionRef = useRef<SpeechRecognition | null>(null);
  const interimMessageRef = useRef<string>("");
  const stoppedManuallyRef = useRef(false);
  const conversationHistory = useRef<Message[]>([]);

  const [isRecording, setIsRecording] = useState(false);

  const callbacksRef = useRef({ onTextMessage, onAudioMessage, onTurnComplete });

  useEffect(() => {
    callbacksRef.current = { onTextMessage, onAudioMessage, onTurnComplete };
  }, [onTextMessage, onAudioMessage, onTurnComplete]);

  const connect = useCallback(() => {
    if (ws.current?.readyState === WebSocket.OPEN) return;

    const sessionId = "001";
    const wsUrl = `ws://localhost:8000/ws/${sessionId}?is_audio=false`;

    try {
      const socket = new WebSocket(wsUrl);
      ws.current = socket;

      const pingInterval = setInterval(() => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(JSON.stringify({ type: "ping" }));
        }
      }, 30000);

      socket.onopen = () => {
        console.log("[WS] Connected.");
        setIsConnected(true);
        reconnectAttempts.current = 0;

        const cleanHistory = getValidHistory(conversationHistory.current);
        if (cleanHistory.length > 0) {
          socket.send(
            JSON.stringify({ mime_type: "text/plain", data: "", history: cleanHistory })
          );
        }
      };

      socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);

          if (message.turn_complete) {
            callbacksRef.current.onTextMessage("", true);
            callbacksRef.current.onTurnComplete?.();
            return;
          }

          if (!message.mime_type) message.mime_type = "text/plain";

          if (message.mime_type === "text/plain") {
            if (message.tool_output) {
              const formattedOutput = `🔍 ${message.tool_name || "Tool"} Results:\n${message.data}`;
              callbacksRef.current.onTextMessage(formattedOutput, false);
            } else {
              callbacksRef.current.onTextMessage(message.data, false);
            }
          } else if (
            message.mime_type === "audio/pcm" &&
            typeof message.data === "string" &&
            callbacksRef.current.onAudioMessage
          ) {
            const binary = atob(message.data);
            const buffer = new Uint8Array(binary.length);
            for (let i = 0; i < binary.length; i++) buffer[i] = binary.charCodeAt(i);
            callbacksRef.current.onAudioMessage(buffer.buffer);
          }
        } catch (err) {
          console.error("[WS] Failed to parse message:", err);
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

        if (!isRecording && reconnectAttempts.current < MAX_RECONNECT_ATTEMPTS) {
          reconnectAttempts.current++;
          reconnectTimeout.current = setTimeout(connect, RECONNECT_DELAY * reconnectAttempts.current);
        } else {
          console.error("[WS] Max reconnection attempts reached or recording stopped.");
        }
      };
    } catch (err) {
      console.error("[WS] Failed to create WebSocket:", err);
      setIsConnected(false);
    }
  }, [isRecording]);

  useEffect(() => {
    connect();
    return () => {
      if (reconnectTimeout.current) clearTimeout(reconnectTimeout.current);
      if (ws.current) ws.current.close();
    };
  }, [connect]);

  useEffect(() => {
    const saveHistory = () => {
      localStorage.setItem("conversationHistory", JSON.stringify(conversationHistory.current));
    };

    const savedHistory = localStorage.getItem("conversationHistory");
    if (savedHistory) {
      try {
        conversationHistory.current = JSON.parse(savedHistory);
      } catch (err) {
        console.error("[WS] Failed to load conversation history:", err);
      }
    }

    window.addEventListener("beforeunload", saveHistory);
    return () => {
      window.removeEventListener("beforeunload", saveHistory);
      saveHistory();
    };
  }, []);

  const sendUserMessage = useCallback((text: string) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      conversationHistory.current.push({ role: "user", content: text });
      ws.current.send(
        JSON.stringify({
          mime_type: "text/plain",
          data: text,
          history: getValidHistory(conversationHistory.current),
        })
      );
    } else {
      console.error("[WS] Cannot send message: WebSocket is not connected");
    }
  }, []);

  const startListening = useCallback(async () => {
    if (isRecording) return;

    try {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SpeechRecognition) throw new Error("Speech recognition not supported");

      const recognition = new SpeechRecognition();
      recognitionRef.current = recognition;
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = "en-US";

      recognition.onresult = (event) => {
        let interimTranscript = "";
        let finalTranscript = "";

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + " ";
          } else {
            interimTranscript += transcript;
          }
        }

        if (interimTranscript && interimTranscript !== interimMessageRef.current) {
          interimMessageRef.current = interimTranscript;
          callbacksRef.current.onTextMessage(interimTranscript, false, "assistant");
        }

        if (finalTranscript) {
          const finalText = finalTranscript.trim();
          if (finalText) interimMessageRef.current = finalText;
        }
      };

      recognition.onerror = (event) => {
        console.error("[Speech] Recognition error:", event.error);
        if (event.error === "no-speech") {
          recognition.stop();
          recognition.start();
        }
      };

      recognition.onend = () => {
        if (stoppedManuallyRef.current && interimMessageRef.current) {
          const finalText = interimMessageRef.current;
          interimMessageRef.current = "";
          stoppedManuallyRef.current = false;
          conversationHistory.current.push({ role: "user", content: finalText });
          callbacksRef.current.onTextMessage("", true);

          if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({
              mime_type: "text/plain",
              data: finalText,
              history: getValidHistory(conversationHistory.current),
              source: "audio",
              is_audio: true,
              is_final: true
            }));
          }
        }

        if (isRecording) recognition.start();
      };

      recognition.start();
      setIsRecording(true);
      console.log("[Audio] Started recording");
    } catch (err) {
      console.error("[Audio] Failed to start recognition:", err);
    }
  }, [isRecording]);

  const stopListening = useCallback(() => {
    setIsRecording(false);
    stoppedManuallyRef.current = true;

    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
    } else {
      if (interimMessageRef.current) {
        const finalText = interimMessageRef.current;
        interimMessageRef.current = "";
        stoppedManuallyRef.current = false;

        if (ws.current?.readyState === WebSocket.OPEN) {
          sendUserMessage(finalText);
        }
      }
    }
  }, [sendUserMessage]);

  return {
    sendUserMessage,
    isConnected,
    startListening,
    stopListening,
    isRecording,
  };
}
