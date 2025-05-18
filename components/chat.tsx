"use client";

import { useEffect, useState } from "react";
import { PreviewMessage, ThinkingMessage } from "@/components/message";
import { MultimodalInput } from "@/components/multimodal-input";
import { Overview } from "@/components/overview";
import { useScrollToBottom } from "@/hooks/use-scroll-to-bottom";
import { useADKWebSocket } from "@/hooks/useADKWebSocket";
import { Message, CreateMessage, ChatRequestOptions } from "ai";
import { toast } from "sonner";
import { AudioToggle } from "./AudioToggle";

export function Chat() {
  const chatId = "001";

  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isAudioEnabled, setIsAudioEnabled] = useState(true);

  const append = async (
    message: Message | CreateMessage,
    chatRequestOptions?: ChatRequestOptions
  ): Promise<string> => {
    setMessages((prev) => [...prev, message as Message]);
    return message.id || `msg-${Date.now()}`;
  };

  const stop = () => {
    // Optionally implement stop signal over WebSocket later
  };

  const {
    sendUserMessage,
    startListening,
    stopListening,
    isConnected,
    isRecording,
  } = useADKWebSocket({
    onTextMessage: (chunk: string, isFinal = false, isPartial = false, role?: "user" | "assistant") => {
      setMessages((prev) => {
        if (!chunk) return prev;
        const last = prev[prev.length - 1];
  
        if (role === "user") {
          if (last?.role === "user") {
            // Update the last user message
            return [
              ...prev.slice(0, -1),
              { ...last, content: chunk },
            ];
          } else {
            // Always append a new user message if last is not a user
            return [
              ...prev,
              {
                id: `user-${Date.now()}`,
                role: "user",
                content: chunk,
              },
            ];
          }
        } else if (role === "assistant") {
          if (last?.role === "assistant") {
            // Update the last assistant message
            return [
              ...prev.slice(0, -1),
              { ...last, content: chunk },
            ];
          } else {
            // Always append a new assistant message if last is not an assistant
            return [
              ...prev,
              {
                id: `assistant-${Date.now()}`,
                role: "assistant",
                content: chunk,
              },
            ];
          }
        }

        return prev;
      });
  
      if (isFinal) setIsLoading(false);
    },
    onTurnComplete: () => setIsLoading(false),
    isAudioEnabled,
    setIsAudioEnabled,
  });

  useEffect(() => {
    if (!isConnected) {
      toast.error("WebSocket connection lost. Attempting to reconnect...");
    } else {
      toast.success("WebSocket connected");
    }
  }, [isConnected]);

  // Add a debug log to track audio state changes
  useEffect(() => {
    console.log("[Audio] State changed:", isAudioEnabled);
  }, [isAudioEnabled]);

  const handleSubmit = (
    event?: { preventDefault?: () => void },
    chatRequestOptions?: ChatRequestOptions
  ) => {
    if (event?.preventDefault) {
      event.preventDefault();
    }
    
    if (!input.trim()) return;

    if (!isConnected) {
      toast.error("Cannot send message: WebSocket is not connected");
      return;
    }

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: input,
    };

    append(userMessage);
    sendUserMessage(input);
    setInput("");
    setIsLoading(true);
  };

  const [messagesContainerRef, messagesEndRef] =
    useScrollToBottom<HTMLDivElement>();

  return (
    <div className="flex flex-col min-w-0 h-[calc(100dvh-52px)] bg-background max-w-3xl mx-auto">
      <div className="flex justify-between items-center p-4 border-b">
        <h1 className="text-xl font-bold">Chat</h1>
        <div className="flex items-center gap-2">
          <AudioToggle 
            isEnabled={isAudioEnabled} 
            onToggle={() => {
              console.log("[Audio] Toggle clicked, current state:", isAudioEnabled);
              setIsAudioEnabled(!isAudioEnabled);
            }} 
          />
          <button
            onClick={isRecording ? stopListening : startListening}
            className={`p-2 rounded-full ${
              isRecording 
                ? 'bg-red-500 hover:bg-red-600' 
                : 'bg-blue-500 hover:bg-blue-600'
            }`}
          >
            {isRecording ? (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
              </svg>
            )}
          </button>
        </div>
      </div>
      <div
        ref={messagesContainerRef}
        className="flex flex-col min-w-0 gap-6 flex-1 overflow-y-auto scrollbar-hide pt-4"
      >
        {messages.length === 0 && <Overview />}

        {messages.map((message, index) => (
          <PreviewMessage
            key={message.id}
            chatId={chatId}
            message={message}
            isLoading={isLoading && messages.length - 1 === index}
          />
        ))}

        {isLoading &&
          messages.length > 0 &&
          messages[messages.length - 1].role === "user" && <ThinkingMessage />}

        <div
          ref={messagesEndRef}
          className="shrink-0 min-w-[24px] min-h-[24px]"
        />
      </div>

      <div className="p-4 border-t">
        <MultimodalInput
          chatId={chatId}
          input={input}
          setInput={setInput}
          handleSubmit={handleSubmit}
          isLoading={isLoading}
          stop={stop}
          messages={messages}
          setMessages={setMessages}
          append={append}
          startListening={startListening}
          stopListening={stopListening}
          isRecording={isRecording}
          isAudioEnabled={isAudioEnabled}
          setIsAudioEnabled={setIsAudioEnabled}
        />
      </div>
    </div>
  );
}
