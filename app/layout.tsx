import type React from "react"
import type { Metadata } from "next"
import { Inter } from 'next/font/google'
import "./globals.css"
import { Toaster } from "sonner"
import { SidebarProvider } from "@/components/ui/sidebar"
import { ConnectionProvider } from "@/lib/connection-context"

const inter = Inter({ subsets: ["latin"] })

export const metadata: Metadata = {
  title: "VendoAI",
  description: "Chat interface with integrated knowledge base sidebar",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <ConnectionProvider>
          <SidebarProvider>
            {children}
            <Toaster position="top-center" />
          </SidebarProvider>
        </ConnectionProvider>
      </body>
    </html>
  )
}