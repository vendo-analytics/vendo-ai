"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { CheckCirclFillIcon, CrossIcon, PlusIcon } from "./icons"
import { toast } from "sonner"
import { addFirebaseContent } from "@/lib/firebase-content"
import { useConnectionId } from "@/lib/connection-context"

interface AddContextViewProps {
  onNavigateBack: () => void
  onContentAdded: () => void
}

export function AddContextView({ onNavigateBack, onContentAdded }: AddContextViewProps) {
  const [newTitle, setNewTitle] = useState("")
  const [newContent, setNewContent] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [titleError, setTitleError] = useState("")

  // Get the selected connection ID from global context
  const connectionId = useConnectionId()

  // TODO: Make author dynamic/user-based in the future
  const author = "system user"

  const handleAddContent = async () => {
    if (!newTitle.trim()) {
      setTitleError("Title is required")
      return
    }
    setTitleError("")
    if (!newContent.trim()) {
      toast.error("Please enter some content")
      return
    }

    setIsLoading(true)
    try {
      await addFirebaseContent(connectionId, newTitle.trim(), newContent.trim(), author)
      toast.success("Content added successfully")
      setNewTitle("")
      setNewContent("")
      onContentAdded()
      onNavigateBack()
    } catch (error) {
      console.error("Failed to add content:", error)
      toast.error("Failed to add content")
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    if ((newTitle.trim() || newContent.trim()) && !confirm("Are you sure you want to cancel? Your changes will be lost.")) {
      return
    }
    setNewTitle("")
    setNewContent("")
    setTitleError("")
    onNavigateBack()
  }

  return (
    <div className="flex flex-col h-full bg-background p-6">
      <div className="max-w-4xl mx-auto w-full">
        <div className="mb-6">
          <h1 className="text-2xl font-bold mb-2">Add New Context</h1>
          <p className="text-muted-foreground">
            Add new context information that will be available to the AI assistant during conversations.
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <PlusIcon size={20} />
              New Context Item
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="space-y-2">
              <Label htmlFor="title" className="text-base font-medium">
                Title <span className="text-destructive">*</span>
              </Label>
              <input
                id="title"
                type="text"
                className="w-full border rounded px-3 py-2 text-base"
                placeholder="Enter a title for this document"
                value={newTitle}
                onChange={e => setNewTitle(e.target.value)}
                disabled={isLoading}
                required
              />
              {titleError && <p className="text-sm text-destructive">{titleError}</p>}
            </div>
            <div className="space-y-2">
              <Label htmlFor="content" className="text-base font-medium">
                Content
              </Label>
              <Textarea
                id="content"
                placeholder="Enter the context information here. This could be business rules, procedures, knowledge, or any information you want the AI to have access to..."
                value={newContent}
                onChange={(e) => setNewContent(e.target.value)}
                className="min-h-[200px] resize-y"
                disabled={isLoading}
              />
              <p className="text-sm text-muted-foreground">
                Tip: Be specific and clear. The AI will use this information to provide better responses.
              </p>
            </div>

            <div className="flex gap-3 pt-4">
              <Button onClick={handleAddContent} disabled={isLoading || !newTitle.trim() || !newContent.trim()} className="min-w-[120px]">
                <CheckCirclFillIcon size={16} />
                {isLoading ? "Adding..." : "Add Content"}
              </Button>
              <Button variant="outline" onClick={handleCancel} disabled={isLoading}>
                <CrossIcon size={16} />
                Cancel
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Tips Section */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle className="text-lg">Tips for Adding Context</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li className="flex items-start gap-2">
                <span className="text-primary">•</span>
                <span>Be specific and detailed - the more context you provide, the better the AI can assist you</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary">•</span>
                <span>Include business rules, procedures, and domain-specific knowledge</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary">•</span>
                <span>Use clear, concise language that the AI can easily understand</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-primary">•</span>
                <span>Consider adding examples or use cases to make the context more actionable</span>
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
