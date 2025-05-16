"use client";

import { useEffect, useState } from "react";
import { PreviewMessage, ThinkingMessage } from "@/components/message";
import { MultimodalInput } from "@/components/multimodal-input";
import { Overview } from "@/components/overview";
import { useScrollToBottom } from "@/hooks/use-scroll-to-bottom";
import { Message, CreateMessage, ChatRequestOptions } from "ai";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { useChat } from "@/hooks/use-chat";
import { useLocalStorage } from "usehooks-ts";

export function Chat() {
  const [mode, setMode] = useState<'search' | 'analytics'>('search');
  const [localStorageInput, setLocalStorageInput] = useLocalStorage("input", "");

  const { messages, input, handleInputChange, handleSubmit, isLoading, stop } = useChat({
    api: mode === 'search' ? '/api/chat' : '/api/analytics',
    onResponse: (response) => {
      if (mode === 'analytics') {
        // For analytics mode, we need to handle the non-streaming response
        response.json().then((data) => {
          if (data.error) {
            toast.error(data.error);
          }
        });
      }
    },
  });

  // Initialize input from localStorage
  useEffect(() => {
    if (!input && localStorageInput) {
      handleInputChange({ target: { value: localStorageInput } } as React.ChangeEvent<HTMLInputElement>);
    }
  }, []);

  // Update localStorage when input changes
  useEffect(() => {
    if (input !== undefined) {
      setLocalStorageInput(input);
    }
  }, [input, setLocalStorageInput]);

  const chatId = "001";

  const [messagesContainerRef, messagesEndRef] =
    useScrollToBottom<HTMLDivElement>();

  const handleAppend = async (
    message: Message | CreateMessage,
    chatRequestOptions?: ChatRequestOptions
  ) => {
    // This is a no-op since we're using the useChat hook
    return message.id;
  };

  // Create a wrapper for setInput that matches the expected type
  const handleSetInput = (value: string) => {
    handleInputChange({ target: { value } } as React.ChangeEvent<HTMLInputElement>);
  };

  return (
    <div className="flex flex-col min-w-0 h-[calc(100dvh-52px)] bg-background">
      <div className="flex justify-center gap-4 mb-4 pt-4">
        <Button
          variant={mode === 'search' ? 'default' : 'outline'}
          onClick={() => setMode('search')}
        >
          Search Mode
        </Button>
        <Button
          variant={mode === 'analytics' ? 'default' : 'outline'}
          onClick={() => setMode('analytics')}
        >
          Analytics Mode
        </Button>
      </div>

      <div
        ref={messagesContainerRef}
        className="flex flex-col min-w-0 gap-6 flex-1 overflow-y-scroll px-4"
      >
        {messages.length === 0 ? (
          <Overview />
        ) : (
          <>
            {messages.map((message, i) => (
              <div
                key={i}
                className={cn(
                  "flex w-full items-start gap-4",
                  message.role === "assistant" && "bg-muted/50"
                )}
              >
                <div className="flex-1 space-y-2 overflow-hidden">
                  {message.content}
                </div>
              </div>
            ))}
            {isLoading && <ThinkingMessage />}
          </>
        )}
        <div
          ref={messagesEndRef}
          className="shrink-0 min-w-[24px] min-h-[24px]"
        />
      </div>

      <div className="flex mx-auto px-4 bg-background pb-4 md:pb-6 gap-2 w-full md:max-w-3xl">
        <MultimodalInput
          chatId={chatId}
          input={input}
          setInput={handleSetInput}
          isLoading={isLoading}
          stop={stop}
          messages={messages}
          setMessages={() => {}}
          append={handleAppend}
          handleSubmit={handleSubmit}
          startListening={() => {}}
          stopListening={() => {}}
          isRecording={false}
        />
      </div>
    </div>
  );
}
