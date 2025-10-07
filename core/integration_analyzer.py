"""
Integration Analyzer - CrewAI agent for identifying automation opportunities
Analyzes the complete tool stack to find cross-tool integration opportunities
"""

from typing import List, Dict, Any
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()


class IntegrationAnalyzer:
    """
    CrewAI-powered integration analyzer
    Identifies automation opportunities across the complete tool stack
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-5"),
            temperature=1  # GPT-5 only supports temperature=1
        )

    async def analyze_stack(
        self,
        enriched_tools: List[Dict[str, Any]],
        client_name: str
    ) -> List[Dict[str, Any]]:
        """
        Analyze complete tool stack for integration opportunities

        Args:
            enriched_tools: List of tools with research data
            client_name: Name of client

        Returns:
            List of integration opportunities with n8n workflow specs
        """

        # Create the integration analyst agent
        analyst = Agent(
            role="Integration Automation Specialist",
            goal=f"Identify high-value automation opportunities in {client_name}'s tech stack using open-source tools like n8n",
            backstory="""You are an expert at identifying workflow automation opportunities.
            You understand APIs, data flows, and integration patterns. You specialize in 
            n8n workflow automation and always recommend open-source solutions over proprietary 
            SaaS platforms. You focus on practical, implementable solutions that save time and 
            reduce manual work.""",
            llm=self.llm,
            verbose=True
        )

        # Prepare context for the agent
        context = self._prepare_context(enriched_tools, client_name)

        # Create analysis task
        analysis_task = Task(
            description=f"""Analyze {client_name}'s complete technology stack and identify automation opportunities.

CONTEXT:
{context}

YOUR TASK:
1. Identify cross-tool integration opportunities where data flows between systems
2. Find manual processes that could be automated with n8n workflows
3. Prioritize opportunities by ROI (time saved, error reduction, process improvement)
4. For each opportunity, specify:
   - Clear opportunity name
   - Tools involved
   - Current manual process
   - Proposed n8n workflow (be specific about nodes/triggers)
   - Estimated time savings (hours per week/month)
   - Implementation complexity (Low/Medium/High)
   - Prerequisites (API access, authentication, etc.)

REQUIREMENTS:
- Focus ONLY on open-source solutions (n8n, not Zapier/Make)
- Prioritize opportunities with APIs available
- Consider the tool updates discovered in research
- Be specific about n8n node types (HTTP Request, Webhook, Schedule Trigger, etc.)
- Provide realistic time savings estimates

Output format: Return a detailed analysis with at least 3-5 opportunities, ranked by priority.
""",
            agent=analyst,
            expected_output="A structured list of automation opportunities with n8n implementation details"
        )

        # Run the analysis
        crew = Crew(
            agents=[analyst],
            tasks=[analysis_task],
            verbose=True
        )

        result = crew.kickoff()

        # Parse the result into structured opportunities
        opportunities = self._parse_opportunities(result, enriched_tools)

        return opportunities

    def _prepare_context(
        self,
        enriched_tools: List[Dict[str, Any]],
        client_name: str
    ) -> str:
        """Prepare formatted context for the agent"""

        context_parts = [f"Client: {client_name}\n"]
        context_parts.append(f"Total tools in stack: {len(enriched_tools)}\n")
        context_parts.append("\nTOOL INVENTORY WITH RECENT UPDATES:\n")
        context_parts.append("=" * 60 + "\n")

        for tool in enriched_tools:
            context_parts.append(f"\n{tool['name']}")
            context_parts.append(f"\n  Category: {tool['category']}")
            context_parts.append(f"\n  Type: {tool['type']}")
            context_parts.append(f"\n  Used by: {', '.join(tool['users'])}")
            context_parts.append(f"\n  Criticality: {tool['criticality']}")

            # Add research findings
            research = tool.get('research_result', {})
            if research.get('success'):
                context_parts.append(
                    f"\n  Updates found: {len(tool.get('analyzed_updates', []))}")

                # Add key automation features
                updates = tool.get('analyzed_updates', [])
                automation_updates = [
                    u for u in updates
                    if u.get('automation_potential', 'low') in ['high', 'medium']
                ]

                if automation_updates:
                    context_parts.append(f"\n  Key automation features:")
                    for update in automation_updates[:3]:  # Top 3
                        context_parts.append(
                            f"\n    - {update.get('feature_name', 'Unknown')}")
                        context_parts.append(
                            f"\n      Value: {update.get('automation_value', 'N/A')}")

                # Add API info
                if research.get('has_api'):
                    context_parts.append(
                        f"\n  ✅ API Available: {research.get('api_type', 'REST')}")
                else:
                    context_parts.append(f"\n  ⚠️  API status unknown")
            else:
                context_parts.append(
                    f"\n  Research incomplete: {research.get('error', 'Unknown')}")

            context_parts.append("\n" + "-" * 60)

        return "".join(context_parts)

    def _parse_opportunities(
        self,
        crew_result: Any,
        enriched_tools: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Parse CrewAI result into structured opportunities

        Note: This is a simple parser. In production, you might want
        to ask the agent to output JSON for easier parsing.
        """

        # For now, extract the raw text output
        result_text = str(crew_result)

        # Create a structured summary
        # This is simplified - you may want to enhance parsing
        opportunities = [{
            'raw_analysis': result_text,
            'tool_count': len(enriched_tools),
            'tools_analyzed': [t['name'] for t in enriched_tools]
        }]

        # TODO: Enhanced parsing to extract individual opportunities
        # For now, the report writer will work with the raw analysis

        return opportunities


def analyze_integration_opportunities(
    enriched_tools: List[Dict[str, Any]],
    client_name: str
) -> List[Dict[str, Any]]:
    """
    Convenience function for integration analysis
    Can be called synchronously
    """
    import asyncio

    analyzer = IntegrationAnalyzer()

    # Run async function in sync context
    if asyncio.get_event_loop().is_running():
        # Already in async context
        return asyncio.create_task(analyzer.analyze_stack(enriched_tools, client_name))
    else:
        # Create new event loop
        return asyncio.run(analyzer.analyze_stack(enriched_tools, client_name))
