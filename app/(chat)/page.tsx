import { Chat } from "@/components/chat"
import { KnowledgeSidebar } from "@/components/knowledge-sidebar"
import { SidebarInset, SidebarTrigger } from "@/components/ui/sidebar"
import { Navbar } from "@/components/navbar"

export default function Page() {
  return (
    <>
      <KnowledgeSidebar />
      <SidebarInset>
        <div className="flex flex-col h-full">
          {/* Top Navigation Bar */}
          <div className="flex items-center justify-between px-4 py-2 border-b bg-background">
            <div className="flex items-center gap-2">
              <SidebarTrigger />
              <h1 className="text-xl font-bold">Vendo AI Chat</h1>
            </div>
            <div className="hidden md:block">
              <Navbar />
            </div>
          </div>

          {/* Chat Component */}
          <div className="flex-1 overflow-hidden">
            <Chat />
          </div>
        </div>
      </SidebarInset>
    </>
  )
}
