"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle } from "lucide-react"
import { useEffect, useState } from "react"
import { useConnectionId } from "@/lib/connection-context"

interface UserProperty {
  name: string
  type: string
  description: string
}

export function UserProperties() {
  const [properties, setProperties] = useState<UserProperty[]>([])
  const [isLoading, setIsLoading] = useState(true)

  // Get the selected connection ID from global context
  const connectionId = useConnectionId()

  useEffect(() => {
    setIsLoading(true)
    fetch(`/api/user-properties?connection_id=${connectionId}`)
      .then((res) => res.json())
      .then((data) => {
        setProperties(data)
        setIsLoading(false)
      })
      .catch((err) => {
        console.error("Failed to fetch user details:", err)
        setProperties([])
        setIsLoading(false)
      })
  }, [connectionId])

  return (
    <div className="flex flex-col h-full bg-background p-6">
      <div className="mb-6">
        <div className="text-sm text-muted-foreground mb-2">USER PROPERTIES</div>
        <h1 className="text-2xl font-bold mb-2">User Properties</h1>
        <p className="text-muted-foreground">View and manage user properties for your application</p>
      </div>

      <Card className="mt-6">
        <CardHeader>
          <CardTitle>User Properties</CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-8">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary mb-3"></div>
              <p className="text-muted-foreground text-sm">Loading user properties...</p>
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