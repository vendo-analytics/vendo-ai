"use client"

import React, { createContext, useContext, useState, useEffect } from 'react'

interface Company {
  id: string
  name: string
}

interface ConnectionContextType {
  selectedConnectionId: string
  setSelectedConnectionId: (id: string) => void
  selectedCompany: Company | undefined
  companies: Company[]
  isLoading: boolean
  error: string | null
}

const ConnectionContext = createContext<ConnectionContextType | undefined>(undefined)

export function ConnectionProvider({ children }: { children: React.ReactNode }) {
  const [companies, setCompanies] = useState<Company[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedConnectionId, setSelectedConnectionId] = useState<string>("gb1uauyn0Khjcs4Fgxh8")

  // Fetch companies from API
  useEffect(() => {
    let ignore = false
    async function fetchCompanies() {
      setIsLoading(true)
      setError(null)
      try {
        const res = await fetch("/api/companies")
        if (!res.ok) throw new Error("Failed to fetch companies")
        const data: Company[] = await res.json()
        if (!ignore) {
          setCompanies(data)
          // Set default selectedConnectionId
          let initialId = "gb1uauyn0Khjcs4Fgxh8"
          if (typeof window !== "undefined") {
            const saved = localStorage.getItem("selectedConnectionId")
            if (saved && data.find(c => c.id === saved)) {
              initialId = saved
            } else if (data[0]?.id) {
              initialId = data[0].id
            }
          } else if (data[0]?.id) {
            initialId = data[0].id
          }
          setSelectedConnectionId(initialId)
        }
      } catch (e: any) {
        if (!ignore) setError(e.message || "Unknown error")
      } finally {
        if (!ignore) setIsLoading(false)
      }
    }
    fetchCompanies()
    return () => { ignore = true }
  }, [])

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
    isLoading,
    error,
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

export function useConnectionId(): string {
  const { selectedConnectionId } = useConnection()
  return selectedConnectionId
}