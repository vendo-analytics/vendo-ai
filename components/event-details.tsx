import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle } from "lucide-react"

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

// Sample event properties data
const eventPropertiesData: Record<string, EventProperty[]> = {
  "order-received": [
    {
      "name": "account_id",
      "type": "string",
      "description": "Advertising account ID"
    },
    {
      "name": "campaign_name",
      "type": "string",
      "description": "Advertising Campaign Name"
    },
    {
      "name": "currency",
      "type": "string",
      "description": "Currency of the order"
    },
    {
      "name": "amount",
      "type": "number",
      "description": "Amount involved"
    },
    {
      "name": "order_id",
      "type": "string",
      "description": "Shopify Order ID"
    }
  ],
  "ad-data": [
    {
      "name": "account_id",
      "type": "string",
      "description": "Advertising account ID"
    },
    {
      "name": "campaign_name",
      "type": "string",
      "description": "Advertising Campaign Name"
    },
    {
      "name": "currency",
      "type": "string",
      "description": "Currency of the order"
    },
    {
      "name": "amount",
      "type": "number",
      "description": "Amount involved"
    },
    {
      "name": "order_id",
      "type": "string",
      "description": "Shopify Order ID"
    }
  ]
};

export function EventDetails({ event }: EventDetailProps) {
  const properties = eventPropertiesData[event.id] || []

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
          <div className="text-sm text-muted-foreground">Source: {event.source.join(", ")}</div>
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
        </CardContent>
      </Card>
    </div>
  )
}
