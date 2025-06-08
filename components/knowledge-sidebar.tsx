"use client"

import { useState, useEffect } from "react"
import Image from "next/image"
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
import { MessageCircle, FileText, ChevronDown, ChevronRight, NotebookPen, Building2, MousePointerClick, CircleUserRound } from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useConnection } from "@/lib/connection-context"

// Firebase API functions - integrated with your backend
const fetchFirebaseContent = async (connectionId = "001") => {
  try {
    const response = await fetch(`/api/general-context?connection_id=${connectionId}`)
    if (!response.ok) throw new Error("Failed to fetch")
    const data = await response.json()

    console.log("Raw API response:", data) // Debug log

    // Handle different response formats
    if (Array.isArray(data)) {
      // Check if the array contains objects or strings
      if (data.length > 0 && typeof data[0] === "object" && data[0].content) {
        // New format: array of document objects
        return data.map((item: any) => ({
          id: item.id,
          title: item.title || "",
          content: item.content,
          createdAt: item.created_at || "",
          updatedAt: item.updated_at || "",
          author: item.author || "",
          embedding: [],
          index: item.index,
        }))
      } else {
        // Legacy format: array of content strings
        const contentStrings = data.filter((item) => typeof item === "string")
        return contentStrings.map((content: string, index: number) => ({
          id: `${connectionId}_${index}`,
          title: "",
          content: content,
          createdAt: "",
          updatedAt: "",
          author: "",
          embedding: [],
          index: index,
        }))
      }
    } else if (data && typeof data === "object" && data.error) {
      console.error("API returned error:", data.error)
      return []
    } else {
      console.warn("Unexpected API response format:", data)
      return []
    }
  } catch (error) {
    console.error("Error fetching Firebase content:", error)
    return []
  }
}

export const addFirebaseContent = async (connectionId: string, content: string, messageType = "general_context") => {
  try {
    const response = await fetch("/api/general-context/add", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        connection_id: connectionId,
        content,
        message_type: messageType,
      }),
    })
    if (!response.ok) throw new Error("Failed to add content")

    return {
      id: `${connectionId}_${Date.now()}`,
      title: "",
      content,
      createdAt: "",
      updatedAt: "",
      author: "",
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
  connectionId: string,
  index: number,
  newContent: string,
  messageType = "general_context",
) => {
  try {
    const response = await fetch("/api/general-context/update", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        connection_id: connectionId,
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

const deleteFirebaseContent = async (connectionId: string, index: number, messageType = "general_context") => {
  try {
    const response = await fetch("/api/general-context/delete", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        connection_id: connectionId,
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
  title: string
  content: string
  createdAt: string
  updatedAt: string
  author: string
  embedding: number[]
  index: number
}

export type PageView =
  | "chat"
  | "business-context"
  | "events"
  | "event-properties"
  | "user-properties"
  | "annotations"
  | "add-context"
  | "data-dictionary"
  | "document-detail"

// Update the KnowledgeSidebarProps interface to include onContentRefresh and onDocumentClick
interface KnowledgeSidebarProps {
  onNavigate: (view: PageView) => void
  currentView: PageView
  selectedEventId?: string
  onContentRefresh: number
  onDocumentClick?: (doc: any) => void
}

export function KnowledgeSidebar({ onNavigate, currentView, selectedEventId, onContentRefresh, onDocumentClick }: KnowledgeSidebarProps) {
  const [contentItems, setContentItems] = useState<ContentItem[]>([])
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editingContent, setEditingContent] = useState("")
  const [newContent, setNewContent] = useState("")
  const [isAddingNew, setIsAddingNew] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  const [isDataDictionaryOpen, setIsDataDictionaryOpen] = useState(
    currentView === "event-properties" || currentView === "user-properties" || currentView === "data-dictionary"
  )
  const [isCompanyKnowledgeOpen, setIsCompanyKnowledgeOpen] = useState(
    currentView === "business-context" || currentView === "annotations" || currentView === "add-context"
  )

  // Use the global connection context
  const { selectedConnectionId, setSelectedConnectionId, companies } = useConnection()

  // Fetch content on component mount, when connection changes, or when refresh is triggered
  useEffect(() => {
    const loadContent = async () => {
      try {
        setIsLoading(true)
        console.log("[DEBUG] Content refresh triggered.", {
          connectionId: selectedConnectionId,
          refreshTrigger: onContentRefresh
        })
        const items = await fetchFirebaseContent(selectedConnectionId)
        console.log("[DEBUG] Loaded items:", items)
        setContentItems(items)
      } catch (error) {
        console.error("[ERROR] Failed to load content:", error)
        toast.error("Failed to load content")
      } finally {
        setIsLoading(false)
      }
    }
    loadContent()
  }, [selectedConnectionId, onContentRefresh])

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
    if (!editingId) return

    try {
      // Find the item by id to get its index
      const item = contentItems.find((item) => item.id === editingId)
      if (!item) {
        toast.error("Item not found")
        return
      }

      await updateFirebaseContent(selectedConnectionId, item.index, editingContent)
      // Refresh the entire list to get updated content
      const updatedItems = await fetchFirebaseContent(selectedConnectionId)
      setContentItems(updatedItems)
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

    try {
      // Find the item by id to get its index
      const item = contentItems.find((item) => item.id === id)
      if (!item) {
        toast.error("Item not found")
        return
      }

      await deleteFirebaseContent(selectedConnectionId, item.index)
      // Refresh the entire list to get updated indices
      const updatedItems = await fetchFirebaseContent(selectedConnectionId)
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
      await addFirebaseContent(selectedConnectionId, newContent)
      // Refresh the entire list to get proper indices
      const updatedItems = await fetchFirebaseContent(selectedConnectionId)
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
          <Image 
            src="/black_logo.png" 
            alt="VendoAI Logo" 
            width={32} 
            height={32} 
            className="h-8 w-auto"
          />

          {/* Connection Selector Dropdown */}
          <Select value={selectedConnectionId} onValueChange={setSelectedConnectionId}>
            <SelectTrigger className="w-[180px] h-8">
              <SelectValue placeholder="Select connection" />
            </SelectTrigger>
            <SelectContent>
              {companies.map((company) => (
                <SelectItem key={company.id} value={company.id}>
                  {company.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
      </SidebarHeader>

      <SidebarContent>
        {/* Navigation Section */}
        <SidebarGroup>
          <SidebarGroupLabel>Company</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              <SidebarMenuItem>
                <SidebarMenuButton onClick={() => onNavigate("chat")} isActive={currentView === "chat"}>
                  <MessageCircle size={16} />
                  <span>Chat</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
            
              {/* Data Dictionary Parent */}
              <SidebarMenuItem>
                <SidebarMenuButton
                  onClick={() => setIsDataDictionaryOpen((open) => !open)}
                  isActive={
                    currentView === "data-dictionary" ||
                    currentView === "events" ||
                    currentView === "event-properties" ||
                    currentView === "user-properties"
                  }
                >
                  {isDataDictionaryOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                  <span>Data Dictionary</span>
                </SidebarMenuButton>
                {isDataDictionaryOpen && (
                  <SidebarMenu className="ml-6 mt-1">
                    <SidebarMenuItem>
                      <SidebarMenuButton
                        onClick={() => onNavigate("events")}
                        isActive={currentView === "events" }
                      >
                        <MousePointerClick size={16} />
                        <span>Events</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                    <SidebarMenuItem>
                      <SidebarMenuButton
                        onClick={() => onNavigate("user-properties")}
                        isActive={currentView === "user-properties"}
                      >
                        <CircleUserRound size={16} />
                        <span>User Properties</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  </SidebarMenu>
                )}
              </SidebarMenuItem>
              {/* Company Knowledge Parent */}
              <SidebarMenuItem>
                <SidebarMenuButton
                  onClick={() => setIsCompanyKnowledgeOpen((open) => !open)}
                  isActive={
                    currentView === "business-context" ||
                    currentView === "annotations" ||
                    currentView === "add-context"
                  }
                >
                  {isCompanyKnowledgeOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                  <span>Company Knowledge</span>
                </SidebarMenuButton>
                {isCompanyKnowledgeOpen && (
                  <SidebarMenu className="ml-6 mt-1">
                    <SidebarMenuItem>
                      <SidebarMenuButton
                        onClick={() => onNavigate("business-context")}
                        isActive={currentView === "business-context"}
                      >
                        <Building2 size={16} />
                        <span>Business Context</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                    <SidebarMenuItem>
                      <SidebarMenuButton
                        onClick={() => onNavigate("annotations")}
                        isActive={currentView === "annotations"}
                      >
                        <NotebookPen size={16} />
                        <span>Annotations</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                
                    <SidebarGroupContent>
                      <SidebarMenu>
                        {isLoading ? (
                          <div className="text-center text-muted-foreground">Loading content...</div>
                        ) : filteredContent.length === 0 ? (
                          <div className="text-center text-muted-foreground">
                            {searchQuery ? "No matching content found" : "No content available"}
                          </div>
                        ) : (
                          filteredContent.map((item) => (
                            <SidebarMenuItem key={item.id}>
                              <SidebarMenuButton
                                className="w-full justify-start text-left h-auto py-2 flex items-center"
                                onClick={() => onDocumentClick?.(item)}
                              >
                                <FileText size={16} />
                                <span className="truncate">{item.title || 'Untitled'}</span>
                              </SidebarMenuButton>
                            </SidebarMenuItem>
                          ))
                        )}
                      </SidebarMenu>
                    </SidebarGroupContent>
                    {/* Add Context always at the bottom */}
                    <SidebarMenuItem>
                      <SidebarMenuButton
                        onClick={() => onNavigate("add-context")}
                        isActive={currentView === "add-context"}
                      >
                        <PlusIcon size={16} />
                        <span>Add Context</span>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  </SidebarMenu>
                )}
              </SidebarMenuItem>
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}
