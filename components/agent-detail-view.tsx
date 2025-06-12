"use client"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  ArrowLeft,
  Play,
  Settings,
  BarChart3,
  Clock,
  CheckCircle2,
  AlertTriangle,
  LineChart,
  Users,
  PieChart,
  Target,
  DollarSign,
} from "lucide-react"
import { ReactNode } from "react"

interface Agent {
  id: string
  name: string
  description: string
  category: "Time-Series" | "Customer Analytics" | "Marketing" | "Experimentation" | "Real-Time" | "Predictive"
  status: "active" | "inactive" | "beta"
  icon: ReactNode
  capabilities: string[]
  skillMapping: string[]
  lastUsed: string
  usageCount: number
  version: string
  accuracy: string
  responseTime: string
  detailedDescription: string
  features: string[]
  businessQuestions: string[]
  recentActivity: Array<{
    time: string
    action: string
    severity: "low" | "medium" | "high"
  }>
}

interface AgentDetailProps {
  agentId: string
  onBack: () => void
  onLaunchAgent: (agentId: string) => void
}

// Mock agent data with detailed analytics focus
const getAgentDetails = (agentId: string): Agent | null => {
  const agentMap: Record<string, Agent> = {
    "time-series-agent": {
      id: "time-series-agent",
      name: "Time-Series Forecasting Agent",
      description:
        "Track metric evolution, spot trends, seasonality and shocks. Performs period-over-period analysis and forecasts future performance using Prophet and ARIMA models.",
      category: "Time-Series",
      status: "active",
      icon: <LineChart size={32} />,
      capabilities: ["SQL window functions", "Prophet forecasting", "Seasonality decomposition", "Anomaly detection"],
      skillMapping: ["Time-Series Analysis", "Anomaly Detection & Real-Time Monitoring"],
      lastUsed: "1 hour ago",
      usageCount: 234,
      version: "3.2.1",
      accuracy: "92.4%",
      responseTime: "< 200ms",
      detailedDescription:
        "Advanced time-series analysis agent that combines SQL window functions with machine learning forecasting models. Uses Prophet for trend and seasonality detection, ARIMA for complex patterns, and statistical methods for anomaly detection. Ideal for tracking KPIs like revenue, CAC, and conversion rates over time.",
      features: [
        "SQL DATE_TRUNC and window functions for MoM/YoY analysis",
        "Prophet and ARIMA forecasting models",
        "Seasonality decomposition and trend analysis",
        "Change-point detection using ruptures library",
        "Automated period-over-period reporting",
        "Integration with BI dashboards for visualization",
      ],
      businessQuestions: [
        "What will our Q4 revenue look like based on current trends?",
        "When did our CAC start increasing and why?",
        "Are there seasonal patterns in our user acquisition?",
        "Which metrics show unusual behavior this month?",
      ],
      recentActivity: [
        { time: "1 hour ago", action: "Forecasted Q4 paid-ad spend vs revenue", severity: "low" },
        { time: "3 hours ago", action: "Detected CAC spike after creative change", severity: "high" },
        { time: "6 hours ago", action: "Generated seasonality report for Black Friday", severity: "medium" },
        { time: "1 day ago", action: "Updated ARIMA model with latest data", severity: "low" },
      ],
    },
    "cohort-analysis-agent": {
      id: "cohort-analysis-agent",
      name: "Cohort Analysis Agent",
      description:
        "Group users by shared start actions and measure retention or value over time. Analyzes user lifecycle patterns and cohort LTV progression.",
      category: "Customer Analytics",
      status: "active",
      icon: <Users size={32} />,
      capabilities: ["Cohort bucketing", "Retention matrices", "Survival analysis", "Churn prediction"],
      skillMapping: ["Cohort Analysis", "Customer Lifetime Value (LTV) Modeling"],
      lastUsed: "2 hours ago",
      usageCount: 156,
      version: "2.8.0",
      accuracy: "94.7%",
      responseTime: "< 150ms",
      detailedDescription:
        "Specialized cohort analysis agent that groups users by acquisition date or first action to track retention and value over time. Uses survival analysis for churn prediction and calculates cohort-based LTV metrics. Essential for understanding user lifecycle patterns and optimizing retention strategies.",
      features: [
        "SQL cohort bucketing with MIN(event_date) per user_id",
        "Retention matrices using window functions",
        "Survival analysis with lifelines library for churn curves",
        "Cohort LTV calculations by acquisition channel",
        "Integration with Mixpanel and Amplitude cohort tools",
        "Automated cohort reporting and alerting",
      ],
      businessQuestions: [
        "How do Black Friday users compare to regular acquisition cohorts?",
        "What's the LTV difference between organic vs paid users?",
        "Which cohorts have the highest 90-day retention?",
        "When do most users typically churn in their lifecycle?",
      ],
      recentActivity: [
        { time: "2 hours ago", action: "Analyzed Black Friday vs normal week retention", severity: "medium" },
        { time: "4 hours ago", action: "Updated cohort LTV by first product purchased", severity: "low" },
        { time: "8 hours ago", action: "Generated monthly cohort retention report", severity: "low" },
        { time: "1 day ago", action: "Alert: Cohort retention below threshold", severity: "high" },
      ],
    },
    "attribution-agent": {
      id: "attribution-agent",
      name: "Attribution & Incrementality Agent",
      description:
        "Allocate credit to marketing touches and estimate incremental lift. Uses multi-touch attribution models and geo-matched market tests.",
      category: "Marketing",
      status: "active",
      icon: <Target size={32} />,
      capabilities: ["Multi-touch attribution", "Markov chains", "Incrementality testing", "Holdout analysis"],
      skillMapping: ["Attribution & Incrementality", "Experimentation & Causal Inference"],
      lastUsed: "5 hours ago",
      usageCount: 98,
      version: "2.1.5",
      accuracy: "89.3%",
      responseTime: "< 300ms",
      detailedDescription:
        "Advanced attribution agent that goes beyond last-click to understand true marketing impact. Uses Markov chain models for multi-touch attribution and implements geo-matched market tests for incrementality measurement. Essential for optimizing marketing spend allocation.",
      features: [
        "Multi-touch attribution models (linear, time-decay, Markov)",
        "Geo-matched market testing for incrementality",
        "Bayesian structural time-series with CausalImpact",
        "Integration with Facebook's Robyn MMM framework",
        "Holdout test design and analysis",
        "Cross-channel attribution reporting",
      ],
      businessQuestions: [
        "What's the true incremental ROAS of our TikTok campaigns?",
        "How much credit should email get in our conversion paths?",
        "Which channels work best together (synergy effects)?",
        "What would happen if we paused our brand campaigns?",
      ],
      recentActivity: [
        { time: "5 hours ago", action: "Measured TikTok vs email incremental ROAS", severity: "medium" },
        { time: "8 hours ago", action: "Updated Markov chain attribution model", severity: "low" },
        { time: "12 hours ago", action: "Completed geo-holdout test analysis", severity: "high" },
        { time: "2 days ago", action: "Generated cross-channel attribution report", severity: "low" },
      ],
    },
    "segmentation-agent": {
      id: "segmentation-agent",
      name: "Customer Segmentation Agent",
      description:
        "Group users by shared behavior or attributes using ML clustering. Creates actionable segments for personalized messaging and targeted campaigns.",
      category: "Customer Analytics",
      status: "active",
      icon: <PieChart size={32} />,
      capabilities: ["RFM analysis", "K-means clustering", "Feature engineering", "Segment profiling"],
      skillMapping: ["Segmentation & Clustering", "Lookup-Table Enrichment & Dimensional Modeling"],
      lastUsed: "4 hours ago",
      usageCount: 145,
      version: "2.5.3",
      accuracy: "91.8%",
      responseTime: "< 250ms",
      detailedDescription:
        "ML-powered segmentation agent that identifies meaningful customer groups using behavioral and demographic features. Implements RFM analysis, K-means clustering, and advanced feature engineering to create actionable segments for marketing personalization.",
      features: [
        "RFM (Recency, Frequency, Monetary) analysis",
        "K-means, DBSCAN, and Gaussian Mixture clustering",
        "Customer embedding generation for similarity",
        "PCA and UMAP for segment visualization",
        "Integration with Meta custom audiences",
        "Automated segment profiling and naming",
      ],
      businessQuestions: [
        "Who are our most price-sensitive customers?",
        "Which users are likely to become high-value customers?",
        "How should we personalize messaging for different segments?",
        "Which segments respond best to different offer types?",
      ],
      recentActivity: [
        { time: "4 hours ago", action: "Identified high-value, low-frequency segment", severity: "medium" },
        { time: "6 hours ago", action: "Updated RFM segmentation model", severity: "low" },
        { time: "10 hours ago", action: "Synced segments to Meta custom audiences", severity: "low" },
        { time: "1 day ago", action: "Generated segment performance report", severity: "medium" },
      ],
    },
    "ltv-modeling-agent": {
      id: "ltv-modeling-agent",
      name: "LTV Prediction Agent",
      description:
        "Predict customer lifetime value using probabilistic models. Forecasts net present value to optimize acquisition spending and retention strategies.",
      category: "Predictive",
      status: "active",
      icon: <DollarSign size={32} />,
      capabilities: ["BG/NBD modeling", "Survival analysis", "DCF calculations", "Churn probability"],
      skillMapping: ["Customer Lifetime Value (LTV) Modeling", "Predictive Modeling & Propensity Scoring"],
      lastUsed: "6 hours ago",
      usageCount: 167,
      version: "3.1.2",
      accuracy: "88.9%",
      responseTime: "< 180ms",
      detailedDescription:
        "Probabilistic LTV modeling agent using BG/NBD and Gamma-Gamma models to predict customer lifetime value. Incorporates survival analysis for churn prediction and discounted cash flow calculations for accurate NPV estimates.",
      features: [
        "BG/NBD and Gamma-Gamma probabilistic models",
        "Survival analysis for churn probability estimation",
        "Discounted cash flow calculations in SQL",
        "PyMC probabilistic programming integration",
        "Real-time LTV scoring for new customers",
        "CAC payback period optimization",
      ],
      businessQuestions: [
        "What's the 12-month LTV for different acquisition channels?",
        "How much should we bid for Google Ads based on predicted LTV?",
        "Which customers are likely to have highest lifetime value?",
        "What's our LTV:CAC ratio by customer segment?",
      ],
      recentActivity: [
        { time: "6 hours ago", action: "Updated 12-month LTV model for CAC bidding", severity: "high" },
        { time: "8 hours ago", action: "Generated LTV predictions for new cohort", severity: "medium" },
        { time: "12 hours ago", action: "Calculated churn probability scores", severity: "low" },
        { time: "1 day ago", action: "Optimized Google Ads bidding caps", severity: "medium" },
      ],
    },
    // Add more detailed agent mappings as needed
  }

  return agentMap[agentId] || null
}

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

const severityColors = {
  low: "text-green-600",
  medium: "text-orange-600",
  high: "text-red-600",
}

export function AgentDetailView({ agentId, onBack, onLaunchAgent }: AgentDetailProps) {
  const agent = getAgentDetails(agentId)

  if (!agent) {
    return (
      <div className="flex flex-col h-full bg-background p-6">
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-2">Agent Not Found</h2>
            <p className="text-muted-foreground mb-4">The requested agent could not be found.</p>
            <Button onClick={onBack}>
              <ArrowLeft size={16} className="mr-2" />
              Back to Agents
            </Button>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full bg-background p-6 overflow-auto">
      {/* Header */}
      <div className="flex items-center gap-4 mb-6">
        <Button variant="ghost" onClick={onBack} className="flex items-center gap-2">
          <ArrowLeft size={16} />
          Back to Agents
        </Button>
      </div>

      {/* Agent Header */}
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-start gap-4">
          <div className="p-3 bg-primary/10 rounded-lg">{agent.icon}</div>
          <div>
            <h1 className="text-3xl font-bold mb-2">{agent.name}</h1>
            <p className="text-muted-foreground mb-3 max-w-2xl">{agent.description}</p>
            <div className="flex items-center gap-3">
              <Badge className={categoryColors[agent.category]}>{agent.category}</Badge>
              <div className="flex items-center gap-1">
                {statusIcons[agent.status]}
                <span className="text-sm text-muted-foreground capitalize">{agent.status}</span>
              </div>
              <span className="text-sm text-muted-foreground">v{agent.version}</span>
            </div>
          </div>
        </div>

        <div className="flex gap-2">
          <Button variant="outline">
            <Settings size={16} className="mr-2" />
            Configure
          </Button>
          <Button onClick={() => onLaunchAgent(agentId)}>
            <Play size={16} className="mr-2" />
            Launch Agent
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Usage Count</p>
                <p className="text-2xl font-bold">{agent.usageCount}</p>
              </div>
              <BarChart3 className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Accuracy</p>
                <p className="text-2xl font-bold text-green-600">{agent.accuracy}</p>
              </div>
              <CheckCircle2 className="h-8 w-8 text-green-500" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Response Time</p>
                <p className="text-2xl font-bold">{agent.responseTime}</p>
              </div>
              <Clock className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Last Used</p>
                <p className="text-lg font-semibold">{agent.lastUsed}</p>
              </div>
              <Clock className="h-8 w-8 text-muted-foreground" />
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="lg:col-span-2 space-y-6">
          {/* Detailed Description */}
          <Card>
            <CardHeader>
              <CardTitle>About This Agent</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground leading-relaxed">{agent.detailedDescription}</p>
            </CardContent>
          </Card>

          {/* Core Skills Mapping */}
          <Card>
            <CardHeader>
              <CardTitle>Core Analytical Skills</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {agent.skillMapping.map((skill: string, index: number) => (
                  <div key={index} className="flex items-center gap-3 p-3 bg-muted/50 rounded-lg">
                    <CheckCircle2 size={16} className="text-green-500 flex-shrink-0" />
                    <span className="font-medium">{skill}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Business Questions */}
          <Card>
            <CardHeader>
              <CardTitle>Business Questions This Agent Answers</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {agent.businessQuestions?.map((question: string, index: number) => (
                  <div key={index} className="flex items-start gap-3 p-3 border-l-4 border-primary/20 bg-primary/5">
                    <span className="text-primary font-bold text-lg">Q:</span>
                    <span className="text-sm font-medium">{question}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Technical Features */}
          <Card>
            <CardHeader>
              <CardTitle>Technical Capabilities</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 gap-3">
                {agent.features.map((feature: string, index: number) => (
                  <div key={index} className="flex items-start gap-2">
                    <CheckCircle2 size={16} className="text-green-500 flex-shrink-0 mt-0.5" />
                    <span className="text-sm">{feature}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {agent.recentActivity.map((activity: any, index: number) => (
                  <div key={index} className="flex items-start gap-3">
                    <div
                      className={`w-2 h-2 rounded-full mt-2 ${
                        activity.severity === "high"
                          ? "bg-red-500"
                          : activity.severity === "medium"
                            ? "bg-orange-500"
                            : "bg-green-500"
                      }`}
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium">{activity.action}</p>
                      <p className="text-xs text-muted-foreground">{activity.time}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle>Quick Actions</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              <Button variant="outline" className="w-full justify-start">
                <Play size={16} className="mr-2" />
                Run Analysis
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Settings size={16} className="mr-2" />
                Configure Parameters
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <BarChart3 size={16} className="mr-2" />
                View Historical Results
              </Button>
              <Button variant="outline" className="w-full justify-start">
                <Clock size={16} className="mr-2" />
                Schedule Recurring Run
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}
