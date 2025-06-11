"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCircle, Pencil, Check, X } from "lucide-react"
import { useEffect, useState } from "react"
import { useConnectionId } from "@/lib/connection-context"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "sonner"

interface UserProperty {
  name: string
  type: string
  description: string
  sample_value?: any
}

export function UserProperties() {
  const [properties, setProperties] = useState<UserProperty[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [editingProperty, setEditingProperty] = useState<string | null>(null)
  const [editingDescription, setEditingDescription] = useState("")
  const [editingType, setEditingType] = useState("")

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

  const parseSampleValue = (value: any): any[] => {
    if (value === null || value === undefined) return []
    
    // If it's already an array, return it
    if (Array.isArray(value)) return value
    
    // If it's a string that looks like a list
    if (typeof value === 'string') {
      try {
        // Remove any extra quotes and brackets
        const cleaned = value.replace(/^\[|\]$/g, '').replace(/^'|'$/g, '')
        // Split by comma and clean each item
        return cleaned.split(',').map(item => item.trim().replace(/^'|'$/g, ''))
      } catch (e) {
        return [value]
      }
    }
    
    // For other types, return as single item array
    return [value]
  }

  const formatSampleValue = (value: any) => {
    const values = parseSampleValue(value)
    if (values.length === 0) return "No sample value"
    
    return values.map((val, idx) => (
      <span key={idx} className="text-xs bg-muted px-2 py-1 rounded mr-1">
        {typeof val === "object" ? JSON.stringify(val) : String(val)}
      </span>
    ))
  }

  const handleEditProperty = (propertyName: string, currentDescription: string, currentType: string) => {
    setEditingProperty(propertyName)
    setEditingDescription(currentDescription)
    setEditingType(currentType)
  }

  const handleSaveProperty = async (propertyName: string) => {
    try {
      const response = await fetch(`/api/user-properties/update?connection_id=${connectionId}&property_name=${encodeURIComponent(propertyName)}&description=${encodeURIComponent(editingDescription)}&type=${encodeURIComponent(editingType)}`, {
        method: "PUT",
      })

      if (!response.ok) throw new Error("Failed to update property")

      // Update local state
      setProperties((prev) =>
        prev.map((prop) =>
          prop.name === propertyName
            ? { ...prop, description: editingDescription, type: editingType }
            : prop
        )
      )

      setEditingProperty(null)
      setEditingDescription("")
      setEditingType("")
      toast.success("Property updated successfully")
    } catch (error) {
      console.error("Error updating property:", error)
      toast.error("Failed to update property")
    }
  }

  const handleCancelEdit = () => {
    setEditingProperty(null)
    setEditingDescription("")
    setEditingType("")
  }

  const dataTypeOptions = ["string", "integer", "array", "boolean", "float", "object"]

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
                  <th className="py-3 px-4 font-medium text-muted-foreground">SAMPLE VALUES</th>
                  <th className="py-3 px-4 font-medium text-muted-foreground">ACTIONS</th>
                </tr>
              </thead>
              <tbody>
                {properties.map((prop) => {
                  const isEditing = editingProperty === prop.name
                  return (
                  <tr key={prop.name} className="border-b">
                    <td className="py-4 px-4 font-mono text-sm">{prop.name}</td>
                      <td className="py-4 px-4">
                        {isEditing ? (
                          <Select value={editingType} onValueChange={setEditingType}>
                            <SelectTrigger className="w-32">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {dataTypeOptions.map((type) => (
                                <SelectItem key={type} value={type}>
                                  {type}
                                </SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        ) : (
                          <span className="text-muted-foreground">{prop.type}</span>
                        )}
                      </td>
                      <td className="py-4 px-4">
                        {isEditing ? (
                          <Textarea
                            value={editingDescription}
                            onChange={(e) => setEditingDescription(e.target.value)}
                            placeholder="Enter description..."
                            className="bg-white dark:bg-gray-800 border-blue-200 dark:border-blue-800"
                            rows={2}
                          />
                        ) : (
                          prop.description
                        )}
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex flex-wrap gap-1">
                          {formatSampleValue(prop.sample_value)}
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex gap-1">
                          {isEditing ? (
                            <>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={() => handleSaveProperty(prop.name)}
                                className="h-8 w-8 p-0"
                              >
                                <Check size={14} />
                              </Button>
                              <Button
                                size="sm"
                                variant="ghost"
                                onClick={handleCancelEdit}
                                className="h-8 w-8 p-0"
                              >
                                <X size={14} />
                              </Button>
                            </>
                          ) : (
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleEditProperty(prop.name, prop.description, prop.type)}
                              className="h-8 w-8 p-0"
                            >
                              <Pencil size={14} />
                            </Button>
                          )}
                        </div>
                      </td>
                  </tr>
                  )
                })}
              </tbody>
            </table>
          )}
        </CardContent>
      </Card>
    </div>
  )
} 