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


class SoftwareUpdateResearcher:
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
    
    async def research_tool_updates(
        self,
        tool_name: str,
        tool_type: str = "business_software",
        lookback_years: int = 2,
        research_depth: str = "medium"
    ) -> Dict[str, Any]:
        """
        Research tool updates using web search.
        
        Args:
            tool_name: Name of the software tool
            tool_type: Category of tool
            lookback_years: How many years back to search
            research_depth: quick, medium, or deep
            
        Returns:
            Dict with research results including updates found
        """
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=lookback_years * 365)
        start_str = start_date.strftime("%Y-%m-%d")
        end_str = end_date.strftime("%Y-%m-%d")
        
        # Check cache
        cache_key = f"{tool_name.lower().replace(' ', '_')}_{start_str}_{end_str}"
        cached_result = self._check_cache(cache_key)
        if cached_result:
            print(f"   💾 Using cached results for {tool_name}")
            return cached_result['results']
        
        # Perform research with web search
        result = await self._research_via_web(
            tool_name,
            tool_type,
            start_str,
            end_str,
            research_depth
        )
        
        # Cache result
        self._save_to_cache(cache_key, result)
        
        return result
    
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
        The agent will automatically figure out the best searches.
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
                tool_name
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
        tool_name: str
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
        
        if not updates:
            print(f"   ⚠️  Could not parse structured updates from agent output")
        else:
            print(f"   ✅ Extracted {len(updates)} updates for {tool_name}")
        
        return updates
    
    def _check_cache(self, cache_key: str) -> Optional[Dict]:
        """Check if cached results exist and are still valid"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            cached_time = datetime.fromisoformat(cached_data['cached_at'])
            if datetime.now() - cached_time < self.cache_duration:
                return cached_data
        except Exception as e:
            print(f"   ⚠️  Cache read error: {e}")
        
        return None
    
    def _save_to_cache(self, cache_key: str, result: Dict):
        """Save results to cache"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'cache_key': cache_key,
            'results': result
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"   ⚠️  Cache write error: {e}")
