# Mixpanel MCP Agent Integration

This document explains how to integrate and use the Mixpanel MCP (Model Context Protocol) agent with Google ADK for advanced analytics capabilities.

## Overview

The Mixpanel MCP agent provides access to advanced Mixpanel analytics capabilities through MCP server integration, enabling:

- **Real-time event data access** with advanced filtering
- **Advanced funnel and cohort analysis** with multi-step conversion tracking
- **User profile management** with behavioral pattern analysis
- **Retention analysis** with cohort-based metrics
- **Schema information retrieval** for data exploration
- **Advanced insights generation** including predictive analytics

## Architecture

The agent uses a **standalone functions approach** compatible with Google ADK:

```
Agent System:
├── agent.py - Main agent definition
├── prompt.py - Agent-specific prompts
├── tools.py - MCP integration functions
└── README.md - This documentation
```

### Key Components

1. **MixpanelMCPTools Class**: Internal class for MCP server communication
2. **Standalone Functions**: Google ADK-compatible tool functions
3. **Global Instance**: Shared MCP tools instance across functions
4. **Initialization**: One-time setup during agent loading

## Setup Instructions

### 1. Environment Variables

Ensure you have the following environment variables set:

```bash
export MODEL_GEMINI="your-gemini-model-name"
export DEBUG_MODE="false"  # Set to "true" for verbose debugging
```

### 2. Authentication

The agent uses your existing MixpanelClient configuration for authentication. Ensure your Mixpanel credentials are properly configured in your Firebase/Firestore setup with the following fields:

- `project_id`: Your Mixpanel project ID
- `service_account_user_name`: Service account username
- `service_account_secret`: Service account secret/password
- `region`: Data region (US, EU, or IN)

### 3. MCP Server Configuration

The agent automatically determines the appropriate MCP server URL based on your region:

- **US**: `https://mcp.mixpanel.com`
- **EU**: `https://mcp-eu.mixpanel.com`
- **IN**: `https://mcp-in.mixpanel.com`

**Important Note**: These URLs are estimated based on Mixpanel's regional API structure. You may need to adjust them based on the actual MCP server endpoints provided by Mixpanel.

## Available Tools

The Mixpanel MCP agent provides the following standalone functions:

### 1. `query_events_mcp` - Advanced Event Querying
Query events with enhanced filtering and real-time access capabilities.

**Parameters:**
- `event_name` (str): Name of the event to query
- `date_range` (str, optional): Time range (default: '7d')
- `filters` (Dict, optional): Advanced filtering parameters

**Example:**
```python
result = query_events_mcp(
    event_name="Order Received",
    date_range="30d",
    filters={"product_category": "electronics"}
)
```

### 2. `get_user_profiles_mcp` - User Profile Management
Access detailed user profiles with advanced segmentation.

**Parameters:**
- `user_ids` (List[str], optional): Specific user IDs to retrieve
- `limit` (int, optional): Maximum profiles to return (default: 100)
- `filters` (Dict, optional): User segmentation filters

### 3. `create_funnel_mcp` - Advanced Funnel Analysis
Create sophisticated multi-step conversion funnels.

**Parameters:**
- `funnel_name` (str): Descriptive name for the funnel
- `steps` (List[Dict]): Funnel steps with events and conditions
- `date_range` (str, optional): Analysis time range (default: '30d')
- `filters` (Dict, optional): Funnel-specific filters

### 4. `get_cohorts_mcp` - Cohort Management
Access and analyze user cohorts with advanced tracking.

**Parameters:**
- `cohort_name` (str, optional): Specific cohort to retrieve
- `cohort_type` (str, optional): Type-based cohort filtering

### 5. `get_insights_mcp` - Advanced Analytics
Generate predictive insights and trend analysis.

**Parameters:**
- `insight_type` (str): Type of insight ('trends', 'predictions', 'anomalies')
- `parameters` (Dict, optional): Insight-specific parameters

### 6. `get_retention_analysis_mcp` - Retention Analysis
Perform detailed retention analysis with cohort-based metrics.

**Parameters:**
- `event_name` (str): Event for retention analysis
- `date_range` (str, optional): Analysis time range (default: '30d')
- `cohort_size` (str, optional): Cohort size ('day', 'week', 'month')

### 7. `get_schema_mcp` - Schema Information
Explore available events, properties, and data structures.

**Parameters:**
- `entity_type` (str, optional): Schema type ('events', 'properties', 'all')

## Usage Examples

### Basic Event Query
```bash
@mixpanel_mcp query events for "Page View" in the last 7 days
```

### Advanced Funnel Analysis
```bash
@mixpanel_mcp create a funnel for user onboarding: signup -> email verification -> profile completion
```

### Cohort Analysis
```bash
@mixpanel_mcp analyze retention for users who signed up in the last month
```

### Schema Exploration
```bash
@mixpanel_mcp show me all available events and their properties
```

## Troubleshooting

### Common Issues

#### 1. Error: "MCP tools not initialized"
**Cause**: The global MCP tools instance wasn't properly initialized.
**Solution**: Restart the agent system to trigger proper initialization.

#### 2. Error: "Authentication failed"
**Cause**: Invalid Mixpanel credentials or insufficient permissions.
**Solution**: 
- Verify your Mixpanel service account credentials
- Ensure the service account has MCP access permissions
- Check your project ID and region settings

#### 3. Error: "MCP endpoint not found"
**Cause**: The MCP server URL is incorrect or the endpoint doesn't exist.
**Solution**:
- Contact Mixpanel support for official MCP server URLs
- Verify your region configuration
- Check if MCP is enabled for your Mixpanel project

#### 4. Error: "Connection error"
**Cause**: Network connectivity issues or server downtime.
**Solution**:
- Check your internet connection
- Verify firewall settings allow HTTPS requests
- Try again later if the MCP server is experiencing issues

### Debug Mode

Enable debug mode for detailed logging:

```bash
export DEBUG_MODE="true"
```

This will provide:
- Detailed error messages
- Request/response logging
- Parameter validation details
- Troubleshooting suggestions

### Health Check

You can verify the agent is properly loaded by checking:

1. **Agent Registration**: The agent appears in the available agents list
2. **Tool Loading**: All 7 MCP tools are available
3. **Initialization**: The global MCP tools instance is created

## Integration with Other Agents

### Collaboration Patterns

- **Data Retrieval Agent**: Complement BigQuery data with MCP insights
- **Analyst Agent**: Provide MCP data for advanced statistical analysis
- **Root Agent**: Escalate when external coordination is needed

### Data Flow

```
User Request → Root Agent → Mixpanel MCP Agent → MCP Server → Results
```

## Performance Considerations

### Rate Limiting
- MCP server may have rate limits
- Agent includes automatic retry logic
- Use appropriate request timing

### Data Volume
- Limit large queries to avoid timeouts
- Use pagination for large datasets
- Consider caching for frequently accessed data

### Server Capacity
- MCP server capacity may vary by region
- Monitor response times and adjust accordingly
- Implement fallback strategies for high-load scenarios

## Security

### Data Protection
- All requests use HTTPS encryption
- Authentication credentials are securely managed
- No sensitive data is logged (except in debug mode)

### Access Control
- Service account permissions control MCP access
- Project-level security applies to all MCP requests
- Audit logging available through Mixpanel's standard logging

## Support

### Getting Help

1. **Documentation**: Refer to this README and inline function documentation
2. **Debug Mode**: Enable for detailed error information
3. **Mixpanel Support**: Contact for MCP server-specific issues
4. **Agent Logs**: Check application logs for detailed error traces

### Known Limitations

1. **MCP Server URLs**: Currently estimated; may need adjustment
2. **Feature Availability**: Some MCP features may not be available in all regions
3. **Rate Limits**: MCP server rate limits may apply
4. **Beta Features**: Some MCP capabilities may be in beta

## Future Enhancements

Planned improvements:
- Dynamic MCP server URL discovery
- Enhanced caching mechanisms
- Advanced error recovery strategies
- Performance optimization features
- Extended MCP capability support

---

For technical support or feature requests, please contact your system administrator or Mixpanel support. 