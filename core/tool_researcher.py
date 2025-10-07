# core/software_update_researcher.py
"""
Software Update Researcher
Automatically researches software updates and new features using API endpoints and web scraping
"""

import asyncio
import aiohttp
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
import json
import re
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI

# Import the API registry
from core.api_changelog_registry import APIChangelogRegistry


class SoftwareUpdateResearchAgent:
    """
    Research agent that discovers software updates and new features
    Uses API endpoints when available, falls back to web scraping
    """
    
    def __init__(self, llm_model: str = "gpt-4", cache_duration_days: int = 30):
        self.api_registry = APIChangelogRegistry()
        self.cache_dir = Path("data/research_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_duration = timedelta(days=cache_duration_days)
        self.llm = ChatOpenAI(model=llm_model, temperature=0.3)
        
        # Initialize CrewAI agent
        self.research_agent = self._create_research_agent()
    
    def _create_research_agent(self) -> Agent:
        """Create the CrewAI research agent"""
        return Agent(
            role='Software Update Research Specialist',
            goal='Discover recent product enhancements and automation features for business software',
            backstory='''You are an expert at researching software updates, particularly for 
            financial services and business tools. You excel at finding new API capabilities, 
            workflow automation features, and integration enhancements from vendor release notes, 
            press releases, and product announcements. You focus on features that provide 
            automation value and can save users time.''',
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def _load_cache(self, tool_name: str, date_range: tuple) -> Optional[Dict]:
        """Load cached research results"""
        cache_key = f"{tool_name.lower().replace(' ', '_')}_{date_range[0]}_{date_range[1]}"
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    cached_time = datetime.fromisoformat(data.get('cached_at', '1970-01-01'))
                    if datetime.now() - cached_time < self.cache_duration:
                        print(f"📋 Using cached research for {tool_name}")
                        return data.get('results')
            except Exception as e:
                print(f"⚠️ Cache load error: {e}")
        return None
    
    def _save_cache(self, tool_name: str, date_range: tuple, results: Dict) -> None:
        """Save research results to cache"""
        cache_key = f"{tool_name.lower().replace(' ', '_')}_{date_range[0]}_{date_range[1]}"
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'cached_at': datetime.now().isoformat(),
                    'tool_name': tool_name,
                    'date_range': date_range,
                    'results': results
                }, f, indent=2)
        except Exception as e:
            print(f"⚠️ Cache save error: {e}")
    
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
        
        # Step 2: Web scraping research
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
            # For demonstration - actual implementation would make real API calls
            # This is where you'd implement specific logic for each API format
            
            if endpoint_info['auth_required']:
                # Check if we have credentials
                # In production, you'd get this from environment variables
                print(f"   ⚠️ API requires authentication - check .env for credentials")
                return {
                    'success': False,
                    'error': 'Authentication required but credentials not configured',
                    'needs_setup': True
                }
            
            # Placeholder for actual API call logic
            # Each API would need custom implementation
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
        """Research using web scraping via CrewAI agent"""
        
        # Define the research task
        research_task = Task(
            description=f'''Research software updates and new features for {tool_name}.
            
            Tool Information:
            - Tool Name: {tool_name}
            - Tool Type: {tool_type}
            - Date Range: {start_date} to {end_date}
            
            Your task:
            1. Search for "{tool_name} product updates {start_date.split('-')[0]}-{end_date.split('-')[0]}"
            2. Search for "{tool_name} new features automation API"
            3. Search for "{tool_name} press releases enhancements"
            
            Focus on finding:
            - New API capabilities and endpoints
            - Workflow automation features
            - Integration enhancements
            - Features that save time or reduce manual work
            
            For each update found, extract:
            - Feature/update name
            - Release date (if available)
            - Description of what it does
            - Automation potential (how it could save time/work)
            
            Format your findings as a structured list.
            ''',
            agent=self.research_agent,
            expected_output=f'''A structured list of updates for {tool_name} including:
            - Update name
            - Release date
            - Description
            - Automation value'''
        )
        
        # Create crew and execute
        crew = Crew(
            agents=[self.research_agent],
            tasks=[research_task],
            verbose=True
        )
        
        try:
            # Execute the research
            print(f"   🤖 Agent researching {tool_name}...")
            research_output = crew.kickoff()
            
            # Parse the agent's output and structure it
            structured_updates = self._parse_agent_output(
                research_output, 
                tool_name, 
                tool_type,
                start_date,
                end_date
            )
            
            return {
                'success': True,
                'source': 'web_research',
                'tool_name': tool_name,
                'tool_type': tool_type,
                'date_range': f"{start_date} to {end_date}",
                'research_depth': research_depth,
                'updates': structured_updates,
                'raw_output': str(research_output),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"   ❌ Research failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'tool_name': tool_name
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
        Parse the agent's output and create structured update records
        Uses AI to generate business impact descriptions
        """
        # Convert agent output to string
        output_text = str(agent_output)
        
        # Create a task to structure and enhance the findings
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
        
        try:
            analysis_output = crew.kickoff()
            
            # Try to parse as JSON
            try:
                updates = json.loads(str(analysis_output))
                if isinstance(updates, list):
                    return updates
            except:
                # If not valid JSON, create a simple structure
                pass
            
            # Fallback: Create basic structure
            return [{
                'feature_name': f'{tool_name} Updates',
                'release_date': f'{start_date} to {end_date}',
                'description': output_text[:500] + '...' if len(output_text) > 500 else output_text,
                'automation_value': 'Potential for workflow automation improvements',
                'business_impact': 'Review findings to identify specific automation opportunities',
                'implementation_difficulty': 'medium',
                'note': 'Manual review recommended for detailed analysis'
            }]
            
        except Exception as e:
            print(f"   ⚠️ Analysis parsing error: {e}")
            return []
    
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
