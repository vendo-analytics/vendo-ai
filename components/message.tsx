"use client"

import type { Message as AIMessage } from "ai"
import { motion } from "framer-motion"
import { SparklesIcon } from "./icons"
import { ThumbsUpIcon, ThumbsDownIcon } from "./rating-icons"
import { Markdown } from "./markdown"
import { PreviewAttachment } from "./preview-attachment"
import { cn } from "@/lib/utils"
import { Weather } from "./weather"
import dynamic from "next/dynamic"

// Dynamically import ChartEmbed to avoid SSR issues with Recharts
const ChartEmbed = dynamic(() => import("./ChartEmbed"), { ssr: false })

// Helper function to detect if content contains a chart
const isChartContent = (content: string): boolean => {
  // Check for JSX chart format
  const isJsxChart = (
    (content.includes("<LineChart") || content.includes("<BarChart") || content.includes("<ScatterChart")) &&
    content.includes("data=")
  );

  // Check for JSON chart format
  const isJsonChart = (() => {
    try {
      console.log("content", content)
      // Try to parse as JSON
      const jsonData = JSON.parse(content);
      console.log("jsonData", jsonData)
      // Check if it has the required chart properties
      return (
        jsonData &&
        typeof jsonData === 'object' &&
        'type' in jsonData &&
        ['line', 'bar', 'scatter'].includes(jsonData.type) &&
        Array.isArray(jsonData.x) &&
        Array.isArray(jsonData.y) &&
        jsonData.x.length === jsonData.y.length
      );
    } catch (e) {
      return false;
    }
  })();

  return isJsxChart || isJsonChart;
}

type Message = AIMessage & { traceId?: string }

interface PreviewMessageProps {
  chatId: string
  message: Message
  isLoading: boolean
  onRating?: (messageId: string, rating: "up" | "down") => "up" | "down" | null
  currentRating?: "up" | "down" | null
}

export const PreviewMessage = ({ message, onRating, currentRating }: PreviewMessageProps) => {
  const handleRating = async (newRating: "up" | "down") => {
    if (onRating) {
      const result = onRating(message.id, newRating)
      console.log(`Message ${message.id} rated:`, result)
    }
    // Send feedback to backend if traceId exists
    if (message.traceId) {
      try {
        await fetch("/api/feedback", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            traceId: message.traceId,
            value: newRating === "up" ? 1 : 0,
          }),
        })
      } catch (err) {
        console.error("Failed to send feedback to backend:", err)
      }
    }
  }

  // Helper to extract chart if content is JSON
  let chartJsx = undefined;
  let isChart = false;
  if (message.content) {
    try {
      const parsed = JSON.parse(message.content);
      if (
        typeof parsed === 'object' &&
        parsed !== null &&
        'chart' in parsed &&
        typeof parsed.chart === 'string'
      ) {
        chartJsx = parsed.chart;
        isChart = true;
      }
    } catch (e) {
      // Not JSON, fallback to old detection
      isChart = isChartContent(message.content);
      chartJsx = message.content;
    }
  }

  return (
    <motion.div
      className="w-full mx-auto px-4 group/message"
      initial={{ y: 5, opacity: 0 }}
      animate={{ y: 0, opacity: 1 }}
      data-role={message.role}
    >
      <div
        className={cn(
          "group-data-[role=user]/message:bg-primary group-data-[role=user]/message:text-primary-foreground flex gap-4 group-data-[role=user]/message:px-3 w-full group-data-[role=user]/message:w-fit group-data-[role=user]/message:ml-auto group-data-[role=user]/message:max-w-4xl group-data-[role=user]/message:py-2 rounded-xl",
        )}
      >
        {message.role === "assistant" && (
          <div className="size-8 flex items-center rounded-full justify-center ring-1 shrink-0 ring-border">
            <SparklesIcon size={14} />
          </div>
        )}

        <div className="flex flex-col gap-2 w-full">
          {message.content && (
            <div className="flex flex-col gap-4">
              {isChart ? (
                <ChartEmbed chartJsx={chartJsx!} />
              ) : (
                <Markdown>{message.content as string}</Markdown>
              )}
            </div>
          )}

          {message.toolInvocations && message.toolInvocations.length > 0 && (
            <div className="flex flex-col gap-4">
              {message.toolInvocations.map((toolInvocation) => {
                const { toolName, toolCallId, state } = toolInvocation

                if (state === "result") {
                  const { result } = toolInvocation

                  return (
                    <div key={toolCallId}>
                      {toolName === "get_current_weather" ? (
                        <Weather weatherAtLocation={result} />
                      ) : (
                        <pre>{JSON.stringify(result, null, 2)}</pre>
                      )}
                    </div>
                  )
                }
                return (
                  <div
                    key={toolCallId}
                    className={cn({
                      skeleton: ["get_current_weather"].includes(toolName),
                    })}
                  >
                    {toolName === "get_current_weather" ? <Weather /> : null}
                  </div>
                )
              })}
            </div>
          )}

          {message.experimental_attachments && (
            <div className="flex flex-row gap-2">
              {message.experimental_attachments.map((attachment) => (
                <PreviewAttachment key={attachment.url} attachment={attachment} />
              ))}
            </div>
          )}

          {/* Rating buttons for assistant messages */}
          {message.role === "assistant" && message.content && onRating && (
            <div className="flex items-center gap-2 mt-2 opacity-0 group-hover/message:opacity-100 transition-opacity">
              <button
                onClick={async () => await handleRating("up")}
                className={cn(
                  "p-1.5 rounded-md hover:bg-muted transition-colors",
                  currentRating === "up"
                    ? "bg-green-100 text-green-600"
                    : "text-muted-foreground hover:text-foreground",
                )}
                title="Good response"
              >
                <ThumbsUpIcon size={14} />
              </button>
              <button
                onClick={async () => await handleRating("down")}
                className={cn(
                  "p-1.5 rounded-md hover:bg-muted transition-colors",
                  currentRating === "down" ? "bg-red-100 text-red-600" : "text-muted-foreground hover:text-foreground",
                )}
                title="Poor response"
              >
                <ThumbsDownIcon size={14} />
              </button>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  )
}

export const ThinkingMessage = () => {
  const role = "assistant"

  return (
    <motion.div
      className="w-full max-w-4xl px-4 group/message"
      initial={{ y: 5, opacity: 0 }}
      animate={{ y: 0, opacity: 1, transition: { delay: 1 } }}
      data-role={role}
    >
      <div
        className={cn(
          "flex gap-4 group-data-[role=user]/message:px-3 w-full group-data-[role=user]/message:w-fit group-data-[role=user]/message:ml-auto group-data-[role=user]/message:max-w-4xl group-data-[role=user]/message:py-2 rounded-xl",
          {
            "group-data-[role=user]/message:bg-muted": true,
          },
        )}
      >
        <div className="size-8 flex items-center rounded-full justify-center ring-1 shrink-0 ring-border">
          <SparklesIcon size={14} />
        </div>

        <div className="flex flex-col gap-2 w-full">
          <div className="flex flex-col gap-4 text-muted-foreground">Thinking...</div>
        </div>
      </div>
    </motion.div>
  )
}
