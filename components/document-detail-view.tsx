import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { ArrowLeft, Pencil, Trash, Check, X } from "lucide-react"
import { Textarea } from "@/components/ui/textarea"
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

interface DocumentDetailViewProps {
  document: { id: string; title: string; content: string; author: string; createdAt: string; updatedAt: string }
  onBack: () => void
  onEdit?: (id: string, newContent: string, newTitle: string) => Promise<void> | void
  onDelete?: (id: string) => Promise<void> | void
}

export function DocumentDetailView({ document, onBack, onEdit, onDelete }: DocumentDetailViewProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [editTitle, setEditTitle] = useState(document.title)
  const [editContent, setEditContent] = useState(document.content)
  const [isLoading, setIsLoading] = useState(false)

  // Sync edit state with document when document changes
  useEffect(() => {
    setEditTitle(document.title)
    setEditContent(document.content)
  }, [document.id, document.title, document.content])

  const handleSave = async () => {
    if (!onEdit) return
    setIsLoading(true)
    await onEdit(document.id, editContent, editTitle)
    setIsLoading(false)
    setIsEditing(false)
  }

  const handleDelete = async () => {
    if (!onDelete) return
    if (!confirm("Are you sure you want to delete this document?")) return
    setIsLoading(true)
    await onDelete(document.id)
    setIsLoading(false)
    onBack()
  }

  return (
    <div className="flex flex-col h-full bg-background p-6">
      <div className="max-w-4xl mx-auto w-full">
        <Button variant="ghost" onClick={onBack} className="mb-4 flex items-center gap-2">
          <ArrowLeft size={16} />
          Back
        </Button>
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            {isEditing ? (
              <input
                className="text-2xl font-semibold leading-none tracking-tight border-none outline-none bg-transparent flex-1 mr-4"
                value={editTitle}
                onChange={e => setEditTitle(e.target.value)}
                disabled={isLoading}
                placeholder="Enter title..."
                autoFocus
              />
            ) : (
              <CardTitle>{document.title || 'Untitled Document'}</CardTitle>
            )}
            <div className="flex gap-1">
              {!isEditing && (
                <>
                  <Button size="sm" variant="outline" onClick={() => setIsEditing(true)} disabled={isLoading}>
                    <Pencil size={16} /> Edit
                  </Button>
                  <Button size="sm" variant="destructive" onClick={handleDelete} disabled={isLoading}>
                    <Trash size={16} /> Delete
                  </Button>
                </>
              )}
            </div>
          </CardHeader>
          <CardContent>
            {/* Meta info */}
            <div className="mb-4 text-sm text-muted-foreground space-y-1">
              <div><span className="font-semibold">Author:</span> <span className="text-foreground">{document.author || 'Unknown'}</span></div>
              <div><span className="font-semibold">Created At:</span> <span className="text-foreground">{document.createdAt ? new Date(document.createdAt).toLocaleString() : 'Unknown'}</span></div>
              <div><span className="font-semibold">Updated At:</span> <span className="text-foreground">{document.updatedAt ? new Date(document.updatedAt).toLocaleString() : 'Unknown'}</span></div>
            </div>
            {isEditing ? (
              <div className="space-y-4">
                <Textarea
                  value={editContent}
                  onChange={e => setEditContent(e.target.value)}
                  className="min-h-[200px]"
                  disabled={isLoading}
                />
                <div className="flex gap-2">
                  <Button size="sm" onClick={handleSave} disabled={isLoading || !editContent.trim() || !editTitle.trim()}>
                    <Check size={16} /> Save
                  </Button>
                  <Button size="sm" variant="outline" onClick={() => { setIsEditing(false); setEditContent(document.content); setEditTitle(document.title) }} disabled={isLoading}>
                    <X size={16} /> Cancel
                  </Button>
                </div>
              </div>
            ) : (
              <div className="prose prose-neutral dark:prose-invert max-w-none">
                <ReactMarkdown 
                  remarkPlugins={[remarkGfm]}
                  components={{
                    h1: ({ node, ...props }) => <h1 className="text-2xl font-bold mb-4 mt-6" {...props} />,
                    h2: ({ node, ...props }) => <h2 className="text-xl font-semibold mb-3 mt-5" {...props} />,
                    h3: ({ node, ...props }) => <h3 className="text-lg font-medium mb-2 mt-4" {...props} />,
                    p: ({ node, ...props }) => <p className="mb-3 leading-relaxed" {...props} />,
                    ul: ({ node, ...props }) => <ul className="list-disc list-inside mb-3 space-y-1" {...props} />,
                    ol: ({ node, ...props }) => <ol className="list-decimal list-inside mb-3 space-y-1" {...props} />,
                    li: ({ node, ...props }) => <li className="mb-1" {...props} />,
                    blockquote: ({ node, ...props }) => <blockquote className="border-l-4 border-muted pl-4 italic mb-3" {...props} />,
                    code: ({ node, inline, ...props }: any) => 
                      inline ? (
                        <code className="bg-muted px-1 py-0.5 rounded text-sm font-mono" {...props} />
                      ) : (
                        <code className="block bg-muted p-3 rounded-md font-mono text-sm overflow-x-auto mb-3" {...props} />
                      ),
                    pre: ({ node, ...props }) => <pre className="bg-muted p-3 rounded-md overflow-x-auto mb-3" {...props} />,
                    a: ({ node, ...props }) => <a className="text-blue-600 hover:text-blue-800 underline" {...props} />,
                    strong: ({ node, ...props }) => <strong className="font-semibold" {...props} />,
                    em: ({ node, ...props }) => <em className="italic" {...props} />,
                  }}
                >
                  {document.content}
                </ReactMarkdown>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  )
} 