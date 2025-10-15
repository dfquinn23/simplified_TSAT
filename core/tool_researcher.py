"""
Software Update Researcher
Automatically researches software updates using web search tools
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import json

from crewai import Agent, Task, Crew
from crewai_tools import ScrapeWebsiteTool
from crewai.tools import BaseTool
# from langchain_community.tools import DuckDuckGoSearchResults
from langchain_openai import ChatOpenAI
from ddgs import DDGS

from core.api_changelog_registry import APIChangelogRegistry


class DuckDuckGoSearchTool(BaseTool):
    name: str = "web_search"
    description: str = "Search the web for information about software updates, release notes, and new features."

    def _run(self, query: str) -> str:
        """Execute the search"""
        print(f"   🔎 DuckDuckGo searching: '{query}'")  # Debug
        try:
            results = DDGS().text(query, max_results=5)
            # Debug
            print(f"   📊 Got {len(results) if results else 0} results")

            if not results:
                return "No results found."

            formatted = []
            for r in results:
                formatted.append(
                    f"Title: {r.get('title', 'N/A')}\n"
                    f"URL: {r.get('href', 'N/A')}\n"
                    f"Snippet: {r.get('body', 'N/A')}\n"
                )
            return "\n---\n".join(formatted)
        except Exception as e:
            error_msg = f"Search error: {str(e)}"
            print(f"   ❌ {error_msg}")  # Debug
            return error_msg


class SoftwareUpdateResearchAgent:
    """
    Research agent that discovers software updates and new features.
    Now with ACTUAL web search capability using custom tool!
    """

    def __init__(self, llm_model: str = "gpt-5", cache_duration_days: int = 30):
        self.api_registry = APIChangelogRegistry()
        self.cache_dir = Path("data/research_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(days=cache_duration_days)
        self.llm = ChatOpenAI(model=llm_model, temperature=1)

        # Initialize web search tools
        self.search_tool = DuckDuckGoSearchTool()  # ✅ Simple, clean
        self.scrape_tool = ScrapeWebsiteTool()

        # Initialize CrewAI agent with search tools
        self.research_agent = self._create_research_agent()

    def _create_research_agent(self) -> Agent:
        """Create research agent with web search tools"""
        return Agent(
            role='Software Update Research Specialist',
            goal='Find real, verifiable software updates from vendor websites and documentation',
            backstory='''You are an expert software researcher specializing in 
            finding product updates, new features, and API enhancements for business software.
            
            You have access to web search and can visit vendor websites directly.
            You focus on finding REAL information with specific details and sources.
            
            If you cannot find updates after thorough searching, you honestly report
            "No public updates found" rather than inventing information.
            
            You are especially good at researching financial services and business tools.''',
            tools=[self.search_tool, self.scrape_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def _normalize_tool_name(self, tool_name: str) -> str:
        """Normalize tool name for cache key"""
        return tool_name.lower().strip().replace(' ', '_')

    def _load_cache(self, tool_name: str, date_range: tuple) -> Optional[Dict]:
        """Load cached research results if available and not expired"""
        cache_key = self._normalize_tool_name(tool_name)
        cache_file = self.cache_dir / f"{cache_key}.json"

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)

            cached_time = datetime.fromisoformat(
                cached.get('cached_at', '2000-01-01'))
            if datetime.now() - cached_time < self.cache_duration:
                if cached.get('date_range') == list(date_range):
                    print(
                        f"   📦 Using cached results from {cached_time.strftime('%Y-%m-%d')}")
                    return cached.get('results')
        except Exception as e:
            print(f"   ⚠️ Cache read error: {e}")

        return None

    def _save_cache(self, tool_name: str, date_range: tuple, results: Dict):
        """Save research results to cache"""
        cache_key = self._normalize_tool_name(tool_name)
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            cache_data = {
                'tool_name': tool_name,
                'date_range': list(date_range),
                'cached_at': datetime.now().isoformat(),
                'results': results
            }
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"   ⚠️ Cache write error: {e}")

    async def research_tool_updates(
        self,
        tool_name: str,
        tool_type: str,
        start_date: str,
        end_date: str,
        research_depth: str = "medium"
    ) -> Dict[str, Any]:
        """
        Research updates for a specific tool

        Args:
            tool_name: Name of the tool
            tool_type: Type/category of tool (e.g., 'crm', 'portfolio_management')
            start_date: Start date for research (YYYY-MM-DD)
            end_date: End date for research (YYYY-MM-DD)
            research_depth: 'quick', 'medium', or 'deep'

        Returns:
            Dictionary with discovered updates
        """
        print(f"\n🔬 Researching updates for: {tool_name}")
        print(f"   Type: {tool_type}")
        print(f"   Date Range: {start_date} to {end_date}")
        print(f"   Depth: {research_depth}")

        # Check cache first
        date_range = (start_date, end_date)
        cached_results = self._load_cache(tool_name, date_range)
        if cached_results:
            return cached_results

        # Step 1: Check if tool has API endpoint
        if self.api_registry.has_api_endpoint(tool_name):
            print(f"   ✅ Found API endpoint in registry")
            api_results = await self._research_via_api(tool_name, start_date, end_date)
            if api_results['success']:
                self._save_cache(tool_name, date_range, api_results)
                return api_results
            else:
                print(f"   ⚠️ API research failed, falling back to web scraping")
        else:
            print(f"   ℹ️ No API endpoint found, using web research")

        # Step 2: Web research with search tools
        web_results = await self._research_via_web(
            tool_name,
            tool_type,
            start_date,
            end_date,
            research_depth
        )

        # Save to cache
        self._save_cache(tool_name, date_range, web_results)

        return web_results

    async def _research_via_api(
        self,
        tool_name: str,
        start_date: str,
        end_date: str
    ) -> Dict[str, Any]:
        """Research using API endpoint"""
        endpoint_info = self.api_registry.get_endpoint(tool_name)

        if not endpoint_info or not endpoint_info.get('endpoint'):
            return {'success': False, 'error': 'No API endpoint available'}

        try:
            if endpoint_info['auth_required']:
                print(f"   ⚠️ API requires authentication - check .env for credentials")
                return {
                    'success': False,
                    'error': 'Authentication required but credentials not configured',
                    'needs_setup': True
                }

            # Placeholder for actual API call logic
            result = {
                'success': True,
                'source': 'api',
                'tool_name': tool_name,
                'endpoint': endpoint_info['endpoint'],
                'updates_found': [],
                'note': 'API integration not yet implemented - use web research'
            }

            return result

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

    async def _research_via_web(
        self,
        tool_name: str,
        tool_type: str,
        start_date: str,
        end_date: str,
        research_depth: str
    ) -> Dict[str, Any]:
        """
        Research using web search tools.
        The agent now has ACTUAL search capability!
        """

        year_start = start_date.split('-')[0]
        year_end = end_date.split('-')[0]

        research_task = Task(
            description=f'''Research software updates for {tool_name} from {year_start} to {year_end}.

IMPORTANT: You have web search AND scrape tools available. Use them together to find REAL information.

RESEARCH STRATEGY:
1. First, understand what this tool is:
   - Search: "{tool_name} official website"
   - Search: "{tool_name} company"
   - **Scrape the official website to understand the product**
   
2. Find and READ update sources:
   - Search: "{tool_name} release notes {year_start}"
   - Search: "{tool_name} what's new {year_end}"
   - Search: "{tool_name} changelog"
   - Search: "{tool_name} updates {year_start}-{year_end}"
   - Search: "{tool_name} blog"
   - **For EVERY relevant URL you find, use the scrape tool to read the full page**
   
3. **CRITICAL - How to use the scrape tool:**
   - When search returns a blog post URL → Scrape that exact URL
   - When you find a release notes page → Scrape it
   - When you find a changelog → Scrape it
   - DON'T rely only on search snippets - they're incomplete
   - Example: Search finds "wealthbox.com/blog/new-feature" → Use scrape tool on that URL
   
4. Look for API and integration updates:
   - Search: "{tool_name} API updates {year_start}"
   - Search: "{tool_name} developer updates"
   - Search: "{tool_name} integration features"
   - **Scrape the developer documentation pages**

WHAT TO FIND:
- Major new features released
- API enhancements or new endpoints
- Integration capabilities (especially with other business tools)
- Automation features
- Mobile app updates
- Security/compliance updates

REQUIREMENTS FOR EACH UPDATE:
- **Feature Name**: Specific name (not generic like "New Features")
- **Date**: When it was released (month/year at minimum)
- **Description**: What it does and why it matters (2-3 sentences)
- **Source URL**: Link to official announcement or documentation
- **Category**: automation/integration/api/feature/mobile/security

WORKFLOW EXAMPLE:
1. Search "Wealthbox blog" → Find https://wealthbox.com/blog
2. Scrape https://wealthbox.com/blog → See list of posts
3. Scrape individual post URLs like https://wealthbox.com/blog/wealthbox-ai
4. Extract: feature name, date, description from the scraped content

HONESTY REQUIREMENT:
If you cannot find updates after searching AND scraping:
- Try 3-4 different search queries
- Scrape at least 3-5 relevant pages
- Check if the tool is behind a login wall
- If still no results, return "No public updates found"
- DO NOT make up features or dates

Tool Type Context: {tool_type}
Research Depth: {research_depth}''',
            agent=self.research_agent,
            expected_output='''A JSON object with this structure:
{{
    "success": true/false,
    "tool_name": "Tool Name",
    "source": "web_research",
    "updates": [
        {{
            "feature_name": "Specific Feature Name",
            "release_date": "YYYY-MM-DD or YYYY-MM or YYYY",
            "description": "Detailed description of what this feature does",
            "source_url": "https://...",
            "category": "automation/integration/api/feature/mobile/security",
            "business_impact": "How this helps businesses"
        }}
    ],
    "research_notes": "Summary of what was found and any challenges"
}}'''
        )

        try:
            print(f"   🔍 Starting web research with search tools...")
            crew = Crew(
                agents=[self.research_agent],
                tasks=[research_task],
                verbose=True
            )

            result = crew.kickoff()

            # Parse the result - handle CrewOutput object
            try:
                # CrewOutput has a raw attribute with the actual output
                if hasattr(result, 'raw'):
                    output_str = result.raw
                elif hasattr(result, 'output'):
                    output_str = result.output
                else:
                    output_str = str(result)

                # Try to extract JSON from the string
                import re
                json_match = re.search(r'\{.*\}', output_str, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                else:
                    parsed = {'success': False,
                              'error': 'Could not parse result as JSON'}

                # Ensure required fields exist
                if 'success' not in parsed:
                    parsed['success'] = True
                if 'tool_name' not in parsed:
                    parsed['tool_name'] = tool_name
                if 'source' not in parsed:
                    parsed['source'] = 'web_research'
                if 'updates' not in parsed:
                    parsed['updates'] = []

                print(
                    f"   ✅ Research complete: {len(parsed.get('updates', []))} updates found")
                return parsed

            except json.JSONDecodeError as e:
                print(f"   ⚠️ Could not parse research results as JSON: {e}")
                return {
                    'success': False,
                    'tool_name': tool_name,
                    'source': 'web_research',
                    'error': f'JSON parse error: {str(e)}',
                    'raw_output': output_str[:500] if 'output_str' in locals() else str(result)[:500]
                }

        except Exception as e:
            print(f"   ❌ Research failed: {str(e)}")
            return {
                'success': False,
                'tool_name': tool_name,
                'source': 'web_research',
                'error': str(e),
                'updates': []
            }
