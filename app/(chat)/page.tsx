"use client"

import { useState } from "react"
import { Chat } from "@/components/chat"
import { BusinessContextEditor } from "@/components/business-context-editor"
import { KnowledgeSidebar } from "@/components/knowledge-sidebar"
import { SidebarInset } from "@/components/ui/sidebar"
import { Navbar } from "@/components/navbar"
import { Separator } from "@/components/ui/separator"
import { Button } from "@/components/ui/button"
import { MenuIcon } from "@/components/icons"
import { useSidebar } from "@/components/ui/sidebar"
import { EventsView } from "@/components/events-view"
import { EventDetails } from "@/components/event-details"
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
    "chat" | "business-context" | "events" | "event-details" | "annotations"
  >("chat")
  const [selectedEvent, setSelectedEvent] = useState<any>(null)

  const getPageTitle = () => {
    switch (currentView) {
      case "business-context":
        return "Business Context"
      case "events":
        return "Events"
      case "event-details":
        return "Event Details"
      case "annotations":
        return "Annotations"
      case "chat":
      default:
        return "AI Chat with Knowledge Base"
    }
  }

  const handleNavigate = (view: "chat" | "business-context" | "events" | "event-details" | "annotations") => {
    setCurrentView(view)
    if (view !== "event-details") {
      setSelectedEvent(null)
    }
  }

  const handleSelectEvent = (event: any) => {
    setSelectedEvent(event)
    setCurrentView("event-details")
  }

  return (
    <>
      <KnowledgeSidebar onNavigate={handleNavigate} currentView={currentView} selectedEventId={selectedEvent?.id} />
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
          {currentView === "event-details" && selectedEvent && <EventDetails event={selectedEvent} />}
          {currentView === "annotations" && <AnnotationsView />}
        </div>
      </SidebarInset>
    </>
  )
}
