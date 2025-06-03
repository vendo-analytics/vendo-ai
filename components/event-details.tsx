"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle } from "lucide-react"
import { useEffect, useState } from "react"
import { useConnectionId } from "@/lib/connection-context"

interface EventProperty {
  name: string
  type: string
  description: string
}

interface EventDetailProps {
  event: {
    id: string
    name: string
    description: string
    source: string[]
    status: "Healthy" | "Warning" | "Broken" | "Offline"
    count: number
    change: number
  }
}

export function EventDetails({ event }: EventDetailProps) {
  const [properties, setProperties] = useState<EventProperty[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Get the selected connection ID from global context
  const connectionId = useConnectionId()

  useEffect(() => {
    if (!event?.id) return

    setIsLoading(true)
    fetch(`/api/event-details?connection_id=${connectionId}&event_id=${encodeURIComponent(event.id)}`)
      .then((res) => res.json())
      .then((data) => {
        setProperties(data)
        setIsLoading(false)
      })
      .catch((err) => {
        console.error("Failed to fetch event details:", err)
        setProperties([])
        setIsLoading(false)
      })
  }, [event?.id, connectionId]) // Add connectionId to dependencies

  return (
    <div className="flex flex-col h-full bg-background p-6">
      <div className="mb-6">
        <div className="text-sm text-muted-foreground mb-2">EVENT DETAILS</div>
        <h1 className="text-2xl font-bold mb-2">{event.name}</h1>
        <p className="text-muted-foreground">{event.description}</p>

        <div className="flex items-center mt-4 mb-2">
          {event.status === "Healthy" && (
            <div className="flex items-center text-green-500">
              <CheckCircle className="h-5 w-5 mr-2" />
              <span>Healthy</span>
            </div>
          )}
          <div className="ml-auto text-2xl font-bold">{event.count.toLocaleString()}</div>
        </div>
        <div className="flex items-center">
          <div className="text-sm text-muted-foreground">
            Source: {(Array.isArray(event.source) ? event.source : event.source ? [event.source] : []).join(", ")}
          </div>
          <div className={`ml-auto text-sm ${event.change >= 0 ? "text-green-500" : "text-red-500"}`}>
            {event.change >= 0 ? "↑" : "↓"} {Math.abs(event.change)}%
          </div>
        </div>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>Event Properties</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mb-3"></div>
              <p className="text-muted-foreground text-sm">Loading event properties...</p>
            </div>
          ) : (
            <table className="w-full">
              <thead>
                <tr className="border-b text-left">
                  <th className="py-3 px-4 font-medium text-muted-foreground">NAME</th>
                  <th className="py-3 px-4 font-medium text-muted-foreground">TYPE</th>
                  <th className="py-3 px-4 font-medium text-muted-foreground">DESCRIPTION</th>
                </tr>
              </thead>
              <tbody>
                {properties.map((prop) => (
                  <tr key={prop.name} className="border-b">
                    <td className="py-4 px-4 font-mono text-sm">{prop.name}</td>
                    <td className="py-4 px-4 text-muted-foreground">{prop.type}</td>
                    <td className="py-4 px-4">{prop.description}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
