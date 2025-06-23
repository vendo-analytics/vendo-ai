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
} from "@/components/ui/sidebar"
import { PlusIcon } from "./icons"
import { toast } from "sonner"
import {
  Database,
  MessageCircle,
  FileText,
  ChevronDown,
  ChevronRight,
  NotebookPen,
  Building2,
  MousePointerClick,
  CircleUserRound,
  MoreVertical,
  Brain,
  BarChart3,
} from "lucide-react"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useConnection } from "@/lib/connection-context"
import { useADKWebSocket } from "@/hooks/useADKWebSocket"
import type { Message } from "ai"

// Firebase API functions - integrated with your backend
const fetchFirebaseContent = async (connectionId = "gb1uauyn0Khjcs4Fgxh8") => {
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

interface ChatHistoryItem {
  id: string
  title: string
  date: Date
  preview?: string
}

export type PageView =
  | "dashboard"
  | "chat"
  | "business-context"
  | "mixpanel-event-schema"
  | "user-properties"
  | "annotations"
  | "add-context"
  | "data-dictionary"
  | "document-detail"
  | "agents"
  | "agent-detail"

// Update the KnowledgeSidebarProps interface to include onContentRefresh and onDocumentClick
interface KnowledgeSidebarProps {
  onNavigate: (view: PageView) => void
  currentView: PageView
  selectedEventId?: string
  onContentRefresh: number
  onDocumentClick?: (doc: any) => void
  onChatSelect?: (chatId: string, messages: Message[]) => void
}

export function KnowledgeSidebar({
  onNavigate,
  currentView,
  selectedEventId,
  onContentRefresh,
  onDocumentClick,
  onChatSelect,
}: KnowledgeSidebarProps) {
  const [contentItems, setContentItems] = useState<ContentItem[]>([])
  const [editingId, setEditingId] = useState<string | null>(null)
  const [editingContent, setEditingContent] = useState("")
  const [newContent, setNewContent] = useState("")
  const [isAddingNew, setIsAddingNew] = useState(false)
  const [searchQuery, setSearchQuery] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  const [isDataDictionaryOpen, setIsDataDictionaryOpen] = useState(
    currentView === "mixpanel-event-schema" || currentView === "user-properties"
  )
  const [isCompanyKnowledgeOpen, setIsCompanyKnowledgeOpen] = useState(
    currentView === "business-context" || currentView === "annotations" || currentView === "add-context",
  )
  const [isRecentOpen, setIsRecentOpen] = useState(true)
  const [isTodayOpen, setIsTodayOpen] = useState(true)
  const [isPrevious7DaysOpen, setIsPrevious7DaysOpen] = useState(true)
  const [isPrevious30DaysOpen, setIsPrevious30DaysOpen] = useState(true)
  const [selectedChatId, setSelectedChatId] = useState<string | null>(null)

  // Replace mock chat history with state from Firebase
  const [chatHistory, setChatHistory] = useState<{
    today: ChatHistoryItem[];
    previous7Days: ChatHistoryItem[];
    previous30Days: ChatHistoryItem[];
  }>({
    today: [],
    previous7Days: [],
    previous30Days: []
  });

  // Use the global connection context
  const { selectedConnectionId, setSelectedConnectionId, companies } = useConnection()

  // Get the WebSocket hook context
  const { loadSession, createNewSession } = useADKWebSocket({
    onTextMessage: (text, isFinal, isPartial, role) => {
      // Handle replayed messages
      // You might want to pass this up to the parent component
    },
    onTurnComplete: () => {
      // Handle turn complete
    }
  });

  // Fetch content on component mount, when connection changes, or when refresh is triggered
  useEffect(() => {
    const loadContent = async () => {
      try {
        setIsLoading(true)
        console.log("[DEBUG] Content refresh triggered.", {
          connectionId: selectedConnectionId,
          refreshTrigger: onContentRefresh,
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

  // Add effect to fetch chat history when connection changes
  useEffect(() => {
    const loadChatHistory = async () => {
      try {
        const history = await fetchChatHistory(selectedConnectionId);
        setChatHistory(history);
      } catch (error) {
        console.error("Failed to load chat history:", error);
        toast.error("Failed to load chat history");
      }
    };
    
    loadChatHistory();
  }, [selectedConnectionId]);

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

  const handleChatClick = async (chatId: string) => {
    try {
      setSelectedChatId(chatId);
      await loadSession(chatId);
      onNavigate("chat");
      
      // Refresh chat history after loading a chat
      const history = await fetchChatHistory(selectedConnectionId);
      setChatHistory(history);
      
      if (onChatSelect) {
        onChatSelect(chatId, []);
      }
    } catch (error) {
      console.error("Error loading chat:", error);
      toast.error("Failed to load chat session");
    }
  };

  const handleNewChat = async () => {
    try {
      const newSessionId = createNewSession();
      setSelectedChatId(null);
      onNavigate("chat");
      
      if (onChatSelect) {
        onChatSelect(newSessionId, []);
      }
    } catch (error) {
      console.error("Error creating new chat:", error);
      toast.error("Failed to create new chat");
    }
  };

  return (
    <Sidebar>
      <SidebarHeader>
        <div className="flex items-center justify-between p-2">
          <Image src="/black_logo.png" alt="VendoAI Logo" width={32} height={32} className="h-8 w-auto" />

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
                <SidebarMenuButton onClick={() => onNavigate("dashboard")} isActive={currentView === "dashboard"}>
                  <BarChart3 size={16} />
                  <span>Dashboard</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton 
                  onClick={handleNewChat} 
                  isActive={currentView === "chat" && !selectedChatId}
                >
                  <MessageCircle size={16} />
                  <span>Chat</span>
                </SidebarMenuButton>
              </SidebarMenuItem>
              <SidebarMenuItem>
                <SidebarMenuButton onClick={() => onNavigate("agents")} isActive={currentView === "agents"}>
                  <Brain size={16} />
                  <span>AI Agents</span>
                </SidebarMenuButton>
              </SidebarMenuItem>

              {/* Data Dictionary Parent */}
              <SidebarMenuItem>
                <SidebarMenuButton
                  onClick={() => setIsDataDictionaryOpen((open) => !open)}
                  isActive={
                    currentView === "data-dictionary" ||
                    currentView === "user-properties" ||
                    currentView === "mixpanel-event-schema"
                  }
                >
                  {isDataDictionaryOpen ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
                  <span>Data Dictionary</span>
                </SidebarMenuButton>
                {isDataDictionaryOpen && (
                  <SidebarMenu className="ml-6 mt-1">
                     <SidebarMenuItem>
                <SidebarMenuButton
                  onClick={() => onNavigate("mixpanel-event-schema")}
                  isActive={currentView === "mixpanel-event-schema"}
                >
                  <Database size={16} />
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
                    currentView === "business-context" || currentView === "annotations" || currentView === "add-context"
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
                                <span className="truncate">{item.title || "Untitled"}</span>
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

        {/* Chat History Section */}
        <SidebarGroup>
          <div className="border-t border-border/50 mt-2 pt-2">
            <SidebarGroupLabel className="px-2">Chat History</SidebarGroupLabel>

            <SidebarGroupContent>
              {/* Today's Chats */}
              <div className="px-4 py-1">
                <div
                  className="text-xs font-medium text-muted-foreground cursor-pointer flex items-center"
                  onClick={() => setIsTodayOpen(!isTodayOpen)}
                >
                  {isTodayOpen ? (
                    <ChevronDown size={12} className="mr-1" />
                  ) : (
                    <ChevronRight size={12} className="mr-1" />
                  )}
                  Today
                </div>
                {isTodayOpen && (
                  <div className="mt-1">
                    {chatHistory.today.map((chat) => (
                      <div
                        key={chat.id}
                        className={`flex items-center justify-between py-1 px-2 hover:bg-muted/50 rounded-md cursor-pointer group ${
                          selectedChatId === chat.id ? 'bg-muted' : ''
                        }`}
                        onClick={() => handleChatClick(chat.id)}
                      >
                        <div className="text-sm truncate">{chat.title}</div>
                        <MoreVertical size={14} className="opacity-0 group-hover:opacity-100 text-muted-foreground" />
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Previous 7 Days */}
              <div className="px-4 py-1">
                <div
                  className="text-xs font-medium text-muted-foreground cursor-pointer flex items-center"
                  onClick={() => setIsPrevious7DaysOpen(!isPrevious7DaysOpen)}
                >
                  {isPrevious7DaysOpen ? (
                    <ChevronDown size={12} className="mr-1" />
                  ) : (
                    <ChevronRight size={12} className="mr-1" />
                  )}
                  Previous 7 Days
                </div>
                {isPrevious7DaysOpen && (
                  <div className="mt-1">
                    {chatHistory.previous7Days.map((chat) => (
                      <div
                        key={chat.id}
                        className={`flex items-center justify-between py-1 px-2 hover:bg-muted/50 rounded-md cursor-pointer group ${
                          selectedChatId === chat.id ? 'bg-muted' : ''
                        }`}
                        onClick={() => handleChatClick(chat.id)}
                      >
                        <div className="text-sm truncate">{chat.title}</div>
                        <MoreVertical size={14} className="opacity-0 group-hover:opacity-100 text-muted-foreground" />
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Previous 30 Days */}
              <div className="px-4 py-1">
                <div
                  className="text-xs font-medium text-muted-foreground cursor-pointer flex items-center"
                  onClick={() => setIsPrevious30DaysOpen(!isPrevious30DaysOpen)}
                >
                  {isPrevious30DaysOpen ? (
                    <ChevronDown size={12} className="mr-1" />
                  ) : (
                    <ChevronRight size={12} className="mr-1" />
                  )}
                  Previous 30 Days
                </div>
                {isPrevious30DaysOpen && (
                  <div className="mt-1">
                    {chatHistory.previous30Days.map((chat) => (
                      <div
                        key={chat.id}
                        className={`flex items-center justify-between py-1 px-2 hover:bg-muted/50 rounded-md cursor-pointer group ${
                          selectedChatId === chat.id ? 'bg-muted' : ''
                        }`}
                        onClick={() => handleChatClick(chat.id)}
                      >
                        <div className="text-sm truncate">{chat.title}</div>
                        <MoreVertical size={14} className="opacity-0 group-hover:opacity-100 text-muted-foreground" />
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </SidebarGroupContent>
          </div>
        </SidebarGroup>
      </SidebarContent>
    </Sidebar>
  )
}

// Add this near the top with other Firebase API functions
const fetchChatHistory = async (connectionId: string) => {
  try {
    const response = await fetch(`/api/chat/history?connection_id=${connectionId}`);
    if (!response.ok) throw new Error("Failed to fetch chat history");
    const data = await response.json();
    
    // Group chats by date ranges
    const today = new Date();
    const sevenDaysAgo = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    const thirtyDaysAgo = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);

    // Helper function to format chat title
    const formatChatTitle = (chat: any) => {
      // Use the content (summary) as the title, or fallback to timestamp
      if (chat.content) {
        return chat.content;
      }
      const date = new Date(chat.timestamp);
      return `Chat ${date.toLocaleString()}`;
    };

    // Helper function to group chats by date
    const groupChats = (chats: any[]) => {
      return {
        today: chats
          .filter((chat) => {
            const chatDate = new Date(chat.timestamp);
            return chatDate.toDateString() === today.toDateString();
          })
          .map((chat) => ({
            id: chat.session_id,
            title: formatChatTitle(chat),
            date: new Date(chat.timestamp),
            preview: chat.content
          })),
        previous7Days: chats
          .filter((chat) => {
            const chatDate = new Date(chat.timestamp);
            return chatDate > sevenDaysAgo && chatDate.toDateString() !== today.toDateString();
          })
          .map((chat) => ({
            id: chat.session_id,
            title: formatChatTitle(chat),
            date: new Date(chat.timestamp),
            preview: chat.content
          })),
        previous30Days: chats
          .filter((chat) => {
            const chatDate = new Date(chat.timestamp);
            return chatDate > thirtyDaysAgo && chatDate <= sevenDaysAgo;
          })
          .map((chat) => ({
            id: chat.session_id,
            title: formatChatTitle(chat),
            date: new Date(chat.timestamp),
            preview: chat.content
          }))
      };
    };

    // Sort chats by date (newest first) before grouping
    const sortedChats = data.sort((a: any, b: any) => {
      return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
    });

    return groupChats(sortedChats);
  } catch (error) {
    console.error("Error fetching chat history:", error);
    return {
      today: [],
      previous7Days: [],
      previous30Days: []
    };
  }
};
