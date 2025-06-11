"use client"

import { useState, useCallback, useEffect } from "react"
import type { Message } from "ai"
import { Chat } from "@/components/chat"
import { BusinessContextEditor } from "@/components/business-context-editor"
import { KnowledgeSidebar } from "@/components/knowledge-sidebar"
import { AddContextView } from "@/components/add-context-view"
import { SidebarInset } from "@/components/ui/sidebar"
import { Navbar } from "@/components/navbar"
import { Separator } from "@/components/ui/separator"
import { Button } from "@/components/ui/button"
import { MenuIcon } from "@/components/icons"
import { useSidebar } from "@/components/ui/sidebar"
import { EventsView } from "@/components/events-view"
import { EventProperties } from "@/components/event-properties"
import { UserProperties } from "@/components/user-properties"
import { AnnotationsView } from "@/components/annotations-view"
import { DocumentDetailView } from "@/components/document-detail-view"
import { toast } from "sonner"
import { addFirebaseContent } from "@/lib/firebase-content"
import { useConnectionId } from "@/lib/connection-context"
import { MixpanelEventSchemaView } from "@/components/mixpanel-event-schema-view"

type PageView =
  | "chat"
  | "business-context"
  | "mixpanel-event-schema"
  | "user-properties"
  | "annotations"
  | "add-context"
  | "data-dictionary"
  | "document-detail"

function CustomSidebarTrigger() {
  const { toggleSidebar } = useSidebar()

  return (
    <Button variant="ghost" size="icon" onClick={toggleSidebar} className="h-8 w-8">
      <MenuIcon size={16} />
      <span className="sr-only">Toggle Sidebar</span>
    </Button>
  )
}

async function updateDocument(connectionId: string, index: number, newContent: string, newTitle: string) {
  try {
    const response = await fetch("/api/general-context/update", {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        connection_id: connectionId,
        index: index,
        new_content: newContent,
        new_title: newTitle,
        message_type: "general_context"
      }),
    })
    if (!response.ok) throw new Error("Failed to update document")
    toast.success("Document updated successfully")
  } catch (error) {
    toast.error("Failed to update document")
    throw error
  }
}

async function deleteDocument(connectionId: string, index: number) {
  try {
    const response = await fetch("/api/general-context/delete", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        connection_id: connectionId,
        index: index,
        message_type: "general_context"
      }),
    })
    if (!response.ok) throw new Error("Failed to delete document")
    toast.success("Document deleted successfully")
  } catch (error) {
    toast.error("Failed to delete document")
    throw error
  }
}

export default function Page() {
  const [currentView, setCurrentView] = useState<PageView>("chat")
  const [selectedChatId, setSelectedChatId] = useState<string>("001")
  const [chatMessages, setChatMessages] = useState<Message[]>([])
  const [selectedEvent, setSelectedEvent] = useState<any>(null)
  const [selectedDocument, setSelectedDocument] = useState<any>(null)
  const [contentRefreshTrigger, setContentRefreshTrigger] = useState(0)
  const [isDebugMode, setIsDebugMode] = useState(false)

  // Use the connection context
  const connectionId = useConnectionId()

  // Fetch initial debug mode state
  useEffect(() => {
    const fetchDebugMode = async () => {
      try {
        const response = await fetch(`/api/debug-mode?connection_id=${connectionId}`)
        if (!response.ok) throw new Error("Failed to fetch debug mode")
        const data = await response.json()
        setIsDebugMode(data.debug_mode)
      } catch (error) {
        console.error("Failed to fetch debug mode:", error)
      }
    }
    
    if (connectionId) {
      fetchDebugMode()
    }
  }, [connectionId])

  const getPageTitle = () => {
    switch (currentView) {
      case "business-context":
        return "Business Context"
      case "user-properties":
        return "User Properties"
      case "annotations":
        return "Annotations"
      case "add-context":
        return "Add Context"
      case "data-dictionary":
        return "Data Dictionary"
      case "document-detail":
        return "Custom Document"
      case "mixpanel-event-schema":
        return "Mixpanel Event Schema"
      case "chat":
      default:
        return "Vendo AI Demo"
    }
  }

  const handleContentAdded = useCallback(() => {
    console.log("[DEBUG] Content added, triggering refresh")
    setContentRefreshTrigger(prev => {
      console.log("[DEBUG] Updating refresh trigger from", prev, "to", prev + 1)
      return prev + 1
    })
  }, [])

  const handleNavigateBackFromAddContext = () => {
    setCurrentView("chat")
  }

  const handleChatSelect = (chatId: string) => {
    setSelectedChatId(chatId)
    setCurrentView("chat")
  }

  const handleNavigate = (view: PageView) => {
    setCurrentView(view)
  }

  const toggleDebugMode = async () => {
    try {
      const newValue = !isDebugMode
      const response = await fetch("/api/debug-mode", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          connection_id: connectionId,
          debug_mode: newValue
        })
      })
      
      if (!response.ok) throw new Error("Failed to update debug mode")
      
      setIsDebugMode(newValue)
      console.log(`Debug mode ${newValue ? "enabled" : "disabled"}`)
      if (newValue) {
        toast.success("Debug mode enabled")
      } else {
        toast.success("Debug mode disabled")
      }
    } catch (error) {
      console.error("Failed to toggle debug mode:", error)
      toast.error("Failed to toggle debug mode")
    }
  }

  // New: Data Dictionary selection view
  const renderDataDictionaryMenu = () => (
    <div className="flex flex-col gap-4 p-8">
      <h2 className="text-lg font-semibold mb-2">Data Dictionary</h2>
      <Button variant="outline" onClick={() => setCurrentView("mixpanel-event-schema")}>Mixpanel Event Schema</Button>
      <Button variant="outline" onClick={() => setCurrentView("user-properties")}>User Properties</Button>
    </div>
  )

  return (
    <>
      <KnowledgeSidebar
        onNavigate={handleNavigate}
        currentView={currentView}
        selectedEventId={selectedEvent?.id}
        onContentRefresh={contentRefreshTrigger}
        onDocumentClick={(doc) => {
          setCurrentView("document-detail");
          setSelectedDocument(doc);
        }}
        onChatSelect={handleChatSelect}
      />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 border-b px-4">
          <CustomSidebarTrigger />
          <Separator orientation="vertical" className="mr-2 h-4" />
          <h1 className="text-xl font-bold">{getPageTitle()}</h1>
          {/* Debug Toggle in Header */}
          <div className="ml-auto flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="text-sm text-muted-foreground">Debug</span>
              <button
                onClick={toggleDebugMode}
                className={`relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 ${
                  isDebugMode ? "bg-orange-500" : "bg-gray-200"
                }`}
                role="switch"
                aria-checked={isDebugMode}
                aria-label="Toggle debug mode"
              >
                <span
                  className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
                    isDebugMode ? "translate-x-5" : "translate-x-1"
                  }`}
                />
              </button>
            </div>

            <div className="hidden md:block">
              <Navbar />
            </div>
          </div>
        </header>
          
        <div className="flex flex-1 flex-col">
          {currentView === "chat" && (
            <Chat 
              chatId={selectedChatId} 
              initialMessages={chatMessages}
            />
          )}
          {currentView === "business-context" && <BusinessContextEditor />}
          {currentView === "mixpanel-event-schema" && <MixpanelEventSchemaView />}
          {currentView === "user-properties" && <UserProperties />}
          {currentView === "annotations" && <AnnotationsView />}
          {currentView === "add-context" && (
            <AddContextView onNavigateBack={handleNavigateBackFromAddContext} onContentAdded={handleContentAdded} />
          )}
          {currentView === "data-dictionary" && renderDataDictionaryMenu()}
          {currentView === "document-detail" && selectedDocument && (
            <DocumentDetailView
              document={selectedDocument}
              onBack={() => setCurrentView("business-context")}
              onEdit={async (id: string, newContent: string, newTitle: string) => {
                await updateDocument(connectionId, selectedDocument.index, newContent, newTitle)
                setContentRefreshTrigger((prev) => prev + 1)
                setSelectedDocument((doc: any) => ({ 
                  ...doc, 
                  content: newContent,
                  title: newTitle,
                  updatedAt: new Date().toISOString()
                }))
              }}
              onDelete={async (id: string) => {
                await deleteDocument(connectionId, selectedDocument.index)
                setContentRefreshTrigger((prev) => prev + 1)
                setCurrentView("business-context")
              }}
            />
          )}
          {currentView === "mixpanel-event-schema" && <MixpanelEventSchemaView />}
        </div>
      </SidebarInset>
    </>
  )
}
