# Agent Skills & Capabilities

## Overview
This document outlines all the capabilities and skills of the Vendo AI Analytics Assistant - a multi-agent system designed for data analytics, business intelligence, and marketing insights.

---

## 🎯 Key Features
- **Multi-Agent Architecture**: Utilizes a top-level agent that orchestrates sub-agents, each specialized in a specific task.



### Root Agent (`root_agent`)
- **Primary Role**: Orchestrates and routes requests to specialized sub-agents
- **Operating Modes**: 
  - **Clarify Mode**: Asks clarifying questions for ambiguous requests
  - **Auto Mode** (default): Makes reasonable assumptions and acts quickly
- **User Profile Integration**: Personalizes responses using company, country, timezone, currency, and annual targets
- **Tools:**: 
  - **Google Search** (`google_search`) - External information retrieval

### Sub-Agents
1. **Data Retrieval Agent** (`data_retrieval`) - understands user request and creates SQL queries, and returns the right data from BigQuery 
2. **Data Planner** (`data_planner`) - Tracking schema design


---

## 📊 Data Analysis Capabilities

### 1. SQL Query Generation & Execution
- ✅ **Creates BigQuery SQL queries** for complex analytics
- ✅ **Validates SQL syntax** before execution
- ✅ **Executes queries** against BigQuery data warehouse
- ✅ **Formats results** in readable tables with up to 100 rows display
- ✅ **Handles large datasets** with pagination and row limits

### 2. Database Context & Schema Knowledge
- ✅ **Knows event data schema** (`gam-dwh.mixpanel_data_3324357.mixpanel_all_data_export_full`)
- ✅ **Understands user data schema** (`gam-dwh.piri_red.engage` and `gam-dwh.piri_red.export`)
- ✅ **Maps user intent** to database fields using semantic matching
- ✅ **Handles data validation** with proper constraints and rules

### 3. Event & User Analytics
- ✅ **Tracks marketing events**: Page views, purchases, cart additions, product views
- ✅ **Analyzes user behavior**: Customer journeys, conversion funnels, retention
- ✅ **Campaign attribution**: First-touch and last-touch attribution analysis
- ✅ **UTM parameter analysis**: Source, medium, campaign, content, term tracking
- ✅ **Customer segmentation**: By location, behavior, purchase history, marketing consent

---

## 🔍 SQL Functions & Operations Mapping

### Aggregation Functions
| User Request | SQL Function | Example |
|-------------|-------------|---------|
| "Total revenue" | `SUM(amount)` | `SELECT SUM(cart_total_amount) FROM events` |
| "Average order value" | `AVG(amount)` | `SELECT AVG(cart_total_amount) FROM events` |
| "Count of customers" | `COUNT(DISTINCT distinct_id)` | `SELECT COUNT(DISTINCT distinct_id) FROM users` |
| "Number of events" | `COUNT(*)` | `SELECT COUNT(*) FROM events` |

### Date Functions
| User Request | SQL Function | Example |
|-------------|-------------|---------|
| "Last 30 days" | `DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)` | `WHERE DATE(report_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)` |
| "This month" | `DATE_TRUNC(CURRENT_DATE(), MONTH)` | `WHERE DATE(report_date) >= DATE_TRUNC(CURRENT_DATE(), MONTH)` |
| "Daily breakdown" | `DATE(timestamp)` | `GROUP BY DATE(report_date)` |
| "Monthly trends" | `DATE_TRUNC(DATE(timestamp), MONTH)` | `GROUP BY DATE_TRUNC(DATE(report_date), MONTH)` |

### Filtering & Segmentation
| User Request | SQL Implementation | Example |
|-------------|-------------------|---------|
| "Customers only" | `WHERE total_spent > 0` | Filter users who made purchases |
| "Newsletter subscribers" | `WHERE email_marketing_consent_state = 'subscribed'` | Marketing consent filtering |
| "By campaign" | `GROUP BY utm_campaign` | Campaign performance analysis |
| "By location" | `GROUP BY mp_reserved_city` | Geographic segmentation |

### Advanced Analytics
| Capability | SQL Pattern | Use Case |
|-----------|-------------|----------|
| **Cohort Analysis** | `WITH first_event AS (SELECT DISTINCT_ID, MIN(timestamp) as first_seen FROM events GROUP BY distinct_id)` | User acquisition analysis |
| **Attribution Analysis** | `WITH first_touch AS (SELECT distinct_id, FIRST_VALUE(utm_source) OVER (PARTITION BY distinct_id ORDER BY timestamp) as first_source FROM events)` | Marketing attribution |
| **Funnel Analysis** | Multiple CTEs with event filtering and user joins | Conversion funnel tracking |
| **Landing Page Analysis** | `REGEXP_EXTRACT(mp_reserved_current_url, r'^https?://[^/]+(/[^?]*)')` | Clean URL analysis |

---

## 📈 Data Visualization Capabilities

### 1. Chart Generation
- ✅ **Generates JSX code** for Recharts components
- ✅ **Supports multiple chart types**: Line, Bar, Scatter
- ✅ **Automatic chart type selection** based on data characteristics
- ✅ **Custom titles and formatting** for professional presentation

### 2. Chart Type Intelligence
| Data Type | Recommended Chart | Use Case |
|-----------|------------------|----------|
| **Time Series** | Line Chart | Revenue over time, daily users, trends |
| **Categories** | Bar Chart | Sales by campaign, users by source |
| **Correlations** | Scatter Chart | Ad spend vs revenue, price vs quantity |

### 3. Chart Components
```jsx
// Line Chart Example
<LineChart width={500} height={300} data={data}>
  <XAxis dataKey="x" />
  <YAxis />
  <Tooltip />
  <Line type="monotone" dataKey="y" stroke="#8884d8" />
</LineChart>

// Bar Chart Example  
<BarChart width={500} height={300} data={data}>
  <XAxis dataKey="x" />
  <YAxis />
  <Tooltip />
  <Bar dataKey="y" fill="#8884d8" />
</BarChart>

// Scatter Chart Example
<ScatterChart width={500} height={300} data={data}>
  <XAxis dataKey="x" type="number" />
  <YAxis dataKey="y" type="number" />
  <Tooltip />
  <Scatter data={data} fill="#8884d8" />
</ScatterChart>
```

---

## 🌐 External Information Capabilities

### 1. Google Search Integration
- ✅ **Real-time web search** for external information
- ✅ **Market research** and competitor analysis
- ✅ **Public data retrieval** (holidays, benchmarks, facts)
- ✅ **Source citation** with URLs and references
- ✅ **Regional customization** based on user profile

### 2. Search Use Cases
| Request Type | Example | Action |
|-------------|---------|--------|
| **Public Holidays** | "Easter 2025 dates in Australia" | Search for holiday dates |
| **Market Benchmarks** | "Average e-commerce conversion rate" | Industry benchmark lookup |
| **Competitor Info** | "Who are our main competitors?" | Competitive analysis |
| **General Facts** | "Population of New Zealand" | Factual information retrieval |

---

## 🛠️ Data Planning & Schema Design

### 1. Event Tracking Design
- ✅ **Creates event schemas** for new tracking requirements
- ✅ **Defines event properties** with data types and descriptions
- ✅ **Best practice naming** (verb-noun format, underscores)
- ✅ **Implementation guidance** for development teams

### 2. Event Schema Template
```
## Event Tracking Recommendation

### Event Name: Newsletter_Signup

### Event Properties:
- user_id: Unique identifier for the user - string
- email: User's email address - string  
- source_page: Page where signup occurred - string
- campaign_id: Marketing campaign identifier - string
- timestamp: Event occurrence time - datetime
- device_type: User's device category - string

### Implementation Notes:
- Ensure GDPR compliance for email storage
- Track source attribution for campaign analysis
```

---

## 🎯 Business Intelligence Features

### 1. Customer Analytics
- ✅ **Customer lifetime value** calculation
- ✅ **Purchase behavior analysis** 
- ✅ **Retention and churn** metrics
- ✅ **Segmentation by demographics** and behavior
- ✅ **Marketing consent tracking**

### 2. Marketing Analytics  
- ✅ **Campaign performance** measurement
- ✅ **Attribution modeling** (first-touch, last-touch)
- ✅ **UTM parameter analysis**
- ✅ **Conversion funnel** optimization
- ✅ **ROI and ROAS** calculations

### 3. E-commerce Analytics
- ✅ **Revenue tracking** and forecasting
- ✅ **Product performance** analysis
- ✅ **Cart abandonment** metrics
- ✅ **Average order value** trends
- ✅ **Geographic performance** analysis

---

## 🔧 Technical Capabilities

### 1. BigQuery Integration
- ✅ **Secure authentication** via service account
- ✅ **Query optimization** for performance
- ✅ **Error handling** and validation
- ✅ **Result formatting** and pagination
- ✅ **Data type handling** (strings, numbers, dates, decimals)

### 2. Data Processing
- ✅ **Pandas integration** for data manipulation
- ✅ **JSON serialization** for API responses
- ✅ **Date/time handling** with timezone awareness
- ✅ **Currency formatting** (AUD default)
- ✅ **URL cleaning** and normalization

### 3. System Architecture
- ✅ **Multi-agent orchestration** with routing logic
- ✅ **Context preservation** across conversations
- ✅ **User profile integration** for personalization
- ✅ **Error routing** to appropriate agents
- ✅ **Extensible design** for new capabilities

---

## 📋 Sample Queries & Use Cases

### Revenue Analysis
```sql
-- Total revenue by campaign for last 30 days
SELECT 
  utm_campaign,
  COUNT(*) as total_orders,
  SUM(cart_total_amount) as total_revenue,
  AVG(cart_total_amount) as avg_order_value
FROM `gam-dwh.mixpanel_data_3324357.mixpanel_all_data_export_full`
WHERE event = 'Order Received'
  AND DATE(report_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
GROUP BY utm_campaign
ORDER BY total_revenue DESC
```

### User Segmentation
```sql
-- Customer segmentation by marketing consent and purchase behavior
SELECT 
  CASE 
    WHEN total_spent > 0 AND email_marketing_consent_state = 'subscribed' THEN 'Customers - Newsletter Subscribers'
    WHEN total_spent > 0 AND email_marketing_consent_state = 'not_subscribed' THEN 'Customers - No Newsletter'
    WHEN total_spent = 0 AND email_marketing_consent_state = 'subscribed' THEN 'Prospects - Newsletter Subscribers'
    ELSE 'Prospects - No Newsletter'
  END as user_segment,
  COUNT(*) as user_count,
  AVG(total_spent) as avg_spent
FROM `gam-dwh.piri_red.engage`
GROUP BY user_segment
ORDER BY user_count DESC
```

### Conversion Funnel
```sql
-- Page views to purchase conversion funnel
WITH funnel_data AS (
  SELECT 
    distinct_id,
    COUNTIF(event = 'Page Viewed') as page_views,
    COUNTIF(event = 'Product Viewed') as product_views,
    COUNTIF(event = 'Product Added To Cart') as cart_adds,
    COUNTIF(event = 'Order Received') as purchases
  FROM `gam-dwh.mixpanel_data_3324357.mixpanel_all_data_export_full`
  WHERE DATE(report_date) >= DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY)
  GROUP BY distinct_id
)
SELECT 
  'Page Views' as funnel_step,
  COUNT(*) as users,
  NULL as conversion_rate
FROM funnel_data WHERE page_views > 0
UNION ALL
SELECT 
  'Product Views' as funnel_step,
  COUNT(*) as users,
  ROUND(COUNT(*) / (SELECT COUNT(*) FROM funnel_data WHERE page_views > 0) * 100, 2) as conversion_rate
FROM funnel_data WHERE product_views > 0
-- Continue for other funnel steps...
```

---

## 🚀 Advanced Features

### 1. Intelligent Routing
- ✅ **Automatic agent selection** based on request type
- ✅ **Context-aware routing** for complex queries
- ✅ **Escalation handling** for unsupported requests
- ✅ **Cross-agent communication** for comprehensive answers

### 2. User Experience
- ✅ **Natural language processing** for query interpretation
- ✅ **Semantic field mapping** for user-friendly requests
- ✅ **Confirmation workflows** before query execution
- ✅ **Professional formatting** of results and charts

### 3. Extensibility
- ✅ **Modular agent design** for easy expansion
- ✅ **Schema-driven configuration** for new data sources
- ✅ **Plugin architecture** for additional tools
- ✅ **API-ready responses** for frontend integration

---

## 📞 Contact & Support

For questions about agent capabilities or to request new features, please refer to the development team or check the project documentation.

**Last Updated**: January 2025  
**Version**: 1.0  
**Supported Models**: Google Gemini via ADK 