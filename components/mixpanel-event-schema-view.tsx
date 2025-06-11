"use client"

import { useState, useEffect } from "react"
import { Card, CardContent } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { ChevronDown, ChevronRight, Eye, ShoppingCart, User, Calendar, Pencil, Check, X } from "lucide-react"
import { useConnectionId } from "@/lib/connection-context"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "sonner"

interface SampleValue {
  [key: string]: any
}

interface PropertyData {
  data_type: string
  first_seen: string
  last_seen: string
  sample_values: SampleValue[] | string[] | number[] | boolean[]
  status: "live" | "inactive" | "new"
  description?: string
}

interface EventProperties {
  [key: string]: PropertyData
}

interface EventData {
  first_seen: string
  last_seen: string
  last_30_day_count: number
  properties: EventProperties
  status: "live" | "inactive" | "new"
  description?: string
}

interface SchemaData {
  summary: {
    total_events: number
    date_range: {
      earliest_event: string
      latest_event: string
    }
    last_30_days: {
      period_start: string
      period_end: string
      total_events: number
      events: {
        [key: string]: {
          last_30_day_count: number
          status: string
        }
      }
    }
    status_summary: {
      events: {
        new: number
        inactive: number
        live: number
      }
      properties: {
        new: number
        inactive: number
        live: number
      }
    }
  }
  events: {
    [key: string]: EventData
  }
}

interface DataDictionaryEvent {
  description?: string
  properties?: {
    [key: string]: {
      description?: string
    }
  }
}

interface DataDictionary {
  [key: string]: DataDictionaryEvent
}

export function MixpanelEventSchemaView() {
  const [schemaData, setSchemaData] = useState<SchemaData | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [selectedEvent, setSelectedEvent] = useState<string | null>(null)
  const [expandedEvents, setExpandedEvents] = useState<Record<string, boolean>>({})

  // Property editing state
  const [editingProperty, setEditingProperty] = useState<string | null>(null)
  const [editingDescription, setEditingDescription] = useState("")
  const [editingDataType, setEditingDataType] = useState("")

  // Event description editing state
  const [editingEventDescription, setEditingEventDescription] = useState<string | null>(null)
  const [editingEventDescriptionText, setEditingEventDescriptionText] = useState("")

  // Get the selected connection ID from global context
  const connectionId = useConnectionId()

  useEffect(() => {
    const fetchSchemaData = async () => {
      try {
        setIsLoading(true)
        // Fetch schema data (which now includes Mixpanel Event Schema)
        const response = await fetch(`/api/mixpanel-event-schema?connection_id=${connectionId}`)
        if (!response.ok) throw new Error("Failed to fetch schema data")
        const data = await response.json() as SchemaData
        
        setSchemaData(data)

        // Set the first event as selected by default
        if (data && data.events && Object.keys(data.events).length > 0) {
          setSelectedEvent(Object.keys(data.events)[0])
          // Initialize expanded state for all events
          const initialExpandedState: Record<string, boolean> = {}
          Object.keys(data.events).forEach((eventName) => {
            initialExpandedState[eventName] = false
          })
          setExpandedEvents(initialExpandedState)
        }
      } catch (error) {
        console.error("Error fetching schema data:", error)
      } finally {
        setIsLoading(false)
      }
    }

    fetchSchemaData()
  }, [connectionId])

  const toggleEventExpanded = (eventName: string) => {
    setExpandedEvents((prev) => ({
      ...prev,
      [eventName]: !prev[eventName],
    }))
    setSelectedEvent(eventName)
  }

  const formatDate = (dateString: string) => {
    try {
      const date = new Date(dateString)
      return date.toLocaleString("en-US", {
        year: "numeric",
        month: "short",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      })
    } catch (e) {
      return dateString
    }
  }

  const getEventIcon = (eventName: string) => {
    if (eventName.toLowerCase().includes("page")) return <Eye size={18} />
    if (eventName.toLowerCase().includes("cart")) return <ShoppingCart size={18} />
    if (eventName.toLowerCase().includes("signup") || eventName.toLowerCase().includes("user"))
      return <User size={18} />
    return <Calendar size={18} />
  }

  // Property editing functions
  const handleEditProperty = (
    eventName: string,
    propertyName: string,
    currentDescription: string,
    currentDataType: string,
  ) => {
    setEditingProperty(`${eventName}.${propertyName}`)
    setEditingDescription(currentDescription || "")
    setEditingDataType(currentDataType)
  }

  const handleSaveProperty = async (eventName: string, propertyName: string) => {
    try {
      const response = await fetch(`/api/mixpanel-event-schema/update?connection_id=${connectionId}&event_name=${encodeURIComponent(eventName)}&property_name=${encodeURIComponent(propertyName)}&description=${encodeURIComponent(editingDescription)}&data_type=${encodeURIComponent(editingDataType)}`, {
        method: "PUT",
      })

      if (!response.ok) throw new Error("Failed to update property")

      // Update local state
      setSchemaData((prev) => {
        if (!prev) return prev
        return {
          ...prev,
          events: {
            ...prev.events,
            [eventName]: {
              ...prev.events[eventName],
              properties: {
                ...prev.events[eventName].properties,
                [propertyName]: {
                  ...prev.events[eventName].properties[propertyName],
                  description: editingDescription,
                  data_type: editingDataType,
                },
              },
            },
          },
        }
      })

      setEditingProperty(null)
      setEditingDescription("")
      setEditingDataType("")
      toast.success("Property updated successfully")
    } catch (error) {
      console.error("Error updating property:", error)
      toast.error("Failed to update property")
    }
  }

  const handleCancelPropertyEdit = () => {
    setEditingProperty(null)
    setEditingDescription("")
    setEditingDataType("")
  }

  // Event description editing functions
  const handleEditEventDescription = (eventName: string, currentDescription: string) => {
    setEditingEventDescription(eventName)
    setEditingEventDescriptionText(currentDescription || "")
  }

  const handleSaveEventDescription = async (eventName: string) => {
    try {
      const response = await fetch(`/api/mixpanel-event-schema/update?connection_id=${connectionId}&event_name=${encodeURIComponent(eventName)}&description=${encodeURIComponent(editingEventDescriptionText)}`, {
        method: "PUT",
      })

      if (!response.ok) throw new Error("Failed to update event description")

      // Update local state
      setSchemaData((prev) => {
        if (!prev) return prev
        return {
          ...prev,
          events: {
            ...prev.events,
            [eventName]: {
              ...prev.events[eventName],
              description: editingEventDescriptionText,
            },
          },
        }
      })

      setEditingEventDescription(null)
      setEditingEventDescriptionText("")
      toast.success("Event description updated successfully")
    } catch (error) {
      console.error("Error updating event description:", error)
      toast.error("Failed to update event description")
    }
  }

  const handleCancelEventDescriptionEdit = () => {
    setEditingEventDescription(null)
    setEditingEventDescriptionText("")
  }

  const dataTypeOptions = ["string", "integer", "array", "boolean", "float", "object"]

  if (isLoading) {
    return (
      <div className="flex flex-col h-full bg-background p-6">
        <div className="flex items-center justify-center h-full">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          <span className="ml-2">Loading schema data...</span>
        </div>
      </div>
    )
  }

  if (!schemaData) {
    return (
      <div className="flex flex-col h-full bg-background p-6">
        <div className="flex items-center justify-center h-full">
          <p className="text-muted-foreground">No schema data available</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-background p-6 overflow-auto">
      <div className="mb-6">
        <h1 className="text-4xl font-bold">Events</h1>
        <p className="text-muted-foreground mt-2">Event tracking overview and detailed property analysis</p>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col">
              <span className="text-muted-foreground mb-2">Total Events</span>
              <span className="text-4xl font-bold">{schemaData.summary.total_events.toLocaleString()}</span>
              <span className="text-sm text-muted-foreground mt-1">
                Since {formatDate(schemaData.summary.date_range.earliest_event).split(",")[0]}
              </span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col">
              <span className="text-muted-foreground mb-2">Last 30 Days</span>
              <span className="text-4xl font-bold">
                {schemaData.summary.last_30_days.total_events.toLocaleString()}
              </span>
              <span className="text-sm text-muted-foreground mt-1">Recent activity</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex flex-col">
              <span className="text-muted-foreground mb-2">Active Events</span>
              <span className="text-4xl font-bold">{schemaData.summary.status_summary.events.live}</span>
              <span className="text-sm text-muted-foreground mt-1">Event types currently tracking</span>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Events List */}
      <div className="space-y-4">
        {Object.entries(schemaData.events).map(([eventName, eventData]) => (
          <div
            key={eventName}
            className={`border rounded-lg ${selectedEvent === eventName ? "border-primary" : "border-border"}`}
          >
            <div className="flex items-center p-4 cursor-pointer" onClick={() => toggleEventExpanded(eventName)}>
              <div className="mr-3">{getEventIcon(eventName)}</div>
              <div className="flex-1">
                <h3 className="font-semibold">{eventName}</h3>
                <p className="text-sm text-muted-foreground">
                  {eventData.last_30_day_count} events in last 30 days • {Object.keys(eventData?.properties ?? {}).length}{" "}
                  properties
                </p>
              </div>
              <Badge variant={eventData.status === "live" ? "default" : "outline"} className="mr-2">
                {eventData.status}
              </Badge>
              <button className="p-1">
                {expandedEvents[eventName] ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
              </button>
            </div>

            {expandedEvents[eventName] && (
              <div className="px-4 pb-4">
                <Separator className="mb-4" />

                {/* Event Details */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                  <div>
                    <h4 className="font-medium text-muted-foreground mb-1">First Seen</h4>
                    <p>{formatDate(eventData.first_seen)}</p>
                  </div>
                  <div>
                    <h4 className="font-medium text-muted-foreground mb-1">Last Seen</h4>
                    <p>{formatDate(eventData.last_seen)}</p>
                  </div>
                  <div>
                    <h4 className="font-medium text-muted-foreground mb-1">Recent Count</h4>
                    <p>{eventData.last_30_day_count} events</p>
                  </div>
                </div>

                {/* Event Description - Now Editable */}
                <div className="bg-blue-50 dark:bg-blue-950 p-4 rounded-lg mb-6">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium">Description</h4>
                    {editingEventDescription === eventName ? (
                      <div className="flex gap-1">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleSaveEventDescription(eventName)}
                          className="h-8 w-8 p-0"
                        >
                          <Check size={14} />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={handleCancelEventDescriptionEdit}
                          className="h-8 w-8 p-0"
                        >
                          <X size={14} />
                        </Button>
                      </div>
                    ) : (
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => handleEditEventDescription(eventName, eventData.description || "")}
                        className="h-8 w-8 p-0"
                      >
                        <Pencil size={14} />
                      </Button>
                    )}
                  </div>
                  {editingEventDescription === eventName ? (
                    <Textarea
                      value={editingEventDescriptionText}
                      onChange={(e) => setEditingEventDescriptionText(e.target.value)}
                      placeholder="Enter event description..."
                      className="bg-white dark:bg-gray-800 border-blue-200 dark:border-blue-800"
                      rows={3}
                    />
                  ) : (
                    <p className="text-blue-800 dark:text-blue-300">
                      {eventData.description || "No description available. Click the edit button to add one."}
                    </p>
                  )}
                </div>

                {/* Properties Table */}
                <div className="mt-6">
                  <h4 className="font-medium mb-3">Properties ({Object.keys(eventData?.properties ?? {}).length})</h4>
                  <div className="overflow-x-auto max-w-full">
                    <table className="w-full border-collapse table-fixed">
                      <thead>
                        <tr className="border-b text-left">
                          <th className="py-3 px-4 font-medium text-muted-foreground w-[20%]">Property Name</th>
                          <th className="py-3 px-4 font-medium text-muted-foreground w-[10%]">Type</th>
                          <th className="py-3 px-4 font-medium text-muted-foreground w-[10%]">Status</th>
                          <th className="py-3 px-4 font-medium text-muted-foreground w-[15%]">First Seen</th>
                          <th className="py-3 px-4 font-medium text-muted-foreground w-[15%]">Last Seen</th>
                          <th className="py-3 px-4 font-medium text-muted-foreground w-[20%]">Sample Values</th>
                          <th className="py-3 px-4 font-medium text-muted-foreground w-[10%]">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(eventData?.properties ?? {}).map(([propName, propData]) => {
                          const isEditing = editingProperty === `${eventName}.${propName}`
                          return (
                            <tr key={propName} className="border-b hover:bg-muted/50">
                              <td className="py-4 px-4 font-medium truncate">
                                {propName}
                                {!isEditing && propData.description && (
                                  <p className="text-xs text-muted-foreground mt-1 truncate">{propData.description}</p>
                                )}
                                {isEditing && (
                                  <div className="mt-2">
                                    <Input
                                      value={editingDescription}
                                      onChange={(e) => setEditingDescription(e.target.value)}
                                      placeholder="Enter description..."
                                      className="text-xs"
                                    />
                                  </div>
                                )}
                              </td>
                              <td className="py-4 px-4 truncate">
                                {isEditing ? (
                                  <Select value={editingDataType} onValueChange={setEditingDataType}>
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
                                  <Badge variant="outline" className="font-mono text-xs">
                                    {propData.data_type}
                                  </Badge>
                                )}
                              </td>
                              <td className="py-4 px-4 truncate">
                                <Badge
                                  variant={propData.status === "live" ? "default" : "outline"}
                                  className={`${propData.status === "inactive" ? "text-muted-foreground" : ""}`}
                                >
                                  {propData.status}
                                </Badge>
                              </td>
                              <td className="py-4 px-4 whitespace-nowrap truncate">
                                {formatDate(propData.first_seen).split(",")[0]}
                              </td>
                              <td className="py-4 px-4 whitespace-nowrap truncate">
                                {formatDate(propData.last_seen).split(",")[0]}
                              </td>
                              <td className="py-4 px-4">
                                <div className="flex flex-wrap gap-1">
                                  {(propData?.sample_values ?? []).slice(0, 3).map((value, idx) => (
                                    <Badge key={idx} variant="secondary" className="text-xs truncate max-w-[200px]">
                                      {typeof value === "object"
                                        ? JSON.stringify(value).substring(0, 20)
                                        : String(value)}
                                    </Badge>
                                  ))}
                                  {(!propData?.sample_values || propData.sample_values.length === 0) && (
                                    <Badge variant="secondary" className="text-xs">
                                      No sample values
                                    </Badge>
                                  )}
                                </div>
                              </td>
                              <td className="py-4 px-4">
                                <div className="flex gap-1">
                                  {isEditing ? (
                                    <>
                                      <Button
                                        size="sm"
                                        variant="ghost"
                                        onClick={() => handleSaveProperty(eventName, propName)}
                                        className="h-8 w-8 p-0"
                                      >
                                        <Check size={14} />
                                      </Button>
                                      <Button
                                        size="sm"
                                        variant="ghost"
                                        onClick={handleCancelPropertyEdit}
                                        className="h-8 w-8 p-0"
                                      >
                                        <X size={14} />
                                      </Button>
                                    </>
                                  ) : (
                                    <Button
                                      size="sm"
                                      variant="ghost"
                                      onClick={() =>
                                        handleEditProperty(
                                          eventName,
                                          propName,
                                          propData.description || "",
                                          propData.data_type,
                                        )
                                      }
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
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
