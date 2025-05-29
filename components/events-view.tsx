"use client"
import { CheckCircle, AlertTriangle, XCircle, Clock } from "lucide-react"

// Define types for our events data
interface Event {
  id: string
  name: string
  description: string
  source: string[]
  status: "Healthy" | "Warning" | "Broken" | "Offline"
  count: number
  change: number
}

// Sample data for events
const eventsData: Event[] = [
    {
      "id": "order-received",
      "name": "Order Received",
      "description": "This event is sent when a new order is created in Shopify.",
      "source": [
        "Mixpanel"
      ],
      "status": "Healthy",
      "count": 0,
      "change": 0.0
    },
    {
      "id": "ad-data",
      "name": "Ad Data",
      "description": "Imported advertising data from Meta, Google, TikTok etc.",
      "source": [
        "Mixpanel"
      ],
      "status": "Healthy",
      "count": 0,
      "change": 0.0
    }
  ];

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
  return (
    <div className="flex flex-col h-full bg-background p-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Events</h1>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full border-collapse">
          <thead>
            <tr className="border-b text-left">
              <th className="py-3 px-4 font-medium text-muted-foreground">EVENT NAME</th>
              <th className="py-3 px-4 font-medium text-muted-foreground">DESCRIPTION</th>
              <th className="py-3 px-4 font-medium text-muted-foreground">SOURCE</th>
              <th className="py-3 px-4 font-medium text-muted-foreground">STATUS</th>
              <th className="py-3 px-4 font-medium text-muted-foreground text-right">LAST 30 DAYS</th>
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
                  {event.source.map((src) => (
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
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
