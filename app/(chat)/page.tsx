"use client"

import { useState, useCallback } from "react"
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

type PageView =
  | "chat"
  | "business-context"
  | "events"
  | "event-properties"
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
  
  // Use the connection context
  const connectionId = useConnectionId()

  const getPageTitle = () => {
    switch (currentView) {
      case "business-context":
        return "Business Context"
      case "events":
        return "Events"
      case "event-properties":
        return "Event Properties"
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
      case "chat":
      default:
        return "Vendo AI Demo"
    }
  }

  const handleNavigate = (view: PageView) => {
    setCurrentView(view)
    if (view !== "event-properties") {
      setSelectedEvent(null)
    }
  }

  const handleSelectEvent = (event: any) => {
    setSelectedEvent(event)
    setCurrentView("event-properties")
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

  // New: Data Dictionary selection view
  const renderDataDictionaryMenu = () => (
    <div className="flex flex-col gap-4 p-8">
      <h2 className="text-lg font-semibold mb-2">Data Dictionary</h2>
      <Button variant="outline" onClick={() => setCurrentView("event-properties")}>Event Properties</Button>
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
          <div className="ml-auto hidden md:block">
            <Navbar />
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
          {currentView === "events" && <EventsView onSelectEvent={handleSelectEvent} />}
          {currentView === "event-properties" && selectedEvent && <EventProperties event={selectedEvent} />}
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
        </div>
      </SidebarInset>
    </>
  )
}
