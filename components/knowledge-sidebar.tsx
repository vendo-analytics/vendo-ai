"use client"

import { useState, useEffect } from "react"
import {
  Sidebar,
  SidebarContent,
  SidebarHeader,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarInput,
} from "@/components/ui/sidebar"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { PlusIcon, PencilEditIcon, TrashIcon, CheckCirclFillIcon, CrossIcon } from "./icons"
import { toast } from "sonner"

// Firebase API functions - integrated with your backend
const fetchFirebaseContent = async (userId = "001") => {
  try {
    const response = await fetch(`/api/context/requirements?user_id=${userId}`)
    if (!response.ok) throw new Error("Failed to fetch")
    const data = await response.json()

    console.log("Raw API response:", data) // Debug log

    // Handle different response formats
    let contentStrings: string[] = []

    if (Array.isArray(data)) {
      contentStrings = data.filter((item) => typeof item === "string")
    } else if (data && typeof data === "object" && data.error) {
      console.error("API returned error:", data.error)
      return []
    } else {
      console.warn("Unexpected API response format:", data)
      return []
    }

    // Transform content strings to match ContentItem interface
    return contentStrings.map((content: string, index: number) => ({
      id: `${userId}_${index}`,
      content: content,
      embedding: [],
      index: index,
    }))
  } catch (error) {
    console.error("Error fetching Firebase content:", error)
    return []
  }
}

const fetchBusinessContext = async (userId = "001") => {
  try {
    const response = await fetch(`/api/context/business?user_id=${userId}`)
    if (!response.ok) {
      if (response.status === 404) {
        console.log("No business context found in Firebase, using defaults")
        return null
      }
      throw new Error("Failed to fetch business context")
    }
    const data = await response.json()
    console.log("Business context from Firebase:", data)
    return data
  } catch (error) {
    console.error("Error fetching business context:", error)
    return null
  }
}

const updateBusinessContext = async (userId: string, businessContext: BusinessContext) => {
  try {
    const response = await fetch("/api/context/business", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
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

const addFirebaseContent = async (userId: string, content: string, messageType = "requirements") => {
  try {
    const response = await fetch("/api/context/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        content,
        message_type: messageType,
      }),
    })
    if (!response.ok) throw new Error("Failed to add content")

    return {
      id: `${userId}_${Date.now()}`,
      content,
      embedding: [],
      index: Date.now(),
    }
  } catch (error) {
    console.error("Error adding Firebase content:", error)
    throw error
  }
}

// Note: Update and delete operations are now implemented with index-based backend endpoints
const updateFirebaseContent = async (
  userId: string,
  index: number,
  newContent: string,
  messageType = "requirements",
) => {
  try {
    const response = await fetch("/api/context/update", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        index: index,
        new_content: newContent,
        message_type: messageType,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || "Failed to update content")
    }

    return true
  } catch (error) {
    console.error("Error updating Firebase content:", error)
    throw error
  }
}

const deleteFirebaseContent = async (userId: string, index: number, messageType = "requirements") => {
  try {
    const response = await fetch("/api/context/delete", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        user_id: userId,
        index: index,
        message_type: messageType,
      }),
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.error || "Failed to delete content")
    }

    return true
  } catch (error) {
    console.error("Error deleting Firebase content:", error)
    throw error
  }
}

interface ContentItem {
  id: string
  content: string
  embedding: number[]
  index: number
}

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

export function KnowledgeSidebar() {
  const [contentItems, setContentItems] = useState<ContentItem[]>([])
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editingContent, setEditingContent] = useState("")
  const [newContent, setNewContent] = useState("")
  const [isAddingNew, setIsAddingNew] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [isLoading, setIsLoading] = useState(true)

  // Business Context State
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
    dataset_id: "1234567890"
  })
  const [isEditingContext, setIsEditingContext] = useState(false)
  const [editingContext, setEditingContext] = useState<BusinessContext>(businessContext)

  // Fetch content on component mount
  useEffect(() => {
    const loadContent = async () => {
      try {
        console.log("Loading content...")
        const items = await fetchFirebaseContent()
        console.log("Loaded items:", items)
        setContentItems(items)
        
        // Load business context from Firebase
        const firebaseBusinessContext = await fetchBusinessContext("001")
        if (firebaseBusinessContext) {
          // Merge with default values to ensure all required fields are present
          const mergedContext = {
            name: firebaseBusinessContext.name || "Suraj Kaya",
            preferred_name: firebaseBusinessContext.preferred_name || "Suraj",
            user_id: firebaseBusinessContext.user_id || "test_user",
            company_name: firebaseBusinessContext.company_name || "Growth Analytics Marketing",
            company_short: firebaseBusinessContext.company_short || "GAM",
            origin_country: firebaseBusinessContext.origin_country || "AU",
            countries_served: firebaseBusinessContext.countries_served || "Global",
            timezone: firebaseBusinessContext.timezone || "Australia/Sydney",
            currency: firebaseBusinessContext.currency || "AUD",
            annual_target: firebaseBusinessContext.annual_target || "$1.2M",
            current_date: firebaseBusinessContext.current_date || "2025-05-21",
            dataset_id: firebaseBusinessContext.dataset_id || "1234567890"
          }
          setBusinessContext(mergedContext)
          setEditingContext(mergedContext)
        }
      } catch (error) {
        toast.error("Failed to load content")
        console.error("Error loading content:", error)
      } finally {
        setIsLoading(false)
      }
    }
    loadContent()
  }, [])

  // Filter content based on search query
  const filteredContent = contentItems.filter((item) => {
    // Add type safety check
    if (!item || typeof item.content !== "string") {
      console.warn("Invalid content item:", item)
      return false
    }
    return item.content.toLowerCase().includes(searchQuery.toLowerCase())
  })

  const handleEdit = (item: ContentItem) => {
    setEditingId(item.id)
    setEditingContent(item.content)
  }

  const handleSaveEdit = async () => {
    if (!editingId || !editingContent.trim()) return

    // Find the original content
    const originalItem = contentItems.find((item) => item.id === editingId)
    if (!originalItem) return

    try {
      await updateFirebaseContent("001", originalItem.index, editingContent)
      setContentItems((prev) =>
        prev.map((item) => (item.id === editingId ? { ...item, content: editingContent } : item)),
      )
      setEditingId(null)
      setEditingContent("")
      toast.success("Content updated successfully")
    } catch (error) {
      toast.error("Failed to update content")
      console.error("Error updating content:", error)
    }
  }

  const handleCancelEdit = () => {
    setEditingId(null)
    setEditingContent("")
  }

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this item?")) return

    // Find the item to get its index
    const itemToDelete = contentItems.find((item) => item.id === id)
    if (!itemToDelete) return

    try {
      await deleteFirebaseContent("001", itemToDelete.index)
      // Refresh the entire list since indices change after deletion
      const updatedItems = await fetchFirebaseContent("001")
      setContentItems(updatedItems)
      toast.success("Content deleted successfully")
    } catch (error) {
      toast.error("Failed to delete content")
      console.error("Error deleting content:", error)
    }
  }

  const handleAddNew = async () => {
    if (!newContent.trim()) return

    try {
      await addFirebaseContent("001", newContent)
      // Refresh the entire list to get proper indices
      const updatedItems = await fetchFirebaseContent("001")
      setContentItems(updatedItems)
      setNewContent("")
      setIsAddingNew(false)
      toast.success("Content added successfully")
    } catch (error) {
      toast.error("Failed to add content")
      console.error("Error adding content:", error)
    }
  }

  // Business Context Handlers
  const handleEditContext = () => {
    setEditingContext(businessContext)
    setIsEditingContext(true)
  }

  const handleSaveContext = async () => {
    try {
      await updateBusinessContext("001", editingContext)
      setBusinessContext(editingContext)
      setIsEditingContext(false)
      toast.success("Business context updated successfully")
    } catch (error) {
      toast.error("Failed to update business context")
      console.error("Error updating business context:", error)
    }
  }

  const handleCancelContext = () => {
    setEditingContext(businessContext)
    setIsEditingContext(false)
  }

  const handleContextChange = (field: keyof BusinessContext, value: string) => {
    setEditingContext((prev) => ({ ...prev, [field]: value }))
  }

  return (
    <Sidebar>
      <SidebarHeader>
        <div className="flex items-center justify-between p-2">
          <h2 className="text-lg font-semibold">Context</h2>
          <Button size="sm" onClick={() => setIsAddingNew(true)} className="h-8 w-8 p-0">
            <PlusIcon size={16} />
          </Button>
        </div>

        {/* Search Input */}
        <div className="p-2">
          <SidebarInput
            placeholder="Search content..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </SidebarHeader>

      <SidebarContent>
        {/* Business Context Section */}
        <SidebarGroup>
          <SidebarGroupLabel>Business Context</SidebarGroupLabel>
          <SidebarGroupContent>
            {isEditingContext ? (
              <div className="p-2 space-y-3 border rounded-md bg-muted/50">
                <div>
                  <Label htmlFor="name" className="text-xs">
                    Full Name
                  </Label>
                  <Input
                    id="name"
                    value={editingContext.name}
                    onChange={(e) => handleContextChange("name", e.target.value)}
                    className="h-8 text-xs"
                  />
                </div>

                <div>
                  <Label htmlFor="preferred_name" className="text-xs">
                    Preferred Name
                  </Label>
                  <Input
                    id="preferred_name"
                    value={editingContext.preferred_name}
                    onChange={(e) => handleContextChange("preferred_name", e.target.value)}
                    className="h-8 text-xs"
                  />
                </div>

                <div>
                  <Label htmlFor="company_name" className="text-xs">
                    Company Name
                  </Label>
                  <Input
                    id="company_name"
                    value={editingContext.company_name}
                    onChange={(e) => handleContextChange("company_name", e.target.value)}
                    className="h-8 text-xs"
                  />
                </div>

                <div>
                  <Label htmlFor="company_short" className="text-xs">
                    Company Short Name
                  </Label>
                  <Input
                    id="company_short"
                    value={editingContext.company_short}
                    onChange={(e) => handleContextChange("company_short", e.target.value)}
                    className="h-8 text-xs"
                  />
                </div>

                <div>
                  <Label htmlFor="origin_country" className="text-xs">
                    Origin Country
                  </Label>
                  <Input
                    id="origin_country"
                    value={editingContext.origin_country}
                    onChange={(e) => handleContextChange("origin_country", e.target.value)}
                    className="h-8 text-xs"
                  />
                </div>

                <div>
                  <Label htmlFor="countries_served" className="text-xs">
                    Countries Served
                  </Label>
                  <Input
                    id="countries_served"
                    value={editingContext.countries_served}
                    onChange={(e) => handleContextChange("countries_served", e.target.value)}
                    className="h-8 text-xs"
                  />
                </div>

                <div>
                  <Label htmlFor="timezone" className="text-xs">
                    Timezone
                  </Label>
                  <Input
                    id="timezone"
                    value={editingContext.timezone}
                    onChange={(e) => handleContextChange("timezone", e.target.value)}
                    className="h-8 text-xs"
                  />
                </div>

                <div>
                  <Label htmlFor="currency" className="text-xs">
                    Currency
                  </Label>
                  <Input
                    id="currency"
                    value={editingContext.currency}
                    onChange={(e) => handleContextChange("currency", e.target.value)}
                    className="h-8 text-xs"
                  />
                </div>

                <div>
                  <Label htmlFor="annual_target" className="text-xs">
                    Annual Target
                  </Label>
                  <Input
                    id="annual_target"
                    value={editingContext.annual_target}
                    onChange={(e) => handleContextChange("annual_target", e.target.value)}
                    className="h-8 text-xs"
                  />
                </div>

                <div>
                  <Label htmlFor="dataset_id" className="text-xs">
                    Dataset ID
                  </Label>
                  <Input
                    id="dataset_id"
                    value={editingContext.dataset_id || ""}
                    onChange={(e) => handleContextChange("dataset_id", e.target.value)}
                    className="h-8 text-xs"
                    placeholder="Optional connection identifier"
                  />
                </div>

                <div className="flex gap-2 pt-2">
                  <Button size="sm" onClick={handleSaveContext} className="flex-1">
                    <CheckCirclFillIcon size={14} />
                    Save
                  </Button>
                  <Button size="sm" variant="outline" onClick={handleCancelContext} className="flex-1">
                    <CrossIcon size={14} />
                    Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <div className="p-2 space-y-2 border rounded-md bg-muted/20">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium text-sm">{businessContext.preferred_name}</h4>
                  <Button size="sm" variant="ghost" className="h-6 w-6 p-0" onClick={handleEditContext}>
                    <PencilEditIcon size={12} />
                  </Button>
                </div>
                <div className="text-xs text-muted-foreground space-y-1">
                  <div>
                    <strong>Company:</strong> {businessContext.company_name} ({businessContext.company_short})
                  </div>
                  <div>
                    <strong>Location:</strong> {businessContext.origin_country}
                  </div>
                  <div>
                    <strong>Target:</strong> {businessContext.annual_target}
                  </div>
                  <div>
                    <strong>Timezone:</strong> {businessContext.timezone}
                  </div>
                  {businessContext.dataset_id && (
                    <div>
                      <strong>Dataset ID:</strong> {businessContext.dataset_id}
                    </div>
                  )}
                </div>
              </div>
            )}
          </SidebarGroupContent>
        </SidebarGroup>

        {/* Content Items Section */}
        <SidebarGroup>
          <SidebarGroupLabel>Content Items ({filteredContent.length})</SidebarGroupLabel>

          <SidebarGroupContent>
            {/* Add New Item Form */}
            {isAddingNew && (
              <div className="p-2 border rounded-md mb-2 bg-muted/50">
                <Textarea
                  placeholder="Enter new content..."
                  value={newContent}
                  onChange={(e) => setNewContent(e.target.value)}
                  className="mb-2 min-h-[80px]"
                />
                <div className="flex gap-2">
                  <Button size="sm" onClick={handleAddNew}>
                    <CheckCirclFillIcon size={14} />
                    Add
                  </Button>
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => {
                      setIsAddingNew(false)
                      setNewContent("")
                    }}
                  >
                    <CrossIcon size={14} />
                    Cancel
                  </Button>
                </div>
              </div>
            )}

            <SidebarMenu>
              {isLoading ? (
                <div className="p-4 text-center text-muted-foreground">Loading content...</div>
              ) : filteredContent.length === 0 ? (
                <div className="p-4 text-center text-muted-foreground">
                  {searchQuery ? "No matching content found" : "No content available"}
                </div>
              ) : (
                filteredContent.map((item) => (
                  <SidebarMenuItem key={item.id}>
                    {editingId === item.id ? (
                      // Edit Mode
                      <div className="p-2 border rounded-md bg-muted/50">
                        <Textarea
                          value={editingContent}
                          onChange={(e) => setEditingContent(e.target.value)}
                          className="mb-2 min-h-[80px]"
                        />
                        <div className="flex gap-2">
                          <Button size="sm" onClick={handleSaveEdit}>
                            <CheckCirclFillIcon size={14} />
                            Save
                          </Button>
                          <Button size="sm" variant="outline" onClick={handleCancelEdit}>
                            <CrossIcon size={14} />
                            Cancel
                          </Button>
                        </div>
                      </div>
                    ) : (
                      // View Mode
                      <div className="group relative">
                        <SidebarMenuButton className="w-full justify-start text-left h-auto py-2">
                          <div className="flex-1 min-w-0">
                            <p className="text-sm line-clamp-3 break-words">{item.content}</p>
                          </div>
                        </SidebarMenuButton>

                        {/* Action Buttons */}
                        <div className="absolute right-2 top-2 opacity-0 group-hover:opacity-100 transition-opacity flex gap-1">
                          <Button size="sm" variant="ghost" className="h-6 w-6 p-0" onClick={() => handleEdit(item)}>
                            <PencilEditIcon size={12} />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-6 w-6 p-0 text-destructive hover:text-destructive"
                            onClick={() => handleDelete(item.id)}
                          >
                            <TrashIcon size={12} />
                          </Button>
                        </div>
                      </div>
                    )}
                  </SidebarMenuItem>
                ))
              )}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}
