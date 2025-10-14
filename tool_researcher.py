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
from crewai_tools import tool, ScrapeWebsiteTool
from langchain_openai import ChatOpenAI
from duckduckgo_search import DDGS

from core.api_changelog_registry import APIChangelogRegistry


class SoftwareUpdateResearchAgent:
    """
    Research agent that discovers software updates and new features.
    Now with ACTUAL web search capability!
    """

    def __init__(self, llm_model: str = "gpt-4", cache_duration_days: int = 30):
        self.api_registry = APIChangelogRegistry()
        self.cache_dir = Path("data/research_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(days=cache_duration_days)
        self.llm = ChatOpenAI(model=llm_model, temperature=0.3)

        # Initialize web search tools
        self.search_tool = self._create_search_tool()
        self.scrape_tool = ScrapeWebsiteTool()

        # Initialize CrewAI agent with search tools
        self.research_agent = self._create_research_agent()

    def _create_search_tool(self):
        """Create DuckDuckGo search tool (free, no API key needed!)"""
        @tool("Search the web")
        def search_web(query: str) -> str:
            """
            Search the web using DuckDuckGo. 
            Use this to find information about software updates, release notes, and new features.
            Returns top search results with titles, URLs, and snippets.
            """
            try:
                results = DDGS().text(query, max_results=5)
                if not results:
                    return "No results found for this query."

                formatted = []
                for r in results:
                    formatted.append(
                        f"Title: {r.get('title', 'N/A')}\n"
                        f"URL: {r.get('href', 'N/A')}\n"
                        f"Snippet: {r.get('body', 'N/A')}\n"
                    )
                return "\n---\n".join(formatted)
            except Exception as e:
                return f"Search error: {str(e)}"

        return search_web

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
            
            You are especially good at researching financial services and business tools.
            ''',
            tools=[self.search_tool, self.scrape_tool],
            verbose=True,
            allow_delegation=False
        )

    def _load_cache(self, tool_name: str, date_range: tuple) -> Optional[Dict]:
        """Load cached research results"""
        cache_key = f"{tool_name.lower().replace(' ', '_')}_{date_range[0]}_{date_range[1]}"
        cache_file = self.cache_dir / f"{cache_key}.json"

        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cached_time = datetime.fromisoformat(
                        data.get('cached_at', '1970-01-01'))
                    if datetime.now() - cached_time < self.cache_duration:
                        print(f"   💾 Using cached research for {tool_name}")
                        return data.get('results')
            except Exception as e:
                print(f"   ⚠️ Cache load error: {e}")
        return None

    def _save_cache(self, tool_name: str, date_range: tuple, results: Dict) -> None:
        """Save research results to cache"""
        cache_key = f"{tool_name.lower().replace(' ', '_')}_{date_range[0]}_{date_range[1]}"
        cache_file = self.cache_dir / f"{cache_key}.json"

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'cached_at': datetime.now().isoformat(),
                    'tool_name': tool_name,
                    'date_range': date_range,
                    'results': results
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"   ⚠️ Cache save error: {e}")

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

IMPORTANT: You have web search tools available. Use them to find REAL information from vendor websites.

RESEARCH STRATEGY:
1. First, understand what this tool is:
   - Search: "{tool_name} official website"
   - Search: "{tool_name} company"
   
2. Then search for updates and release notes:
   - Search: "{tool_name} release notes {year_start}"
   - Search: "{tool_name} what's new {year_end}"
   - Search: "{tool_name} changelog"
   - Search: "{tool_name} updates {year_start}-{year_end}"
   
3. Look for API and integration improvements:
   - Search: "{tool_name} API updates"
   - Search: "{tool_name} new features automation"
   - Search: "{tool_name} integration enhancements"

WHAT TO FIND:
Focus on features that enable automation:
- New API endpoints or capabilities
- Webhook support
- Workflow automation features
- Integration improvements
- Data export/import enhancements
- OAuth or authentication improvements
- Real-time sync capabilities

OUTPUT FORMAT:
For EACH real update you find, provide:

Feature Name: [Specific feature name from vendor]
Release Date: [Actual date or quarter, e.g., "Q2 2024" or "March 2024"]
Source URL: [Where you found this information]
Description: [What specifically changed - be detailed]
Automation Value: [How this helps automate work]

---

If after thorough searching you find NO public updates:
State clearly: "No public updates found for {tool_name}"
Then explain:
- What searches you performed
- Possible reasons (login-required portal, no public changelog, etc.)

CRITICAL RULES:
- Only report information you actually found via web search
- Include source URLs for everything
- Be specific with feature names (not generic like "API improvements")
- If you can't find something, say so honestly
''',
            agent=self.research_agent,
            expected_output=f'List of verified updates with source URLs, or honest statement that no public updates were found'
        )

        crew = Crew(
            agents=[self.research_agent],
            tasks=[research_task],
            verbose=True
        )

        try:
            print(f"   🔍 Researching {tool_name} with web search...")
            research_output = crew.kickoff()

            # Parse the output
            structured_updates = self._parse_agent_output(
                research_output,
                tool_name,
                tool_type,
                start_date,
                end_date
            )

            return {
                'success': True,
                'source': 'web_search',
                'tool_name': tool_name,
                'tool_type': tool_type,
                'date_range': f"{start_date} to {end_date}",
                'research_depth': research_depth,
                'updates': structured_updates,
                'raw_output': str(research_output),
                'timestamp': datetime.now().isoformat()
            }

        except Exception as e:
            print(f"   ❌ Research failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'tool_name': tool_name,
                'updates': []
            }

    def _parse_agent_output(
        self,
        agent_output: Any,
        tool_name: str,
        tool_type: str,
        start_date: str,
        end_date: str
    ) -> List[Dict]:
        """
        Parse agent output into structured updates.
        Returns empty list if no updates found.
        """
        output_text = str(agent_output)

        # Check if agent explicitly said no updates found
        no_updates_patterns = [
            'no public updates found',
            'no updates found',
            'could not find',
            'no information available',
            'no public changelog',
            'no verifiable updates'
        ]

        if any(pattern in output_text.lower() for pattern in no_updates_patterns):
            print(f"   ℹ️  Agent found no public updates for {tool_name}")
            return []

        # Try to extract structured updates
        updates = []

        # Look for the structured format we asked for
        sections = output_text.split('---')

        for section in sections:
            if not section.strip():
                continue

            update = {}
            lines = section.split('\n')

            for line in lines:
                line = line.strip()
                if not line or ':' not in line:
                    continue

                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()

                if 'feature' in key or 'name' in key:
                    update['feature_name'] = value
                elif 'date' in key or 'released' in key:
                    update['release_date'] = value
                elif 'url' in key or 'source' in key:
                    update['source_url'] = value
                elif 'description' in key:
                    update['description'] = value
                elif 'automation' in key or 'value' in key:
                    update['automation_value'] = value

            # Only add if we have at least a feature name
            if update.get('feature_name'):
                updates.append(update)

        # If no structured parsing worked, try the old method
        if not updates:
            # Use AI to structure the findings
            try:
                analysis_task = Task(
                    description=f'''Analyze the research findings and create structured update records.
                    
                    Research Output:
                    {output_text}
                    
                    For each update/feature found:
                    1. Extract the feature name
                    2. Identify release date (or estimate quarter if not found)
                    3. Summarize what it does
                    4. Generate a business impact description focusing on:
                       - Time savings potential
                       - Manual work that can be eliminated
                       - Process improvements
                       - Integration opportunities
                    5. Estimate implementation difficulty (quick/medium/complex)
                    
                    Format as a JSON list where each item has:
                    - feature_name: string
                    - release_date: string (YYYY-MM-DD or YYYY-QQ)
                    - description: string (2-3 sentences)
                    - automation_value: string (specific time/cost savings)
                    - business_impact: string (how this helps the business)
                    - implementation_difficulty: string (quick/medium/complex)
                    ''',
                    agent=self.research_agent,
                    expected_output='JSON formatted list of structured update records'
                )

                crew = Crew(
                    agents=[self.research_agent],
                    tasks=[analysis_task],
                    verbose=False
                )

                analysis_output = crew.kickoff()

                # Try to parse as JSON
                try:
                    parsed_updates = json.loads(str(analysis_output))
                    if isinstance(parsed_updates, list) and parsed_updates:
                        updates = parsed_updates
                except:
                    pass
            except Exception as e:
                print(f"   ⚠️ Analysis parsing error: {e}")

        if not updates:
            print(f"   ⚠️  Could not parse structured updates from agent output")
        else:
            print(f"   ✅ Extracted {len(updates)} updates for {tool_name}")

        return updates

    async def research_tool_stack(
        self,
        tools: List[Dict],
        start_date: str,
        end_date: str,
        research_depth: str = "medium"
    ) -> Dict[str, Any]:
        """
        Research updates for an entire tool stack

        Args:
            tools: List of tools with 'name' and 'type' keys
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            research_depth: 'quick', 'medium', or 'deep'

        Returns:
            Dictionary with all research results
        """
        print(f"\n🔬 Starting research for {len(tools)} tools")
        print(f"   Date Range: {start_date} to {end_date}")
        print(f"   Research Depth: {research_depth}")

        results = {}

        for tool in tools:
            tool_name = tool.get('name', tool.get('Tool Name', ''))
            tool_type = tool.get('type', tool.get('Tool Type', 'unknown'))

            try:
                research_result = await self.research_tool_updates(
                    tool_name=tool_name,
                    tool_type=tool_type,
                    start_date=start_date,
                    end_date=end_date,
                    research_depth=research_depth
                )
                results[tool_name] = research_result

                # Brief pause to avoid rate limiting
                await asyncio.sleep(1)

            except Exception as e:
                print(f"   ❌ Error researching {tool_name}: {e}")
                results[tool_name] = {
                    'success': False,
                    'error': str(e)
                }

        return {
            'total_tools': len(tools),
            'successful': len([r for r in results.values() if r.get('success')]),
            'failed': len([r for r in results.values() if not r.get('success')]),
            'results': results,
            'date_range': f"{start_date} to {end_date}",
            'timestamp': datetime.now().isoformat()
        }


# Convenience function
async def research_tool_updates(
    tool_name: str,
    tool_type: str,
    start_date: str,
    end_date: str,
    research_depth: str = "medium"
) -> Dict[str, Any]:
    """Quick function to research a single tool"""
    agent = SoftwareUpdateResearchAgent()
    return await agent.research_tool_updates(
        tool_name, tool_type, start_date, end_date, research_depth
    )


# Example usage
if __name__ == "__main__":
    async def test_research():
        agent = SoftwareUpdateResearchAgent()

        # Test with a single tool
        result = await agent.research_tool_updates(
            tool_name="Microsoft 365",
            tool_type="productivity_suite",
            start_date="2023-10-01",
            end_date="2025-10-01",
            research_depth="medium"
        )

        print("\n" + "="*60)
        print("📊 Research Results:")
        print(json.dumps(result, indent=2))

    asyncio.run(test_research())
