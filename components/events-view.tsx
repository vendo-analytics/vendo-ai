"use client"
import { CheckCircle, AlertTriangle, XCircle, Clock } from "lucide-react"
import { useEffect, useState } from "react"
import { useConnectionId } from "@/lib/connection-context"

// Define types for our events data
interface Event {
  id: string
  name: string
  description: string
  source: string[]
  status: "Healthy" | "Warning" | "Broken" | "Offline"
  count: number
  change: number
  first_seen?: string
  last_seen?: string
}

// Status badge component
const StatusBadge = ({ status }: { status: Event["status"] }) => {
  switch (status) {
    case "Healthy":
      return (
        <div className="flex items-center text-green-500">
          <CheckCircle className="h-4 w-4 mr-1" />
          <span>Healthy</span>
        </div>
      )
    case "Warning":
      return (
        <div className="flex items-center text-amber-500">
          <AlertTriangle className="h-4 w-4 mr-1" />
          <span>Warning</span>
        </div>
      )
    case "Broken":
      return (
        <div className="flex items-center text-red-500">
          <XCircle className="h-4 w-4 mr-1" />
          <span>Broken</span>
        </div>
      )
    case "Offline":
      return (
        <div className="flex items-center text-gray-500">
          <Clock className="h-4 w-4 mr-1" />
          <span>Offline</span>
        </div>
      )
  }
}

// Source badge component
const SourceBadge = ({ source }: { source: string }) => {
  const bgColor =
    source === "Meta Ads"
      ? "bg-blue-100 text-blue-800"
      : source === "Google Ads"
        ? "bg-blue-100 text-blue-800"
        : source === "Stripe"
          ? "bg-green-100 text-green-800"
          : "bg-gray-100 text-gray-800"

  return <span className={`inline-block px-2 py-1 text-xs rounded-full ${bgColor} mr-1`}>{source}</span>
}

export function EventsView({ onSelectEvent }: { onSelectEvent: (event: Event) => void }) {
  const [eventsData, setEventsData] = useState<Event[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Get the selected connection ID from global context
  const connectionId = useConnectionId()

  useEffect(() => {
    setIsLoading(true)
    fetch(`/api/events-data?connection_id=${connectionId}`)
      .then((res) => res.json())
      .then((data) => {
        setEventsData(data)
        setIsLoading(false)
      })
      .catch((err) => {
        console.error("Failed to fetch events data:", err)
        setEventsData([])
        setIsLoading(false)
      })
  }, [connectionId]) // Add connectionId to dependencies

  return (
    <div className="flex flex-col h-full bg-background p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Events</h1>
      </div>

      {isLoading ? (
        <div className="flex flex-col items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-4"></div>
          <p className="text-muted-foreground">Loading events...</p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b text-left">
                <th className="py-3 px-4 font-medium text-muted-foreground">EVENT NAME</th>
                <th className="py-3 px-4 font-medium text-muted-foreground">DESCRIPTION</th>
                <th className="py-3 px-4 font-medium text-muted-foreground">SOURCE</th>
                <th className="py-3 px-4 font-medium text-muted-foreground">STATUS</th>
                <th className="py-3 px-4 font-medium text-muted-foreground text-right">LAST 30 DAYS</th>
                <th className="py-3 px-4 font-medium text-muted-foreground">FIRST SEEN</th>
                <th className="py-3 px-4 font-medium text-muted-foreground">LAST SEEN</th>
              </tr>
            </thead>
            <tbody>
              {eventsData.map((event) => (
                <tr
                  key={event.id}
                  className="border-b hover:bg-muted/50 cursor-pointer"
                  onClick={() => onSelectEvent(event)}
                >
                  <td className="py-4 px-4 font-medium">{event.name}</td>
                  <td className="py-4 px-4 text-muted-foreground">{event.description}</td>
                  <td className="py-4 px-4">
                    {(
                      Array.isArray(event.source)
                        ? event.source
                        : event.source
                        ? String(event.source).split(",").map(s => s.trim()).filter(Boolean)
                        : []
                    ).map((src) => (
                      <SourceBadge key={src} source={src} />
                    ))}
                  </td>
                  <td className="py-4 px-4">
                    <StatusBadge status={event.status} />
                  </td>
                  <td className="py-4 px-4 text-right">
                    <div className="font-medium">{event.count.toLocaleString()}</div>
                    <div className={`text-sm ${event.change >= 0 ? "text-green-500" : "text-red-500"}`}>
                      {event.change >= 0 ? "↑" : "↓"} {Math.abs(event.change)}%
                    </div>
                  </td>
                  <td className="py-4 px-4 text-muted-foreground">{event.first_seen ? new Date(event.first_seen).toLocaleDateString() : "-"}</td>
                  <td className="py-4 px-4 text-muted-foreground">{event.last_seen ? new Date(event.last_seen).toLocaleDateString() : "-"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
