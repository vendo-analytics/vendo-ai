"use client"

import React, { createContext, useContext, useState, useEffect } from 'react'
interface Company {
  id: string
  name: string
}
// Sample company data - same as in knowledge-sidebar
export const companies: Company[] = [
  { id: "gb1uauyn0Khjcs4Fgxh8", name: "Piri Red" },
  { id: "Gb6MUQ59IluZqapubOMs", name: "Raiz Invest" },
  { id: "qJqU5UoXLBEMW8critIo", name: "Tattooing101" },
]
interface ConnectionContextType {
  selectedConnectionId: string
  setSelectedConnectionId: (id: string) => void
  selectedCompany: Company | undefined
  companies: Company[]
}
const ConnectionContext = createContext<ConnectionContextType | undefined>(undefined)
export function ConnectionProvider({ children }: { children: React.ReactNode }) {
  // Default to the first company or "001" for backward compatibility
  const [selectedConnectionId, setSelectedConnectionId] = useState<string>(() => {
    // Try to get from localStorage first
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('selectedConnectionId')
      if (saved && companies.find(c => c.id === saved)) {
        return saved
      }
    }
    // Fallback to first company or "001"
    return companies[0]?.id || "001"
  })
  // Save to localStorage whenever selection changes
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('selectedConnectionId', selectedConnectionId)
    }
  }, [selectedConnectionId])
  const selectedCompany = companies.find(c => c.id === selectedConnectionId)
  const value: ConnectionContextType = {
    selectedConnectionId,
    setSelectedConnectionId,
    selectedCompany,
    companies,
  }
  return (
    <ConnectionContext.Provider value={value}>
      {children}
    </ConnectionContext.Provider>
  )
}
export function useConnection() {
  const context = useContext(ConnectionContext)
  if (context === undefined) {
    throw new Error('useConnection must be used within a ConnectionProvider')
  }
  return context
}
// Helper hook to get just the connection ID (for backward compatibility)
export function useConnectionId(): string {
  const { selectedConnectionId } = useConnection()
  return selectedConnectionId
}