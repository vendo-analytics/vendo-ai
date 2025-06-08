"use client"

import { useEffect, useState } from "react"
import { PreviewMessage, ThinkingMessage } from "@/components/message"
import { MultimodalInput } from "@/components/multimodal-input"
import { Overview } from "@/components/overview"
import { useScrollToBottom } from "@/hooks/use-scroll-to-bottom"
import { useADKWebSocket } from "@/hooks/useADKWebSocket"
import { useMessageRatings } from "@/hooks/useMessageRatings"
import type { Message, CreateMessage, ChatRequestOptions } from "ai"
import { toast } from "sonner"
import { AudioToggle } from "./AudioToggle"

export function Chat() {
  const chatId = "001"

  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState<string>("")
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [isAudioEnabled, setIsAudioEnabled] = useState(false)

  // Add ratings hook
  const { toggleRating, getRating } = useMessageRatings()

  const append = async (message: Message | CreateMessage, chatRequestOptions?: ChatRequestOptions): Promise<string> => {
    setMessages((prev) => [...prev, message as Message])
    return message.id || `msg-${Date.now()}`
  }

  const stop = () => {
    // Optionally implement stop signal over WebSocket later
  }

  const { sendUserMessage, startListening, stopListening, isConnected, isRecording, stopTTS } = useADKWebSocket({
    onTextMessage: (chunk: string, isFinal = false, isPartial = false, role?: "user" | "assistant", traceId?: string) => {
      setMessages((prev) => {
        if (!chunk) return prev
        const last = prev[prev.length - 1]

        if (role === "user") {
          if (last?.role === "user") {
            // Update the last user message
            return [...prev.slice(0, -1), { ...last, content: chunk }]
          } else {
            // Always append a new user message if last is not a user
            return [
              ...prev,
              {
                id: `user-${Date.now()}`,
                role: "user",
                content: chunk,
              },
            ]
          }
        } else if (role === "assistant") {
          if (last?.role === "assistant") {
            // Update the last assistant message
            return [...prev.slice(0, -1), { ...last, content: chunk, traceId }]
          } else {
            // Always append a new assistant message if last is not an assistant
            return [
              ...prev,
              {
                id: `assistant-${Date.now()}`,
                role: "assistant",
                content: chunk,
                traceId,
              },
            ]
          }
        }

        return prev
      })

      if (isFinal) setIsLoading(false)
    },
    onTurnComplete: () => setIsLoading(false),
    isAudioEnabled,
    setIsAudioEnabled,
  })

  useEffect(() => {
    if (!isConnected) {
      // Only show error if we've attempted to connect
      console.log("WebSocket not connected - running in demo mode")
    } else {
      console.log("WebSocket connected - real-time features available")
    }
  }, [isConnected])

  // Add a debug log to track audio state changes
  useEffect(() => {
    console.log("[Audio] State changed:", isAudioEnabled)
  }, [isAudioEnabled])

  const handleSubmit = (event?: { preventDefault?: () => void }, chatRequestOptions?: ChatRequestOptions) => {
    if (event?.preventDefault) {
      event.preventDefault()
    }

    if (!input.trim()) return

    if (!isConnected) {
      toast.error("Cannot send message: WebSocket is not connected")
      return
    }

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: "user",
      content: input,
    }

    append(userMessage)
    sendUserMessage(input)
    setInput("")
    setIsLoading(true)
  }

  const [messagesContainerRef, messagesEndRef] = useScrollToBottom<HTMLDivElement>()

  // The useScrollToBottom hook handles all scrolling automatically via MutationObserver

  return (
    <div className="flex flex-col h-full bg-background relative">
      {/* Messages Container */}
      <div
        ref={messagesContainerRef}
        className="flex flex-col min-w-0 gap-6 flex-1 overflow-y-auto scrollbar-hide pt-4 px-4 pb-4"
      >
        {messages.length === 0 && <Overview />}

        {messages.map((message, index) => (
          <PreviewMessage
            key={message.id}
            chatId={chatId}
            message={message}
            isLoading={isLoading && messages.length - 1 === index}
            onRating={toggleRating}
            currentRating={getRating(message.id)}
          />
        ))}

        {isLoading && messages.length > 0 && messages[messages.length - 1].role === "user" && <ThinkingMessage />}

        {/* Spacer to account for fixed input */}
        <div className="h-32" />

        {/* Scroll target - positioned at the very bottom */}
        <div ref={messagesEndRef} className="shrink-0 w-full h-1" />
      </div>

      {/* Fixed Input Container at Bottom */}
      <div className="fixed bottom-0 right-0 p-4 border-t bg-background/95 backdrop-blur-sm md:left-64 left-0">
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
          stopTTS={stopTTS}
        />
      </div>
    </div>
  )
}
