"use client"

import { useState, useCallback } from "react"

interface MessageRating {
  messageId: string
  rating: "up" | "down"
  timestamp: number
}

export function useMessageRatings() {
  const [ratings, setRatings] = useState<Record<string, "up" | "down" | null>>({})

  const setRating = useCallback((messageId: string, rating: "up" | "down" | null) => {
    setRatings((prev) => ({
      ...prev,
      [messageId]: rating,
    }))

    // Here you can add API call to save rating to backend
    if (rating) {
      console.log(`Saving rating for message ${messageId}:`, rating)
      // Example API call:
      // fetch('/api/ratings', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ messageId, rating, timestamp: Date.now() })
      // })
    }
  }, [])

  const getRating = useCallback(
    (messageId: string) => {
      return ratings[messageId] || null
    },
    [ratings],
  )

  const toggleRating = useCallback(
    (messageId: string, newRating: "up" | "down") => {
      const currentRating = ratings[messageId]
      const finalRating = currentRating === newRating ? null : newRating
      setRating(messageId, finalRating)
      return finalRating
    },
    [ratings, setRating],
  )

  return {
    ratings,
    setRating,
    getRating,
    toggleRating,
  }
}
