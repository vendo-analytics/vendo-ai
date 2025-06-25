"use client"

import { useEffect, useState, useRef } from "react"
import { PreviewMessage, ThinkingMessage } from "@/components/message"
import { MultimodalInput } from "@/components/multimodal-input"
import { Overview } from "@/components/overview"
import { useScrollToBottom } from "@/hooks/use-scroll-to-bottom"
import { useADKWebSocket } from "@/hooks/useADKWebSocket"
import { useMessageRatings } from "@/hooks/useMessageRatings"
import type { Message, CreateMessage, ChatRequestOptions } from "ai"
import { toast } from "sonner"
import { AudioToggle } from "./AudioToggle"
import { StatusIndicator } from "./status-indicator"

interface ChatProps {
  chatId?: string
  initialMessages?: Message[]
}

export function Chat({ chatId = "001", initialMessages = [] }: ChatProps) {
  const [messages, setMessages] = useState<Message[]>(initialMessages)
  const [input, setInput] = useState<string>("")
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [isAudioEnabled, setIsAudioEnabled] = useState(false)
  const currentChatRef = useRef<string>(chatId)

  // Add ratings hook
  const { toggleRating, getRating } = useMessageRatings()

  // Update messages when initialMessages changes
  useEffect(() => {
    setMessages(initialMessages)
  }, [initialMessages])

  const append = async (message: Message | CreateMessage, chatRequestOptions?: ChatRequestOptions): Promise<string> => {
    setMessages((prev) => [...prev, message as Message])
    return message.id || `msg-${Date.now()}`
  }

  const stop = () => {
    // Optionally implement stop signal over WebSocket later
  }

  const {
    sendUserMessage,
    startListening,
    stopListening,
    isConnected,
    isRecording,
    stopTTS,
    loadSession,
  } = useADKWebSocket({
    onTextMessage: (content, _isFinal = true, _isPartial = false, role, traceId) => {
      if (!content || !role) return
      if (content.trim() === "") return

      setMessages((prev) => [
        ...prev,
        {
          id: `${role}-${Date.now()}`,
          role,
          content,
          traceId,
        },
      ])
    },
    onTurnComplete: () => setIsLoading(false),
    isAudioEnabled,
    setIsAudioEnabled,
  })

  // Add effect to load chat history when chatId changes
  useEffect(() => {
    // Only load if the chatId has actually changed
    if (chatId !== currentChatRef.current) {
      const loadChatHistory = async () => {
        try {
          setIsLoading(true)
          // Clear existing messages first
          setMessages([])

          // Load the new chat session
          await loadSession(chatId)
          // Update the ref after successful load
          currentChatRef.current = chatId
        } catch (error) {
          console.error("Error loading chat history:", error)
          toast.error("Failed to load chat history")
        } finally {
          setIsLoading(false)
        }
      }

      loadChatHistory()
    }
  }, [chatId, loadSession])

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
      {/* Header with Status Indicator */}
      <div className="flex justify-between items-center p-4 border-b shrink-0 bg-background/95 backdrop-blur-sm">
        <h1 className="text-xl font-bold">Chat</h1>
        <div className="flex items-center gap-4">
          <StatusIndicator isConnected={isConnected} isConnecting={false} />
          <AudioToggle
            isEnabled={isAudioEnabled}
            onToggle={() => {
              console.log("[Audio] Toggle clicked, current state:", isAudioEnabled)
              const newState = !isAudioEnabled
              setIsAudioEnabled(newState)
              // If turning off audio, immediately stop any playing TTS
              if (!newState && stopTTS) {
                stopTTS()
              }
            }}
          />
          <button
            onClick={isRecording ? stopListening : startListening}
            className={`p-2 rounded-full transition-colors ${
              isRecording ? "bg-red-500 hover:bg-red-600" : "bg-blue-500 hover:bg-blue-600"
            }`}
          >
            {isRecording ? (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            ) : (
              <svg
                xmlns="http://www.w3.org/2000/svg"
                className="h-5 w-5 text-white"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
                />
              </svg>
            )}
          </button>
        </div>
      </div>

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
