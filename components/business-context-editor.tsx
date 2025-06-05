"use client"

import { useState, useEffect } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCirclFillIcon, CrossIcon, PencilEditIcon } from "./icons"
import { toast } from "sonner"
import { useConnectionId } from "@/lib/connection-context"

interface BusinessContext {
  name: string
  preferred_name: string
  user_id: string
  company_name: string
  company_short: string
  origin_country: string
  countries_served: string
  timezone: string
  currency: string
  annual_target: string
  current_date: string
  dataset_id: string
}

const updateBusinessContext = async (connectionId: string, businessContext: BusinessContext) => {
  try {
    const response = await fetch("/api/business-context", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        connection_id: connectionId,
        business_context: businessContext,
      }),
    })
    if (!response.ok) throw new Error("Failed to update business context")
    return true
  } catch (error) {
    console.error("Error updating business context:", error)
    throw error
  }
}

const fetchBusinessContext = async (connectionId: string) => {
  try {
    const response = await fetch(`/api/business-context?connection_id=${connectionId}`)
    if (!response.ok) return null
    return await response.json()
  } catch (error) {
    console.error("Error fetching business context:", error)
    return null
  }
}

export function BusinessContextEditor() {
  const [businessContext, setBusinessContext] = useState<BusinessContext>({
    name: "Suraj Kaya",
    preferred_name: "Suraj",
    user_id: "test_user",
    company_name: "Growth Analytics Marketing",
    company_short: "GAM",
    origin_country: "AU",
    countries_served: "Global",
    timezone: "Australia/Sydney",
    currency: "AUD",
    annual_target: "$1.2M",
    current_date: "2025-05-21",
    dataset_id: "piri_red"
  })
  const [isEditing, setIsEditing] = useState(false)
  const [editingContext, setEditingContext] = useState<BusinessContext>(businessContext)
  
  // Use the global connection context instead of hardcoded "001"
  const connectionId = useConnectionId()

  useEffect(() => {
    fetchBusinessContext(connectionId).then((data) => {
      if (data) setBusinessContext(data)
    })
  }, [connectionId]) // Add connectionId to dependencies

  const handleEdit = () => {
    setEditingContext(businessContext)
    setIsEditing(true)
  }

  const handleSave = async () => {
    try {
      await updateBusinessContext(connectionId, editingContext) // Use connectionId instead of editingContext.user_id
      setBusinessContext(editingContext)
      setIsEditing(false)
      toast.success("Business context updated successfully")
    } catch (error) {
      toast.error("Failed to update business context")
      console.error("Error updating business context:", error)
    }
  }

  const handleCancel = () => {
    setEditingContext(businessContext)
    setIsEditing(false)
  }

  const handleChange = (field: keyof BusinessContext, value: string) => {
    setEditingContext((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <div className="flex flex-col h-full bg-background p-6">
      <div className="max-w-4xl mx-auto w-full">
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Business Context</CardTitle>
              {!isEditing && (
                <Button onClick={handleEdit} variant="outline" size="sm">
                  <PencilEditIcon size={16} />
                  Edit
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {isEditing ? (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="name">Full Name</Label>
                    <Input
                      id="name"
                      value={editingContext.name}
                      onChange={(e) => handleChange("name", e.target.value)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="preferred_name">Preferred Name</Label>
                    <Input
                      id="preferred_name"
                      value={editingContext.preferred_name}
                      onChange={(e) => handleChange("preferred_name", e.target.value)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="company_name">Company Name</Label>
                    <Input
                      id="company_name"
                      value={editingContext.company_name}
                      onChange={(e) => handleChange("company_name", e.target.value)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="company_short">Company Short Name</Label>
                    <Input
                      id="company_short"
                      value={editingContext.company_short}
                      onChange={(e) => handleChange("company_short", e.target.value)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="origin_country">Origin Country</Label>
                    <Input
                      id="origin_country"
                      value={editingContext.origin_country}
                      onChange={(e) => handleChange("origin_country", e.target.value)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="countries_served">Countries Served</Label>
                    <Input
                      id="countries_served"
                      value={editingContext.countries_served}
                      onChange={(e) => handleChange("countries_served", e.target.value)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="timezone">Timezone</Label>
                    <Input
                      id="timezone"
                      value={editingContext.timezone}
                      onChange={(e) => handleChange("timezone", e.target.value)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="currency">Currency</Label>
                    <Input
                      id="currency"
                      value={editingContext.currency}
                      onChange={(e) => handleChange("currency", e.target.value)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="annual_target">Annual Target</Label>
                    <Input
                      id="annual_target"
                      value={editingContext.annual_target}
                      onChange={(e) => handleChange("annual_target", e.target.value)}
                    />
                  </div>

                  <div>
                    <Label htmlFor="dataset_id">Dataset ID</Label>
                    <Input
                      id="dataset_id"
                      value={editingContext.dataset_id}
                      onChange={(e) => handleChange("dataset_id", e.target.value)}
                      placeholder="Optional dataset identifier"
                    />
                  </div>
                </div>

                <div className="flex gap-3 pt-4">
                  <Button onClick={handleSave}>
                    <CheckCirclFillIcon size={16} />
                    Save Changes
                  </Button>
                  <Button variant="outline" onClick={handleCancel}>
                    <CrossIcon size={16} />
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Full Name</Label>
                    <p className="text-sm">{businessContext.name}</p>
                  </div>

                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Preferred Name</Label>
                    <p className="text-sm">{businessContext.preferred_name}</p>
                  </div>

                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Company Name</Label>
                    <p className="text-sm">{businessContext.company_name}</p>
                  </div>

                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Company Short Name</Label>
                    <p className="text-sm">{businessContext.company_short}</p>
                  </div>

                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Origin Country</Label>
                    <p className="text-sm">{businessContext.origin_country}</p>
                  </div>

                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Countries Served</Label>
                    <p className="text-sm">{businessContext.countries_served}</p>
                  </div>

                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Timezone</Label>
                    <p className="text-sm">{businessContext.timezone}</p>
                  </div>

                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Currency</Label>
                    <p className="text-sm">{businessContext.currency}</p>
                  </div>

                  <div>
                    <Label className="text-sm font-medium text-muted-foreground">Annual Target</Label>
                    <p className="text-sm">{businessContext.annual_target}</p>
                  </div>

                  {businessContext.dataset_id && (
                    <div>
                      <Label className="text-sm font-medium text-muted-foreground">Dataset ID</Label>
                      <p className="text-sm">{businessContext.dataset_id}</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
