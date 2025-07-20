import os
import json
import requests
from typing import Dict, List, Optional, Any
from datetime import datetime, date
import asyncio
import time

from ...state_manager import get_current_connection_id
from ...mixpanel_client import MixpanelClient

# Global instance - will be initialized by the agent
_mixpanel_mcp_tools = None

def initialize_mixpanel_mcp_tools(mixpanel_client):
    """Initialize the global MixpanelMCPTools instance."""
    global _mixpanel_mcp_tools
    _mixpanel_mcp_tools = MixpanelMCPTools(mixpanel_client)

class MixpanelMCPTools:
    """
    Internal class for handling Mixpanel MCP server connections and requests.
    """
    
    def __init__(self, mixpanel_client):
        """
        Initialize MCP tools with Mixpanel client configuration.
        
        Args:
            mixpanel_client: Configured MixpanelClient instance with project credentials
        """
        self.mixpanel_client = mixpanel_client
        self.project_id = mixpanel_client._project_id
        self.username = mixpanel_client._username
        self.secret = mixpanel_client._secret
        
        # Determine region from mixpanel_client
        region = getattr(mixpanel_client, 'region', 'US')
        if hasattr(mixpanel_client, 'lexicon_api_url'):
            if 'eu.mixpanel.com' in mixpanel_client.lexicon_api_url:
                region = 'EU'
            elif 'in.mixpanel.com' in mixpanel_client.lexicon_api_url:
                region = 'IN'
            else:
                region = 'US'
        
        self.region = region
        
        # MCP server URL - These are estimated based on Mixpanel's regional API pattern
        # May need adjustment based on actual MCP server endpoints
        self.mcp_base_url = self._get_mcp_url()
        
        # Initialize session with authentication
        self.session = requests.Session()
        self.session.auth = (self.username, self.secret)
        
        # Set request headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'VendoAI-MCP-Client/1.0'
        })
    
    def _get_mcp_url(self) -> str:
        """
        Get the MCP server URL based on the region.
        
        Returns:
            str: The MCP server base URL
        """
        urls = {
            'US': 'https://mcp.mixpanel.com',
            'EU': 'https://mcp-eu.mixpanel.com', 
            'IN': 'https://mcp-in.mixpanel.com'
        }
        return urls.get(self.region, urls['US'])
    
    def _make_mcp_request(self, endpoint: str, method: str = 'POST', data=None) -> dict:
        """
        Make a request to the MCP server with proper error handling.
        
        Args:
            endpoint: API endpoint path
            method: HTTP method ('GET', 'POST', 'PUT', 'DELETE')
            data: Request payload data
            
        Returns:
            Dict containing response data or error information
        """
        url = f"{self.mcp_base_url}{endpoint}"
        
        try:
            # Add timestamp and request ID for tracking
            if data:
                data['timestamp'] = datetime.now().isoformat()
                data['request_id'] = f"mcp_{int(time.time() * 1000)}"
            
            if method.upper() == 'GET':
                response = self.session.get(url, params=data, timeout=30)
            elif method.upper() == 'POST':
                response = self.session.post(url, json=data, timeout=30)
            elif method.upper() == 'PUT':
                response = self.session.put(url, json=data, timeout=30)
            elif method.upper() == 'DELETE':
                response = self.session.delete(url, timeout=30)
            else:
                return {
                    'error': f'Unsupported HTTP method: {method}',
                    'suggestion': 'Use GET, POST, PUT, or DELETE'
                }
            
            # Handle response status codes
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                return {
                    'error': 'Authentication failed',
                    'suggestion': 'Check your Mixpanel service account credentials'
                }
            elif response.status_code == 403:
                return {
                    'error': 'Access denied',
                    'suggestion': 'Verify your service account has the required permissions'
                }
            elif response.status_code == 404:
                return {
                    'error': 'MCP endpoint not found',
                    'suggestion': 'Check the MCP server URL and endpoint path'
                }
            elif response.status_code == 429:
                return {
                    'error': 'Rate limit exceeded',
                    'suggestion': 'Wait before making more requests'
                }
            elif response.status_code >= 500:
                return {
                    'error': 'MCP server error',
                    'suggestion': 'Try again later or contact Mixpanel support'
                }
            else:
                return {
                    'error': f'Unexpected response status: {response.status_code}',
                    'suggestion': 'Check the request parameters and try again'
                }
        
        except requests.exceptions.Timeout:
            return {
                'error': 'Request timeout',
                'suggestion': 'The MCP server is not responding. Try again later.'
            }
        except requests.exceptions.ConnectionError:
            return {
                'error': 'Connection error',
                'suggestion': 'Check your internet connection and MCP server URL'
            }
        except requests.exceptions.RequestException as e:
            return {
                'error': f'Request error: {str(e)}',
                'suggestion': 'Check your request parameters and network connection'
            }
        except Exception as e:
            return {
                'error': f'Unexpected error: {str(e)}',
                'suggestion': 'Contact support if this error persists'
            }

# Standalone functions for Google ADK integration
def query_events_mcp(event_name: str, date_range: str = '7d') -> dict:
    """
    Query events using Mixpanel's MCP server for advanced analytics.
    
    Args:
        event_name: Name of the event to query
        date_range: Time range for the query (e.g., '7d', '30d', '1h')
        
    Returns:
        Dict containing event data or error information
    """
    if not _mixpanel_mcp_tools:
        return {
            'mime_type': 'text/plain',
            'data': "❌ Error: MCP tools not initialized",
            'raw_data': []
        }
    
    if not event_name:
        return {
            'mime_type': 'text/plain',
            'data': "❌ Error: Event name is required",
            'raw_data': []
        }
    
    payload = {
        'project_id': _mixpanel_mcp_tools.project_id,
        'event_name': event_name,
        'date_range': date_range,
        'filters': {},
        'mcp_version': '1.0'
    }
    
    result = _mixpanel_mcp_tools._make_mcp_request('/events/query', 'POST', payload)
    
    if 'error' in result:
        return {
            'mime_type': 'text/plain',
            'data': f"❌ MCP Error: {result['error']}\n💡 Suggestion: {result.get('suggestion', 'Contact support')}",
            'raw_data': [],
            'error_details': result
        }
    
    events = result.get('events', [])
    return {
        'mime_type': 'application/json',
        'data': f"✅ Retrieved {len(events)} events for '{event_name}' (last {date_range})",
        'raw_data': events,
        'metadata': {
            'event_name': event_name,
            'date_range': date_range,
            'query_timestamp': datetime.now().isoformat()
        }
    }

def get_user_profiles_mcp(limit: int = 100) -> dict:
    """
    Get user profiles using Mixpanel's MCP server.
    
    Args:
        limit: Maximum number of profiles to return
        
    Returns:
        Dict containing user profile data or error information
    """
    if not _mixpanel_mcp_tools:
        return {
            'mime_type': 'text/plain',
            'data': "❌ Error: MCP tools not initialized",
            'raw_data': []
        }
    
    if limit > 1000:
        return {
            'mime_type': 'text/plain',
            'data': "❌ Error: Limit cannot exceed 1000 profiles per request",
            'raw_data': []
        }
    
    payload = {
        'project_id': _mixpanel_mcp_tools.project_id,
        'user_ids': [],
        'limit': limit,
        'filters': {},
        'mcp_version': '1.0'
    }
    
    result = _mixpanel_mcp_tools._make_mcp_request('/profiles/query', 'POST', payload)
    
    if 'error' in result:
        return {
            'mime_type': 'text/plain',
            'data': f"❌ MCP Error: {result['error']}\n💡 Suggestion: {result.get('suggestion', 'Contact support')}",
            'raw_data': [],
            'error_details': result
        }
    
    profiles = result.get('profiles', [])
    return {
        'mime_type': 'application/json',
        'data': f"✅ Retrieved {len(profiles)} user profiles",
        'raw_data': profiles,
        'metadata': {
            'limit_applied': limit,
            'query_timestamp': datetime.now().isoformat()
        }
    }

def create_funnel_mcp(funnel_name: str, date_range: str = '30d') -> dict:
    """
    Create a funnel analysis using Mixpanel's MCP server.
    
    Args:
        funnel_name: Descriptive name for the funnel
        date_range: Time range for the funnel analysis
        
    Returns:
        Dict containing funnel analysis results or error information
    """
    if not _mixpanel_mcp_tools:
        return {
            'mime_type': 'text/plain',
            'data': "❌ Error: MCP tools not initialized",
            'raw_data': []
        }
    
    if not funnel_name:
        return {
            'mime_type': 'text/plain',
            'data': "❌ Error: Funnel name is required",
            'raw_data': []
        }
    
    # Default funnel steps for common user journey
    default_steps = [
        {'event': 'page_view', 'name': 'Page View'},
        {'event': 'signup', 'name': 'Sign Up'}
    ]
    
    payload = {
        'project_id': _mixpanel_mcp_tools.project_id,
        'funnel_name': funnel_name,
        'steps': default_steps,
        'date_range': date_range,
        'filters': {},
        'mcp_version': '1.0'
    }
    
    result = _mixpanel_mcp_tools._make_mcp_request('/funnels/create', 'POST', payload)
    
    if 'error' in result:
        return {
            'mime_type': 'text/plain',
            'data': f"❌ MCP Error: {result['error']}\n💡 Suggestion: {result.get('suggestion', 'Contact support')}",
            'raw_data': [],
            'error_details': result
        }
    
    return {
        'mime_type': 'application/json',
        'data': f"✅ Created funnel '{funnel_name}' with {len(default_steps)} steps",
        'raw_data': result,
        'metadata': {
            'funnel_name': funnel_name,
            'steps_count': len(default_steps),
            'date_range': date_range,
            'creation_timestamp': datetime.now().isoformat()
        }
    }

def get_cohorts_mcp() -> dict:
    """
    Get cohorts using Mixpanel's MCP server.
        
    Returns:
        Dict containing cohort data or error information
    """
    if not _mixpanel_mcp_tools:
        return {
            'mime_type': 'text/plain',
            'data': "❌ Error: MCP tools not initialized",
            'raw_data': []
        }
    
    payload = {
        'project_id': _mixpanel_mcp_tools.project_id,
        'cohort_name': None,
        'cohort_type': None,
        'mcp_version': '1.0'
    }
    
    result = _mixpanel_mcp_tools._make_mcp_request('/cohorts/list', 'POST', payload)
    
    if 'error' in result:
        return {
            'mime_type': 'text/plain',
            'data': f"❌ MCP Error: {result['error']}\n💡 Suggestion: {result.get('suggestion', 'Contact support')}",
            'raw_data': [],
            'error_details': result
        }
    
    cohorts = result.get('cohorts', [])
    return {
        'mime_type': 'application/json',
        'data': f"✅ Retrieved {len(cohorts)} cohorts",
        'raw_data': cohorts,
        'metadata': {
            'query_timestamp': datetime.now().isoformat()
        }
    }

def get_insights_mcp(insight_type: str) -> dict:
    """
    Generate insights using Mixpanel's MCP server.
    
    Args:
        insight_type: Type of insight to generate (e.g., 'trends', 'predictions', 'anomalies')
        
    Returns:
        Dict containing generated insights or error information
    """
    if not _mixpanel_mcp_tools:
        return {
            'mime_type': 'text/plain',
            'data': "❌ Error: MCP tools not initialized",
            'raw_data': []
        }
    
    if not insight_type:
        return {
            'mime_type': 'text/plain',
            'data': "❌ Error: Insight type is required",
            'raw_data': []
        }
    
    payload = {
        'project_id': _mixpanel_mcp_tools.project_id,
        'insight_type': insight_type,
        'parameters': {},
        'mcp_version': '1.0'
    }
    
    result = _mixpanel_mcp_tools._make_mcp_request('/insights/generate', 'POST', payload)
    
    if 'error' in result:
        return {
            'mime_type': 'text/plain',
            'data': f"❌ MCP Error: {result['error']}\n💡 Suggestion: {result.get('suggestion', 'Contact support')}",
            'raw_data': [],
            'error_details': result
        }
    
    return {
        'mime_type': 'application/json',
        'data': f"✅ Generated {insight_type} insights",
        'raw_data': result,
        'metadata': {
            'insight_type': insight_type,
            'generation_timestamp': datetime.now().isoformat()
        }
    }

def get_retention_analysis_mcp(event_name: str, date_range: str = '30d', cohort_size: str = 'day') -> dict:
    """
    Get retention analysis using Mixpanel's MCP server.
    
    Args:
        event_name: Event name for retention analysis
        date_range: Time range for the analysis
        cohort_size: Cohort size for analysis ('day', 'week', 'month')
        
    Returns:
        Dict containing retention analysis results or error information
    """
    if not _mixpanel_mcp_tools:
        return {
            'mime_type': 'text/plain',
            'data': "❌ Error: MCP tools not initialized",
            'raw_data': []
        }
    
    if not event_name:
        return {
            'mime_type': 'text/plain',
            'data': "❌ Error: Event name is required for retention analysis",
            'raw_data': []
        }
    
    payload = {
        'project_id': _mixpanel_mcp_tools.project_id,
        'event_name': event_name,
        'date_range': date_range,
        'cohort_size': cohort_size,
        'mcp_version': '1.0'
    }
    
    result = _mixpanel_mcp_tools._make_mcp_request('/retention/analyze', 'POST', payload)
    
    if 'error' in result:
        return {
            'mime_type': 'text/plain',
            'data': f"❌ MCP Error: {result['error']}\n💡 Suggestion: {result.get('suggestion', 'Contact support')}",
            'raw_data': [],
            'error_details': result
        }
    
    return {
        'mime_type': 'application/json',
        'data': f"✅ Generated retention analysis for '{event_name}'",
        'raw_data': result,
        'metadata': {
            'event_name': event_name,
            'date_range': date_range,
            'cohort_size': cohort_size,
            'analysis_timestamp': datetime.now().isoformat()
        }
    }

def get_schema_mcp(entity_type: str = 'all') -> dict:
    """
    Get schema information using Mixpanel's MCP server.
    
    Args:
        entity_type: Type of schema to retrieve ('events', 'properties', 'all')
        
    Returns:
        Dict containing schema information or error information
    """
    if not _mixpanel_mcp_tools:
        return {
            'mime_type': 'text/plain',
            'data': "❌ Error: MCP tools not initialized",
            'raw_data': []
        }
    
    payload = {
        'project_id': _mixpanel_mcp_tools.project_id,
        'entity_type': entity_type,
        'mcp_version': '1.0'
    }
    
    result = _mixpanel_mcp_tools._make_mcp_request('/schema/info', 'POST', payload)
    
    if 'error' in result:
        return {
            'mime_type': 'text/plain',
            'data': f"❌ MCP Error: {result['error']}\n💡 Suggestion: {result.get('suggestion', 'Contact support')}",
            'raw_data': [],
            'error_details': result
        }
    
    return {
        'mime_type': 'application/json',
        'data': f"✅ Retrieved schema information for {entity_type}",
        'raw_data': result,
        'metadata': {
            'entity_type': entity_type,
            'query_timestamp': datetime.now().isoformat()
        }
    }

# Helper functions for data serialization and compatibility
def convert_to_json_serializable(obj):
    """
    Recursively convert non-JSON-serializable objects (dates, decimals) to serializable types.
    
    Args:
        obj: Object to convert
        
    Returns:
        JSON-serializable version of the object
    """
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: convert_to_json_serializable(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_to_json_serializable(item) for item in obj]
    else:
        return obj
