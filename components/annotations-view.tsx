"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Label } from "@/components/ui/label"
import { PlusIcon, PencilEditIcon, TrashIcon, CheckCirclFillIcon, CrossIcon } from "./icons"
import { toast } from "sonner"

// Define types for annotations
interface Annotation {
  id: string
  date: string
  description: string
  user: string
}

export function AnnotationsView() {
  const [annotations, setAnnotations] = useState<Annotation[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [isAddingNew, setIsAddingNew] = useState(false)
  const [editingId, setEditingId] = useState<string | null>(null)
  const [searchQuery, setSearchQuery] = useState("")

  // Form state
  const [formData, setFormData] = useState({
    date: new Date().toISOString().split("T")[0], // Today's date
    description: "",
    user: "Suraj Kaya", // Default user
  })

  // Fetch annotations from backend
  const fetchAnnotations = () => {
    setIsLoading(true)
    fetch(`/api/annotations?`)
      .then((res) => res.json())
      .then(setAnnotations)
      .catch((err) => {
        console.error("Failed to fetch annotations:", err)
        setAnnotations([])
      })
      .finally(() => setIsLoading(false))
  }

  useEffect(() => {
    fetchAnnotations()
  }, [])

  // Filter and sort annotations based on search query
  const filteredAnnotations = annotations
    .filter(
      (annotation) =>
        annotation.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
        annotation.user.toLowerCase().includes(searchQuery.toLowerCase()),
    )
    .sort((a, b) => {
      // Sort by date descending (newest first)
      const dateA = new Date(a.date).getTime()
      const dateB = new Date(b.date).getTime()
      return dateB - dateA
    })

  const handleAdd = async () => {
    console.log("handleAdd called", formData)
    if (!formData.description.trim()) {
      toast.error("Description is required")
      return
    }
    setIsLoading(true)
    try {
      // Format date as 'YYYY-MM-DD HH:mm:ss'
      const dateObj = new Date(formData.date)
      const pad = (n: number) => n.toString().padStart(2, "0")
      const formattedDate = `${dateObj.getFullYear()}-${pad(dateObj.getMonth() + 1)}-${pad(dateObj.getDate())} ${pad(dateObj.getHours())}:${pad(dateObj.getMinutes())}:${pad(dateObj.getSeconds())}`
      const payload = {
        description: formData.description.trim(),
        date: formattedDate,
      }
      console.log("POST /api/annotations payload", payload)
      const res = await fetch("/api/annotations", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      })
      if (!res.ok) throw new Error("Failed to create annotation")
      toast.success("Annotation added successfully")
      setFormData({
        date: new Date().toISOString().split("T")[0],
        description: "",
        user: "Suraj Kaya",
      })
      setIsAddingNew(false)
      fetchAnnotations()
    } catch (err) {
      toast.error("Failed to create annotation")
    } finally {
      setIsLoading(false)
    }
  }

  const handleEdit = (annotation: Annotation) => {
    // Try to extract just the date part (YYYY-MM-DD) from annotation.date
    let dateValue = ""
    if (annotation.date) {
      // Handles both "YYYY-MM-DD" and "YYYY-MM-DD HH:mm:ss"
      dateValue = annotation.date.split("T")[0]
    }
    setEditingId(annotation.id)
    setFormData({
      date: dateValue,
      description: annotation.description,
      user: annotation.user,
    })
  }

  const handleSaveEdit = async () => {
    if (!formData.description.trim()) {
      toast.error("Description is required")
      return
    }
    setIsLoading(true)
    try {
      const res = await fetch(`/api/annotations/${editingId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ description: formData.description.trim() }),
      })
      if (!res.ok) throw new Error("Failed to update annotation")
      toast.success("Annotation updated successfully")
      setEditingId(null)
      setFormData({
        date: new Date().toISOString().split("T")[0],
        description: "",
        user: "Suraj Kaya",
      })
      fetchAnnotations()
    } catch (err) {
      toast.error("Failed to update annotation")
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (id: string) => {
    if (!confirm("Are you sure you want to delete this annotation?")) return
    setIsLoading(true)
    try {
      const res = await fetch(`/api/annotations/${id}`, { method: "DELETE" })
      if (!res.ok) throw new Error("Failed to delete annotation")
      toast.success("Annotation deleted successfully")
      fetchAnnotations()
    } catch (err) {
      toast.error("Failed to delete annotation")
    } finally {
      setIsLoading(false)
    }
  }

  const handleCancel = () => {
    setIsAddingNew(false)
    setEditingId(null)
    setFormData({
      date: new Date().toISOString().split("T")[0],
      description: "",
      user: "Suraj Kaya",
    })
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    })
  }

  return (
    <div className="flex flex-col h-full bg-background p-6">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <h1 className="text-2xl font-bold">Annotations</h1>
          <Button
            onClick={() => setIsAddingNew(true)}
            disabled={isAddingNew || editingId !== null}
            size="lg"
            className="bg-primary hover:bg-primary/90"
          >
            <PlusIcon size={16} />
            Add New Annotation
          </Button>
        </div>

        {/* Search */}
        <div className="mb-4">
          <Input
            placeholder="Search annotations..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="max-w-md"
          />
        </div>

        {/* Add/Edit Form */}
        {(isAddingNew || editingId) && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle>{editingId ? "Edit Annotation" : "Add New Annotation"}</CardTitle>
            </CardHeader>
            <CardContent>
              {isAddingNew ? (
                // Add New Form - only date and description
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="date">Date</Label>
                    <Input
                      id="date"
                      type="date"
                      value={formData.date}
                      onChange={(e) => setFormData({ ...formData, date: e.target.value })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      placeholder="Enter annotation description..."
                      className="min-h-[100px]"
                    />
                  </div>
                </div>
              ) : (
                // Edit Form - show date and user as read-only, only description editable
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="date-readonly">Date</Label>
                      <Input
                        id="date-readonly"
                        type="date"
                        value={formData.date.split(" ")[0]} // Handle datetime format from backend
                        disabled
                        className="bg-muted cursor-not-allowed"
                      />
                    </div>
                    <div>
                      <Label htmlFor="user-readonly">User</Label>
                      <Input
                        id="user-readonly"
                        value={formData.user}
                        disabled
                        className="bg-muted cursor-not-allowed"
                      />
                    </div>
                  </div>
                  <div>
                    <Label htmlFor="description">Description</Label>
                    <Textarea
                      id="description"
                      value={formData.description}
                      onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                      placeholder="Enter annotation description..."
                      className="min-h-[100px]"
                    />
                  </div>
                </div>
              )}

              <div className="flex gap-2 mt-4">
                <Button onClick={editingId ? handleSaveEdit : handleAdd} disabled={isLoading}>
                  <CheckCirclFillIcon size={16} />
                  {editingId ? "Save Changes" : "Add Annotation"}
                </Button>
                <Button variant="outline" onClick={handleCancel}>
                  <CrossIcon size={16} />
                  Cancel
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Annotations Table */}
      <div className="flex-1 overflow-auto">
        <div className="border rounded-lg">
          <table className="w-full border-collapse">
            <thead>
              <tr className="border-b bg-muted/50">
                <th className="py-3 px-4 text-left font-medium text-muted-foreground">DATE</th>
                <th className="py-3 px-4 text-left font-medium text-muted-foreground">DESCRIPTION</th>
                <th className="py-3 px-4 text-left font-medium text-muted-foreground">USER</th>
                <th className="py-3 px-4 text-left font-medium text-muted-foreground">ACTIONS</th>
              </tr>
            </thead>
            <tbody>
              {isLoading ? (
                <tr>
                  <td colSpan={4} className="py-8 px-4 text-center text-muted-foreground">
                    <div className="flex justify-center items-center py-8">
                      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900"></div>
                    </div>
                  </td>
                </tr>
              ) : filteredAnnotations.length === 0 ? (
                <tr>
                  <td colSpan={4} className="py-8 px-4 text-center text-muted-foreground">
                    {searchQuery
                      ? "No annotations found matching your search."
                      : "No annotations yet. Add your first annotation above."}
                  </td>
                </tr>
              ) : (
                filteredAnnotations.map((annotation) => (
                  <tr key={annotation.id} className="border-b hover:bg-muted/25">
                    <td className="py-4 px-4 text-sm font-medium">{formatDate(annotation.date)}</td>
                    <td className="py-4 px-4 text-sm max-w-md">
                      <p className="line-clamp-2">{annotation.description}</p>
                    </td>
                    <td className="py-4 px-4 text-sm text-muted-foreground">{annotation.user}</td>
                    <td className="py-4 px-4">
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleEdit(annotation)}
                          disabled={isAddingNew || editingId !== null || isLoading}
                        >
                          <PencilEditIcon size={14} />
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => handleDelete(annotation.id)}
                          disabled={isAddingNew || editingId !== null || isLoading}
                          className="text-destructive hover:text-destructive"
                        >
                          <TrashIcon size={14} />
                        </Button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
