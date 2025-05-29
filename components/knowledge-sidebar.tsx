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
import { PlusIcon, PencilEditIcon, TrashIcon, CheckCirclFillIcon, CrossIcon, UserIcon } from "./icons"
import { toast } from "sonner"
import { MessageCircle } from "lucide-react"

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

// Update the KnowledgeSidebarProps interface to include events view
interface KnowledgeSidebarProps {
  onNavigate: (view: "chat" | "business-context" | "events" | "event-details") => void
  currentView: "chat" | "business-context" | "events" | "event-details"
  selectedEventId?: string
}

export function KnowledgeSidebar({ onNavigate, currentView, selectedEventId }: KnowledgeSidebarProps) {
  const [contentItems, setContentItems] = useState<ContentItem[]>([])
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editingContent, setEditingContent] = useState("")
  const [newContent, setNewContent] = useState("")
  const [isAddingNew, setIsAddingNew] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [isLoading, setIsLoading] = useState(true)

  // Fetch content on component mount
  useEffect(() => {
    const loadContent = async () => {
      try {
        console.log("Loading content...")
        const items = await fetchFirebaseContent()
        console.log("Loaded items:", items)
        setContentItems(items)
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

  return (
    <Sidebar>
      <SidebarHeader>
        <div className="flex items-center justify-between p-2">
          <h2 className="text-lg font-semibold">Knowledge Base</h2>
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
        {/* Navigation Section */}
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            {/* Update the SidebarMenu in the Navigation Section to include Events */}
            <SidebarMenu>
              <SidebarMenuItem>
              <SidebarMenuButton onClick={() => onNavigate("chat")} isActive={currentView === "chat"}>
              <MessageCircle size={16} />
                  <span>Chat</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton
                  onClick={() => onNavigate("business-context")}
                  isActive={currentView === "business-context"}
                >
                  <UserIcon />
                  <span>Business Context</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton
                  onClick={() => onNavigate("events")}
                  isActive={currentView === "events" || currentView === "event-details"}
                >
                  <svg
                    width="16"
                    height="16"
                    viewBox="0 0 16 16"
                    fill="none"
                    xmlns="http://www.w3.org/2000/svg"
                    className="mr-2"
                  >
                    <path
                      fillRule="evenodd"
                      clipRule="evenodd"
                      d="M2 2.5C2 1.67157 2.67157 1 3.5 1H12.5C13.3284 1 14 1.67157 14 2.5V13.5C14 14.3284 13.3284 15 12.5 15H3.5C2.67157 15 2 14.3284 2 13.5V2.5ZM3.5 2.5H12.5V13.5H3.5V2.5ZM5 5.5C5 5.22386 5.22386 5 5.5 5H10.5C10.7761 5 11 5.22386 11 5.5C11 5.77614 10.7761 6 10.5 6H5.5C5.22386 6 5 5.77614 5 5.5ZM5 8.5C5 8.22386 5.22386 8 5.5 8H10.5C10.7761 8 11 8.22386 11 8.5C11 8.77614 10.7761 9 10.5 9H5.5C5.22386 9 5 8.77614 5 8.5ZM5 11.5C5 11.2239 5.22386 11 5.5 11H8.5C8.77614 11 9 11.2239 9 11.5C9 11.7761 8.77614 12 8.5 12H5.5C5.22386 12 5 11.7761 5 11.5Z"
                      fill="currentColor"
                    />
                  </svg>
                  <span>Data Dictionary</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            </SidebarMenu>
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
