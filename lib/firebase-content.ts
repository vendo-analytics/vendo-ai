export const fetchFirebaseContent = async (connectionId = "001") => {
  try {
    const response = await fetch(`/api/general-context?connection_id=${connectionId}`)
    if (!response.ok) throw new Error("Failed to fetch")
    const data = await response.json()

    console.log("Raw API response:", data) // Debug log

    // Handle different response formats
    let contentStrings: string[] = []

    if (Array.isArray(data)) {
      contentStrings = data.filter((item) => typeof item === "string")
    } else if (data && typeof data === "object" && data.error) {
      console.error("API returned error:", data.error)
      return []
    } else {
      console.warn("Unexpected API response format:", data)
      return []
    }

    // Transform content strings to match ContentItem interface
    return contentStrings.map((content: string, index: number) => ({
      id: `${connectionId}_${index}`,
      content: content,
      embedding: [],
      index: index,
    }))
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
      content,
      embedding: [],
      index: Date.now(),
    }
  } catch (error) {
    console.error("Error adding Firebase content:", error)
    throw error
  }
}

export const updateFirebaseContent = async (
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

export const deleteFirebaseContent = async (connectionId: string, index: number, messageType = "general_context") => {
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

export interface ContentItem {
  id: string
  content: string
  embedding: number[]
  index: number
} 