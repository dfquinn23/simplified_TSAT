# core/api_changelog_registry.py
"""
API Changelog Endpoint Registry
Maintains a database of known API endpoints for software changelogs and release notes
"""

from typing import Dict, Optional, List
from datetime import datetime, timedelta


class APIChangelogRegistry:
    """Registry of known API endpoints for software changelogs"""
    
    def __init__(self):
        self.endpoints = self._initialize_registry()
    
    def _initialize_registry(self) -> Dict[str, Dict]:
        """Initialize the registry with known API endpoints"""
        return {
            # Productivity & Communication
            'microsoft 365': {
                'endpoint': 'https://graph.microsoft.com/v1.0/admin/serviceAnnouncement/messages',
                'auth_required': True,
                'auth_type': 'oauth2',
                'format': 'json',
                'tool_type': 'productivity_suite',
                'date_field': 'lastModifiedDateTime',
                'title_field': 'title',
                'description_field': 'body.content',
                'category_field': 'category',
                'documentation': 'https://docs.microsoft.com/en-us/graph/api/serviceannouncement-list-messages',
                'notes': 'Requires Microsoft Graph API credentials with ServiceMessage.Read.All permission'
            },
            'zoom': {
                'endpoint': 'https://developers.zoom.us/changelog',
                'auth_required': False,
                'format': 'html_structured',
                'tool_type': 'communication',
                'documentation': 'https://developers.zoom.us/changelog',
                'notes': 'Web scraping with structured HTML, no API auth needed'
            },
            'slack': {
                'endpoint': 'https://api.slack.com/changelog',
                'auth_required': False,
                'format': 'html_structured',
                'tool_type': 'communication',
                'documentation': 'https://api.slack.com/changelog',
                'notes': 'Public changelog, web scraping with structured format'
            },
            'microsoft teams': {
                'endpoint': 'https://graph.microsoft.com/v1.0/admin/serviceAnnouncement/messages',
                'auth_required': True,
                'auth_type': 'oauth2',
                'format': 'json',
                'tool_type': 'communication',
                'date_field': 'lastModifiedDateTime',
                'title_field': 'title',
                'description_field': 'body.content',
                'category_field': 'category',
                'documentation': 'https://docs.microsoft.com/en-us/graph/api/serviceannouncement-list-messages',
                'notes': 'Same as Microsoft 365, filter for Teams service'
            },
            
            # CRM & Sales
            'salesforce': {
                'endpoint': 'https://api.salesforce.com/services/data/v58.0/tooling/query',
                'auth_required': True,
                'auth_type': 'oauth2',
                'format': 'json',
                'tool_type': 'crm',
                'query_param': '?q=SELECT+Id,Name,Description,ReleaseDate+FROM+ReleaseUpdate',
                'documentation': 'https://developer.salesforce.com/docs/atlas.en-us.api_tooling.meta/api_tooling/',
                'notes': 'Requires Salesforce API access'
            },
            'redtail crm': {
                'endpoint': 'https://api.redtailtechnology.com/changelog',
                'auth_required': False,
                'format': 'html_structured',
                'tool_type': 'crm',
                'documentation': 'https://redtailtechnology.com/updates',
                'notes': 'Check website updates page, may require web scraping'
            },
            
            # Financial Services - Research Platforms
            'factset': {
                'endpoint': 'https://developer.factset.com/release-notes',
                'auth_required': False,
                'format': 'html_structured',
                'tool_type': 'research_platform',
                'documentation': 'https://developer.factset.com',
                'notes': 'Developer portal has structured release notes'
            },
            'bloomberg terminal': {
                'endpoint': None,  # No public API
                'auth_required': True,
                'format': 'manual',
                'tool_type': 'research_platform',
                'documentation': 'https://www.bloomberg.com/professional/support/software-updates/',
                'notes': 'Requires Bloomberg terminal access or web scraping support pages'
            },
            'morningstar direct': {
                'endpoint': 'https://www.morningstar.com/products/direct/updates',
                'auth_required': False,
                'format': 'html_structured',
                'tool_type': 'research_platform',
                'documentation': 'https://www.morningstar.com/products/direct',
                'notes': 'Product updates page, requires web scraping'
            },
            
            # Financial Services - Portfolio Management
            'orion eclipse': {
                'endpoint': 'https://support.orionadvisor.com/support/solutions/folders/9000211932',
                'auth_required': False,
                'format': 'html_structured',
                'tool_type': 'portfolio_management',
                'documentation': 'https://support.orionadvisor.com',
                'notes': 'Support portal has release notes section'
            },
            'addepar': {
                'endpoint': 'https://support.addepar.com/hc/en-us/sections/115000249826-Release-Notes',
                'auth_required': False,
                'format': 'html_structured',
                'tool_type': 'portfolio_management',
                'documentation': 'https://support.addepar.com',
                'notes': 'Support center with release notes, web scraping needed'
            },
            'schwab portfolioCenter': {
                'endpoint': 'https://advisorservices.schwab.com/updates',
                'auth_required': False,
                'format': 'html_structured',
                'tool_type': 'portfolio_management',
                'documentation': 'https://advisorservices.schwab.com',
                'notes': 'Advisor services site, may require login for full details'
            },
            
            # Financial Services - Custodial
            'charles schwab': {
                'endpoint': 'https://advisorservices.schwab.com/updates',
                'auth_required': False,
                'format': 'html_structured',
                'tool_type': 'custodial',
                'documentation': 'https://advisorservices.schwab.com',
                'notes': 'Check advisor services updates section'
            },
            'fidelity institutional': {
                'endpoint': 'https://institutional.fidelity.com/app/news-and-insights/updates',
                'auth_required': False,
                'format': 'html_structured',
                'tool_type': 'custodial',
                'documentation': 'https://institutional.fidelity.com',
                'notes': 'Institutional updates page'
            },
            
            # Financial Planning
            'rightcapital': {
                'endpoint': 'https://rightcapital.com/updates',
                'auth_required': False,
                'format': 'html_structured',
                'tool_type': 'financial_planning',
                'documentation': 'https://rightcapital.com',
                'notes': 'Product updates blog/page'
            },
            
            # Operations & Productivity
            'docusign': {
                'endpoint': 'https://developers.docusign.com/changelog',
                'auth_required': False,
                'format': 'html_structured',
                'tool_type': 'operations',
                'documentation': 'https://developers.docusign.com',
                'notes': 'Developer changelog with API updates'
            },
            'quickbooks': {
                'endpoint': 'https://developer.intuit.com/app/developer/qbo/docs/develop/changelog',
                'auth_required': False,
                'format': 'html_structured',
                'tool_type': 'operations',
                'documentation': 'https://developer.intuit.com',
                'notes': 'Developer documentation has API changelog'
            },
            'adp workforce now': {
                'endpoint': 'https://www.adp.com/resources/articles-and-insights/product-updates.aspx',
                'auth_required': False,
                'format': 'html_structured',
                'tool_type': 'operations',
                'documentation': 'https://www.adp.com',
                'notes': 'Product updates section, web scraping required'
            },
            
            # Development Tools
            'github': {
                'endpoint': 'https://api.github.com/repos/{owner}/{repo}/releases',
                'auth_required': False,
                'format': 'json',
                'tool_type': 'development',
                'date_field': 'published_at',
                'title_field': 'name',
                'description_field': 'body',
                'documentation': 'https://docs.github.com/en/rest/releases',
                'notes': 'Requires owner/repo parameters, rate limited without auth'
            },
            
            # Cloud Services
            'aws': {
                'endpoint': 'https://aws.amazon.com/new/',
                'auth_required': False,
                'format': 'html_structured',
                'tool_type': 'cloud_services',
                'documentation': 'https://aws.amazon.com/new/',
                'notes': 'What\'s New page, requires web scraping'
            },
        }
    
    def get_endpoint(self, tool_name: str) -> Optional[Dict]:
        """
        Get API endpoint information for a tool
        
        Args:
            tool_name: Name of the tool (case-insensitive)
            
        Returns:
            Dictionary with endpoint information or None if not found
        """
        tool_key = tool_name.lower().strip()
        return self.endpoints.get(tool_key)
    
    def has_api_endpoint(self, tool_name: str) -> bool:
        """Check if a tool has a known API endpoint"""
        endpoint_info = self.get_endpoint(tool_name)
        return endpoint_info is not None and endpoint_info.get('endpoint') is not None
    
    def requires_auth(self, tool_name: str) -> bool:
        """Check if the API endpoint requires authentication"""
        endpoint_info = self.get_endpoint(tool_name)
        return endpoint_info.get('auth_required', False) if endpoint_info else False
    
    def get_tools_by_type(self, tool_type: str) -> List[str]:
        """Get all tools in the registry of a specific type"""
        return [
            tool_name for tool_name, info in self.endpoints.items()
            if info.get('tool_type') == tool_type
        ]
    
    def add_endpoint(self, tool_name: str, endpoint_info: Dict) -> None:
        """
        Add a new endpoint to the registry
        
        Args:
            tool_name: Name of the tool
            endpoint_info: Dictionary with endpoint configuration
        """
        tool_key = tool_name.lower().strip()
        self.endpoints[tool_key] = endpoint_info
    
    def get_all_tools(self) -> List[str]:
        """Get list of all tools in the registry"""
        return list(self.endpoints.keys())
    
    def get_registry_stats(self) -> Dict:
        """Get statistics about the registry"""
        total_tools = len(self.endpoints)
        with_api = len([t for t, info in self.endpoints.items() if info.get('endpoint')])
        requires_auth = len([t for t, info in self.endpoints.items() if info.get('auth_required')])
        
        tool_types = {}
        for info in self.endpoints.values():
            tool_type = info.get('tool_type', 'unknown')
            tool_types[tool_type] = tool_types.get(tool_type, 0) + 1
        
        return {
            'total_tools': total_tools,
            'with_api_endpoint': with_api,
            'requires_authentication': requires_auth,
            'by_tool_type': tool_types
        }


# Convenience function for quick access
def get_api_endpoint(tool_name: str) -> Optional[Dict]:
    """Quick function to get endpoint info for a tool"""
    registry = APIChangelogRegistry()
    return registry.get_endpoint(tool_name)


# Example usage and testing
if __name__ == "__main__":
    registry = APIChangelogRegistry()
    
    print("📚 API Changelog Registry Initialized")
    print("=" * 60)
    
    stats = registry.get_registry_stats()
    print(f"\n📊 Registry Statistics:")
    print(f"   Total Tools: {stats['total_tools']}")
    print(f"   With API Endpoints: {stats['with_api_endpoint']}")
    print(f"   Requires Auth: {stats['requires_authentication']}")
    
    print(f"\n🏷️  Tools by Type:")
    for tool_type, count in stats['by_tool_type'].items():
        print(f"   {tool_type}: {count} tools")
    
    print(f"\n🔍 Example: Looking up 'Microsoft 365'")
    endpoint_info = registry.get_endpoint('Microsoft 365')
    if endpoint_info:
        print(f"   ✅ Found!")
        print(f"   Endpoint: {endpoint_info['endpoint']}")
        print(f"   Auth Required: {endpoint_info['auth_required']}")
        print(f"   Tool Type: {endpoint_info['tool_type']}")
        print(f"   Format: {endpoint_info['format']}")
    
    print(f"\n🔍 Example: Looking up 'FactSet'")
    endpoint_info = registry.get_endpoint('FactSet')
    if endpoint_info:
        print(f"   ✅ Found!")
        print(f"   Endpoint: {endpoint_info['endpoint']}")
        print(f"   Auth Required: {endpoint_info['auth_required']}")
        print(f"   Tool Type: {endpoint_info['tool_type']}")
