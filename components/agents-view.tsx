"use client"

import type React from "react"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import {
  Search,
  TrendingUp,
  Users,
  BarChart3,
  Target,
  Brain,
  AlertTriangle,
  CheckCircle2,
  Clock,
  ArrowRight,
  LineChart,
  PieChart,
  Activity,
  Filter,
  DollarSign,
  UserCheck,
  Shuffle,
} from "lucide-react"

interface Agent {
  id: string
  name: string
  description: string
  category: "Time-Series" | "Customer Analytics" | "Marketing" | "Experimentation" | "Real-Time" | "Predictive"
  status: "active" | "inactive" | "beta"
  icon: React.ReactNode
  capabilities: string[]
  lastUsed?: string
  usageCount?: number
  skillMapping: string[]
}

const mockAgents: Agent[] = [
  {
    id: "time-series-agent",
    name: "Time-Series Forecasting Agent",
    description:
      "Track metric evolution, spot trends, seasonality and shocks. Performs period-over-period analysis and forecasts future performance using Prophet and ARIMA models.",
    category: "Time-Series",
    status: "active",
    icon: <LineChart size={24} />,
    capabilities: ["SQL window functions", "Prophet forecasting", "Seasonality decomposition", "Anomaly detection"],
    lastUsed: "1 hour ago",
    usageCount: 234,
    skillMapping: ["Time-Series Analysis", "Anomaly Detection & Real-Time Monitoring"],
  },
  {
    id: "cohort-analysis-agent",
    name: "Cohort Analysis Agent",
    description:
      "Group users by shared start actions and measure retention or value over time. Analyzes user lifecycle patterns and cohort LTV progression.",
    category: "Customer Analytics",
    status: "active",
    icon: <Users size={24} />,
    capabilities: ["Cohort bucketing", "Retention matrices", "Survival analysis", "Churn prediction"],
    lastUsed: "2 hours ago",
    usageCount: 156,
    skillMapping: ["Cohort Analysis", "Customer Lifetime Value (LTV) Modeling"],
  },
  {
    id: "funnel-optimization-agent",
    name: "Funnel Optimization Agent",
    description:
      "Track step-by-step conversion rates through critical user journeys. Identifies drop-off points and optimization opportunities in conversion funnels.",
    category: "Customer Analytics",
    status: "active",
    icon: <Filter size={24} />,
    capabilities: [
      "Event hierarchy modeling",
      "Funnel visualization",
      "Statistical significance tests",
      "Journey mapping",
    ],
    lastUsed: "3 hours ago",
    usageCount: 189,
    skillMapping: ["Funnel Analysis & Conversion Drop-Off", "Path & Journey Analysis"],
  },
  {
    id: "segmentation-agent",
    name: "Customer Segmentation Agent",
    description:
      "Group users by shared behavior or attributes using ML clustering. Creates actionable segments for personalized messaging and targeted campaigns.",
    category: "Customer Analytics",
    status: "active",
    icon: <PieChart size={24} />,
    capabilities: ["RFM analysis", "K-means clustering", "Feature engineering", "Segment profiling"],
    lastUsed: "4 hours ago",
    usageCount: 145,
    skillMapping: ["Segmentation & Clustering", "Lookup-Table Enrichment & Dimensional Modeling"],
  },
  {
    id: "attribution-agent",
    name: "Attribution & Incrementality Agent",
    description:
      "Allocate credit to marketing touches and estimate incremental lift. Uses multi-touch attribution models and geo-matched market tests.",
    category: "Marketing",
    status: "active",
    icon: <Target size={24} />,
    capabilities: ["Multi-touch attribution", "Markov chains", "Incrementality testing", "Holdout analysis"],
    lastUsed: "5 hours ago",
    usageCount: 98,
    skillMapping: ["Attribution & Incrementality", "Experimentation & Causal Inference"],
  },
  {
    id: "ltv-modeling-agent",
    name: "LTV Prediction Agent",
    description:
      "Predict customer lifetime value using probabilistic models. Forecasts net present value to optimize acquisition spending and retention strategies.",
    category: "Predictive",
    status: "active",
    icon: <DollarSign size={24} />,
    capabilities: ["BG/NBD modeling", "Survival analysis", "DCF calculations", "Churn probability"],
    lastUsed: "6 hours ago",
    usageCount: 167,
    skillMapping: ["Customer Lifetime Value (LTV) Modeling", "Predictive Modeling & Propensity Scoring"],
  },
  {
    id: "mmm-agent",
    name: "Marketing Mix Modeling Agent",
    description:
      "Top-down econometric model linking spend across channels to sales. Accounts for adstock, saturation, and synergy effects to optimize budget allocation.",
    category: "Marketing",
    status: "beta",
    icon: <BarChart3 size={24} />,
    capabilities: ["Adstock modeling", "Saturation curves", "Budget optimization", "Scenario planning"],
    lastUsed: "1 day ago",
    usageCount: 67,
    skillMapping: ["Marketing-Mix Modeling (MMM)", "Calculated / Derived Metrics"],
  },
  {
    id: "propensity-agent",
    name: "Propensity Scoring Agent",
    description:
      "Use historical features to predict future events. Powers personalized campaigns by scoring likelihood of purchase, churn, or engagement.",
    category: "Predictive",
    status: "active",
    icon: <UserCheck size={24} />,
    capabilities: ["Feature engineering", "XGBoost modeling", "SHAP explainability", "Real-time scoring"],
    lastUsed: "2 hours ago",
    usageCount: 203,
    skillMapping: ["Predictive Modeling & Propensity Scoring", "Lookup-Table Enrichment & Dimensional Modeling"],
  },
  {
    id: "experimentation-agent",
    name: "A/B Testing & Experimentation Agent",
    description:
      "Design and analyze A/B tests to measure causal effects. Handles power calculations, sequential testing, and difference-in-differences analysis.",
    category: "Experimentation",
    status: "active",
    icon: <Shuffle size={24} />,
    capabilities: ["Power calculations", "Bayesian testing", "Sequential analysis", "Causal inference"],
    lastUsed: "1 hour ago",
    usageCount: 134,
    skillMapping: ["Experimentation & Causal Inference", "Anomaly Detection & Real-Time Monitoring"],
  },
  {
    id: "real-time-monitoring-agent",
    name: "Real-Time Monitoring Agent",
    description:
      "Automate detection of metric outliers with instant alerts. Uses statistical control charts and streaming aggregations for real-time insights.",
    category: "Real-Time",
    status: "active",
    icon: <Activity size={24} />,
    capabilities: ["Streaming analytics", "Control charts", "Alert pipelines", "Threshold monitoring"],
    lastUsed: "30 minutes ago",
    usageCount: 289,
    skillMapping: ["Anomaly Detection & Real-Time Monitoring", "Time-Series Analysis"],
  },
  {
    id: "journey-analysis-agent",
    name: "Customer Journey Agent",
    description:
      "Visualize user sequences across touchpoints. Maps customer paths using Markov chains and identifies optimal conversion routes.",
    category: "Customer Analytics",
    status: "beta",
    icon: <TrendingUp size={24} />,
    capabilities: ["Session graphs", "Markov chains", "Path visualization", "Sequence clustering"],
    lastUsed: "4 hours ago",
    usageCount: 78,
    skillMapping: ["Path & Journey Analysis", "Funnel Analysis & Conversion Drop-Off"],
  },
  {
    id: "metrics-calculation-agent",
    name: "Derived Metrics Agent",
    description:
      "Combine raw fields into meaningful KPIs and ratios. Maintains single-source metric definitions with validation and currency handling.",
    category: "Real-Time",
    status: "active",
    icon: <Brain size={24} />,
    capabilities: ["KPI calculations", "Currency conversion", "Validation tests", "Metric governance"],
    lastUsed: "1 hour ago",
    usageCount: 312,
    skillMapping: ["Calculated / Derived Metrics", "Lookup-Table Enrichment & Dimensional Modeling"],
  },
]

const categoryColors = {
  "Time-Series": "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
  "Customer Analytics": "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300",
  Marketing: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
  Experimentation: "bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300",
  "Real-Time": "bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-300",
  Predictive: "bg-indigo-100 text-indigo-800 dark:bg-indigo-900 dark:text-indigo-300",
}

const statusIcons = {
  active: <CheckCircle2 size={16} className="text-green-500" />,
  inactive: <AlertTriangle size={16} className="text-gray-500" />,
  beta: <Clock size={16} className="text-orange-500" />,
}

interface AgentsViewProps {
  onAgentSelect: (agentId: string) => void
}

export function AgentsView({ onAgentSelect }: AgentsViewProps) {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedCategory, setSelectedCategory] = useState<string>("all")
  const [selectedStatus, setSelectedStatus] = useState<string>("all")

  // Get unique categories and statuses
  const categories = Array.from(new Set(mockAgents.map((agent) => agent.category)))
  const statuses = Array.from(new Set(mockAgents.map((agent) => agent.status)))

  // Filter agents based on search and filters
  const filteredAgents = mockAgents.filter((agent) => {
    const matchesSearch =
      agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
      agent.capabilities.some((cap) => cap.toLowerCase().includes(searchQuery.toLowerCase())) ||
      agent.skillMapping.some((skill) => skill.toLowerCase().includes(searchQuery.toLowerCase()))

    const matchesCategory = selectedCategory === "all" || agent.category === selectedCategory
    const matchesStatus = selectedStatus === "all" || agent.status === selectedStatus

    return matchesSearch && matchesCategory && matchesStatus
  })

  const handleAgentClick = (agentId: string) => {
    onAgentSelect(agentId)
  }

  return (
    <div className="flex flex-col h-full bg-background p-6">
      <div className="mb-6">
        <h1 className="text-4xl font-bold mb-2">Analytics Agents</h1>
        <p className="text-muted-foreground">
          Specialized AI agents for data analytics, marketing attribution, customer insights, and experimentation. Each
          agent maps to core analytical skills and business questions.
        </p>
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4 mb-6">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground" size={20} />
          <Input
            placeholder="Search agents by name, skills, or capabilities..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10"
          />
        </div>

        <div className="flex gap-2">
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-3 py-2 border border-input bg-background rounded-md text-sm"
          >
            <option value="all">All Categories</option>
            {categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>

          <select
            value={selectedStatus}
            onChange={(e) => setSelectedStatus(e.target.value)}
            className="px-3 py-2 border border-input bg-background rounded-md text-sm"
          >
            <option value="all">All Status</option>
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Total Agents</p>
                <p className="text-2xl font-bold">{mockAgents.length}</p>
              </div>
              <Brain className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Active</p>
                <p className="text-2xl font-bold text-green-600">
                  {mockAgents.filter((a) => a.status === "active").length}
                </p>
              </div>
              <CheckCircle2 className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Beta</p>
                <p className="text-2xl font-bold text-orange-600">
                  {mockAgents.filter((a) => a.status === "beta").length}
                </p>
              </div>
              <Clock className="h-8 w-8 text-orange-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Skill Areas</p>
                <p className="text-2xl font-bold">13</p>
              </div>
              <BarChart3 className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Agents Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredAgents.map((agent) => (
          <Card
            key={agent.id}
            className="cursor-pointer hover:shadow-lg transition-shadow duration-200 group"
            onClick={() => handleAgentClick(agent.id)}
          >
            <CardHeader className="pb-3">
              <div className="flex items-start justify-between">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary/10 rounded-lg">{agent.icon}</div>
                  <div className="flex-1">
                    <CardTitle className="text-lg group-hover:text-primary transition-colors">{agent.name}</CardTitle>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge className={categoryColors[agent.category]}>{agent.category}</Badge>
                      <div className="flex items-center gap-1">
                        {statusIcons[agent.status]}
                        <span className="text-xs text-muted-foreground capitalize">{agent.status}</span>
                      </div>
                    </div>
                  </div>
                </div>
                <ArrowRight className="h-5 w-5 text-muted-foreground group-hover:text-primary group-hover:translate-x-1 transition-all" />
              </div>
            </CardHeader>

            <CardContent className="pt-0">
              <p className="text-sm text-muted-foreground mb-4 line-clamp-3">{agent.description}</p>

              {/* Skill Mapping */}
              <div className="mb-3">
                <p className="text-xs font-medium text-muted-foreground mb-2">Core Skills</p>
                <div className="flex flex-wrap gap-1">
                  {agent.skillMapping.slice(0, 2).map((skill, index) => (
                    <Badge key={index} variant="secondary" className="text-xs">
                      {skill}
                    </Badge>
                  ))}
                  {agent.skillMapping.length > 2 && (
                    <Badge variant="secondary" className="text-xs">
                      +{agent.skillMapping.length - 2} more
                    </Badge>
                  )}
                </div>
              </div>

              {/* Capabilities */}
              <div className="mb-4">
                <p className="text-xs font-medium text-muted-foreground mb-2">Technical Capabilities</p>
                <div className="flex flex-wrap gap-1">
                  {agent.capabilities.slice(0, 3).map((capability, index) => (
                    <Badge key={index} variant="outline" className="text-xs">
                      {capability}
                    </Badge>
                  ))}
                  {agent.capabilities.length > 3 && (
                    <Badge variant="outline" className="text-xs">
                      +{agent.capabilities.length - 3} more
                    </Badge>
                  )}
                </div>
              </div>

              {/* Usage Stats */}
              {agent.lastUsed && agent.usageCount && (
                <div className="flex justify-between text-xs text-muted-foreground pt-2 border-t">
                  <span>Last used: {agent.lastUsed}</span>
                  <span>{agent.usageCount} uses</span>
                </div>
              )}
            </CardContent>
          </Card>
        ))}
      </div>

      {/* No Results */}
      {filteredAgents.length === 0 && (
        <div className="flex flex-col items-center justify-center py-12">
          <Search className="h-12 w-12 text-muted-foreground mb-4" />
          <h3 className="text-lg font-semibold mb-2">No agents found</h3>
          <p className="text-muted-foreground text-center max-w-md">
            Try adjusting your search terms or filters to find the agents you&apos;tre looking for.
          </p>
          <Button
            variant="outline"
            onClick={() => {
              setSearchQuery("")
              setSelectedCategory("all")
              setSelectedStatus("all")
            }}
            className="mt-4"
          >
            Clear Filters
          </Button>
        </div>
      )}
    </div>
  )
}
