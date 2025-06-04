"use client"

import { useState, useCallback } from "react"
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

function CustomSidebarTrigger() {
  const { toggleSidebar } = useSidebar()

  return (
    <Button variant="ghost" size="icon" onClick={toggleSidebar} className="h-8 w-8">
      <MenuIcon size={16} />
      <span className="sr-only">Toggle Sidebar</span>
    </Button>
  )
}

export default function Page() {
  const [currentView, setCurrentView] = useState<
    "chat" | "business-context" | "events" | "event-properties" | "user-properties" | "annotations" | "add-context"
  >("chat")
  const [selectedEvent, setSelectedEvent] = useState<any>(null)
  const [contentRefreshTrigger, setContentRefreshTrigger] = useState(0)

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
      case "chat":
      default:
        return "AI Chat with Knowledge Base"
    }
  }

  const handleNavigate = (
    view:
      | "chat"
      | "business-context"
      | "events"
      | "event-properties"
      | "user-properties"
      | "annotations"
      | "add-context",
  ) => {
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

  return (
    <>
      <KnowledgeSidebar
        onNavigate={handleNavigate}
        currentView={currentView}
        selectedEventId={selectedEvent?.id}
        onContentRefresh={contentRefreshTrigger}
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
          {currentView === "chat" && <Chat />}
          {currentView === "business-context" && <BusinessContextEditor />}
          {currentView === "events" && <EventsView onSelectEvent={handleSelectEvent} />}
          {currentView === "event-properties" && selectedEvent && <EventProperties event={selectedEvent} />}
          {currentView === "user-properties" && <UserProperties />}
          {currentView === "annotations" && <AnnotationsView />}
          {currentView === "add-context" && (
            <AddContextView onNavigateBack={handleNavigateBackFromAddContext} onContentAdded={handleContentAdded} />
          )}
        </div>
      </SidebarInset>
    </>
  )
}
