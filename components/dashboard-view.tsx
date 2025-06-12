"use client"

import type React from "react"
import type { PageView } from "@/app/(chat)/page"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  TrendingUp,
  TrendingDown,
  AlertTriangle,
  CheckCircle,
  MessageSquare,
  MousePointerClick,
  Users,
  Brain,
  ArrowRight,
  Activity,
  Database,
  Zap,
  Clock,
  Target,
  BarChart3,
} from "lucide-react"
import { useConnection } from "@/lib/connection-context"

interface DashboardStats {
  totalEvents: number
  eventsChange: number
  totalMessages: number
  messagesChange: number
  activeUsers: number
  usersChange: number
  dataQuality: number
  qualityChange: number
}

interface TrendData {
  name: string
  value: number
  change: number
  trend: "up" | "down" | "stable"
}

interface Anomaly {
  id: string
  title: string
  description: string
  severity: "high" | "medium" | "low"
  timestamp: string
  category: string
}

interface RecommendedAction {
  id: string
  title: string
  description: string
  priority: "high" | "medium" | "low"
  estimatedImpact: string
  actionType: "investigate" | "optimize" | "fix" | "review"
}

interface QuickStat {
  label: string
  value: string
  change: number
  icon: React.ReactNode
  color: string
}

export function DashboardView({
  onNavigate,
}: {
  onNavigate: (view: PageView, data?: any) => void
}) {
  const [stats, setStats] = useState<DashboardStats>({
    totalEvents: 0,
    eventsChange: 0,
    totalMessages: 0,
    messagesChange: 0,
    activeUsers: 0,
    usersChange: 0,
    dataQuality: 0,
    qualityChange: 0,
  })

  const [trends, setTrends] = useState<TrendData[]>([])
  const [anomalies, setAnomalies] = useState<Anomaly[]>([])
  const [recommendations, setRecommendations] = useState<RecommendedAction[]>([])
  const [isLoading, setIsLoading] = useState(true)

  const { selectedCompany } = useConnection()

  useEffect(() => {
    // Simulate loading dashboard data
    const loadDashboardData = async () => {
      setIsLoading(true)

      // Simulate API delay
      await new Promise((resolve) => setTimeout(resolve, 1000))

      // Mock data - in real app, this would come from your APIs
      setStats({
        totalEvents: 45672,
        eventsChange: 12.5,
        totalMessages: 1234,
        messagesChange: -3.2,
        activeUsers: 8945,
        usersChange: 8.7,
        dataQuality: 94.2,
        qualityChange: 2.1,
      })

      setTrends([
        { name: "User Engagement", value: 87.3, change: 5.2, trend: "up" },
        { name: "Conversion Rate", value: 3.4, change: -0.8, trend: "down" },
        { name: "Session Duration", value: 245, change: 12.3, trend: "up" },
        { name: "Bounce Rate", value: 32.1, change: -4.5, trend: "down" },
      ])

      setAnomalies([
        {
          id: "1",
          title: "Unusual Traffic Spike",
          description: "Traffic increased by 340% in the last 2 hours from organic search",
          severity: "high",
          timestamp: "2 hours ago",
          category: "Traffic",
        },
        {
          id: "2",
          title: "Data Quality Drop",
          description: "Missing user_id field in 15% of recent events",
          severity: "medium",
          timestamp: "4 hours ago",
          category: "Data Quality",
        },
        {
          id: "3",
          title: "Low Conversion Rate",
          description: "Checkout conversion dropped 25% compared to last week",
          severity: "high",
          timestamp: "6 hours ago",
          category: "Business Metrics",
        },
      ])

      setRecommendations([
        {
          id: "1",
          title: "Investigate Traffic Anomaly",
          description: "Review the sudden traffic spike to understand the source and optimize for conversion",
          priority: "high",
          estimatedImpact: "High revenue impact",
          actionType: "investigate",
        },
        {
          id: "2",
          title: "Fix Data Collection Issues",
          description: "Address missing user_id fields to improve data quality and user tracking",
          priority: "medium",
          estimatedImpact: "Improved analytics accuracy",
          actionType: "fix",
        },
        {
          id: "3",
          title: "Optimize Checkout Flow",
          description: "Review checkout process to identify and resolve conversion barriers",
          priority: "high",
          estimatedImpact: "15-20% conversion increase",
          actionType: "optimize",
        },
      ])

      setIsLoading(false)
    }

    loadDashboardData()
  }, [selectedCompany])

  const quickStats: QuickStat[] = [
    {
      label: "Total Events",
      value: stats.totalEvents.toLocaleString(),
      change: stats.eventsChange,
      icon: <MousePointerClick className="h-4 w-4" />,
      color: "text-blue-600",
    },
    {
      label: "Chat Messages",
      value: stats.totalMessages.toLocaleString(),
      change: stats.messagesChange,
      icon: <MessageSquare className="h-4 w-4" />,
      color: "text-green-600",
    },
    {
      label: "Active Users",
      value: stats.activeUsers.toLocaleString(),
      change: stats.usersChange,
      icon: <Users className="h-4 w-4" />,
      color: "text-purple-600",
    },
    {
      label: "Data Quality",
      value: `${stats.dataQuality}%`,
      change: stats.qualityChange,
      icon: <Database className="h-4 w-4" />,
      color: "text-orange-600",
    },
  ]

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "high":
        return "bg-red-100 text-red-800 border-red-200"
      case "medium":
        return "bg-yellow-100 text-yellow-800 border-yellow-200"
      case "low":
        return "bg-blue-100 text-blue-800 border-blue-200"
      default:
        return "bg-gray-100 text-gray-800 border-gray-200"
    }
  }

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "high":
        return "bg-red-50 border-red-200"
      case "medium":
        return "bg-yellow-50 border-yellow-200"
      case "low":
        return "bg-green-50 border-green-200"
      default:
        return "bg-gray-50 border-gray-200"
    }
  }

  const getActionIcon = (actionType: string) => {
    switch (actionType) {
      case "investigate":
        return <Activity className="h-4 w-4" />
      case "optimize":
        return <Zap className="h-4 w-4" />
      case "fix":
        return <Target className="h-4 w-4" />
      case "review":
        return <CheckCircle className="h-4 w-4" />
      default:
        return <Activity className="h-4 w-4" />
    }
  }

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center h-full">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mb-4"></div>
        <p className="text-muted-foreground">Loading dashboard...</p>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-background p-6 overflow-y-auto">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground mt-1">
          Welcome back! Here's what's happening with {selectedCompany?.name || "your data"}.
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {quickStats.map((stat, index) => (
          <Card
            key={index}
            className="hover:shadow-md transition-shadow cursor-pointer"
            onClick={() => {
              if (stat.label === "Total Events") onNavigate("mixpanel-event-schema")
              if (stat.label === "Chat Messages") onNavigate("chat")
              if (stat.label === "Active Users") onNavigate("user-properties")
            }}
          >
            <CardContent className="p-4">
              <div className="flex items-center justify-between">
                <div className={stat.color}>{stat.icon}</div>
                <div
                  className={`text-sm font-medium ${
                    stat.change > 0 ? "text-green-600" : stat.change < 0 ? "text-red-600" : "text-gray-600"
                  }`}
                >
                  {stat.change > 0 ? "+" : ""}
                  {stat.change}%
                </div>
              </div>
              <div className="mt-2">
                <div className="text-2xl font-bold">{stat.value}</div>
                <div className="text-sm text-muted-foreground">{stat.label}</div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Key Trends */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <BarChart3 className="h-5 w-5" />
              Key Trends
            </CardTitle>
            <CardDescription>Performance metrics over the last 7 days</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {trends.map((trend, index) => (
                <div key={index} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                  <div>
                    <div className="font-medium">{trend.name}</div>
                    <div className="text-2xl font-bold">
                      {trend.value}
                      {trend.name.includes("Rate") ? "%" : trend.name.includes("Duration") ? "s" : ""}
                    </div>
                  </div>
                  <div
                    className={`flex items-center gap-1 ${
                      trend.trend === "up"
                        ? "text-green-600"
                        : trend.trend === "down"
                          ? "text-red-600"
                          : "text-gray-600"
                    }`}
                  >
                    {trend.trend === "up" ? (
                      <TrendingUp className="h-4 w-4" />
                    ) : trend.trend === "down" ? (
                      <TrendingDown className="h-4 w-4" />
                    ) : (
                      <Activity className="h-4 w-4" />
                    )}
                    <span className="text-sm font-medium">
                      {trend.change > 0 ? "+" : ""}
                      {trend.change}%
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Anomalies */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5" />
              Recent Anomalies
            </CardTitle>
            <CardDescription>Unusual patterns detected in your data</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {anomalies.map((anomaly) => (
                <div
                  key={anomaly.id}
                  className="p-3 rounded-lg border bg-card hover:bg-muted/50 transition-colors cursor-pointer"
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="font-medium">{anomaly.title}</div>
                    <Badge className={getSeverityColor(anomaly.severity)}>{anomaly.severity}</Badge>
                  </div>
                  <div className="text-sm text-muted-foreground mb-2">{anomaly.description}</div>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{anomaly.category}</span>
                    <span className="flex items-center gap-1">
                      <Clock className="h-3 w-3" />
                      {anomaly.timestamp}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recommended Actions */}
      <Card className="mb-6">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Brain className="h-5 w-5" />
            Recommended Actions
          </CardTitle>
          <CardDescription>AI-powered suggestions to improve your data and business metrics</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {recommendations.map((action) => (
              <div
                key={action.id}
                className={`p-4 rounded-lg border-2 ${getPriorityColor(action.priority)} hover:shadow-md transition-shadow cursor-pointer`}
              >
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    {getActionIcon(action.actionType)}
                    <Badge variant="outline" className="text-xs">
                      {action.priority} priority
                    </Badge>
                  </div>
                </div>
                <div className="font-medium mb-2">{action.title}</div>
                <div className="text-sm text-muted-foreground mb-3">{action.description}</div>
                <div className="text-xs font-medium text-green-600 mb-3">{action.estimatedImpact}</div>
                <Button size="sm" variant="outline" className="w-full">
                  Take Action
                  <ArrowRight className="h-3 w-3 ml-1" />
                </Button>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Access */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Access</CardTitle>
          <CardDescription>Jump to frequently used features</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <Button variant="outline" className="h-20 flex flex-col gap-2" onClick={() => onNavigate("chat")}>
              <MessageSquare className="h-6 w-6" />
              <span className="text-sm">Chat</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col gap-2" onClick={() => onNavigate("agents")}>
              <Brain className="h-6 w-6" />
              <span className="text-sm">AI Agents</span>
            </Button>
            <Button variant="outline" className="h-20 flex flex-col gap-2" onClick={() => onNavigate("mixpanel-event-schema")}>
              <MousePointerClick className="h-6 w-6" />
              <span className="text-sm">Events</span>
            </Button>
            <Button
              variant="outline"
              className="h-20 flex flex-col gap-2"
              onClick={() => onNavigate("business-context")}
            >
              <Database className="h-6 w-6" />
              <span className="text-sm">Knowledge</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
