"""
Report Writer - CrewAI agent for generating client-ready markdown reports
Synthesizes research findings and opportunities into a professional deliverable
"""

from typing import List, Dict, Any
from datetime import datetime
from pathlib import Path
from crewai import Agent, Task, Crew
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()


class ReportWriter:
    """
    CrewAI-powered report writer
    Generates professional markdown reports for clients
    """

    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-5"),
            temperature=1  # GPT-5 only supports temperature=1
        )
        self.output_dir = Path("output")
        self.output_dir.mkdir(exist_ok=True)

    async def generate_report(
        self,
        enriched_tools: List[Dict[str, Any]],
        opportunities: List[Dict[str, Any]],
        client_name: str
    ) -> str:
        """
        Generate client-ready markdown report

        Args:
            enriched_tools: List of tools with research data
            opportunities: List of integration opportunities
            client_name: Name of client

        Returns:
            Path to generated report file
        """

        # Create the report writer agent
        writer = Agent(
            role="Technology Consulting Report Writer",
            goal=f"Create a professional, actionable tech stack audit report for {client_name}",
            backstory="""You are an experienced technology consultant who writes clear, 
            actionable reports for business clients. You excel at translating technical 
            findings into business value. Your reports are well-structured, easy to scan, 
            and focused on ROI and implementation guidance. You always highlight quick wins 
            and provide specific next steps.""",
            llm=self.llm,
            verbose=True
        )

        # Prepare context
        context = self._prepare_report_context(
            enriched_tools,
            opportunities,
            client_name
        )

        # Create report writing task
        report_task = Task(
            description=f"""Create a comprehensive tech stack audit report for {client_name}.

CONTEXT:
{context}

REPORT STRUCTURE REQUIRED:

# Tech Stack Audit Report: {client_name}

## Executive Summary
- Brief overview of audit scope
- Total tools analyzed
- Key findings (2-3 sentences)
- Total opportunities identified
- Estimated total time savings

## Tools Analyzed

For each tool, include:
- Tool name and category
- Recent updates discovered (if any)
- Key automation features added
- Current utilization assessment

## Integration Opportunities

Prioritized list of automation opportunities:
- Opportunity name
- Tools involved
- Current manual process
- Proposed n8n workflow
- Time savings estimate
- Implementation complexity
- Priority ranking (High/Medium/Low)

## Quick Wins

Identify 2-3 opportunities that can be implemented quickly (< 1 week) for immediate ROI.

## Implementation Roadmap

Phased approach:
- Phase 1: Quick wins (Weeks 1-2)
- Phase 2: Medium complexity (Weeks 3-6)
- Phase 3: Advanced integrations (Weeks 7-12)

## Next Steps

Specific action items with owners and timelines.

REQUIREMENTS:
- Use markdown formatting
- Keep language professional but accessible
- Focus on business value, not just features
- Be specific about time savings and ROI
- Include implementation complexity for each opportunity
- Prioritize open-source solutions (n8n)

Write the complete report now.
""",
            agent=writer,
            expected_output="A complete markdown report ready for client delivery"
        )

        # Run report generation
        crew = Crew(
            agents=[writer],
            tasks=[report_task],
            verbose=True
        )

        result = crew.kickoff()

        # Save report to file
        report_path = self._save_report(result, client_name)

        return str(report_path)

    def _prepare_report_context(
        self,
        enriched_tools: List[Dict[str, Any]],
        opportunities: List[Dict[str, Any]],
        client_name: str
    ) -> str:
        """Prepare formatted context for report generation"""

        context_parts = [f"CLIENT: {client_name}\n"]
        context_parts.append(
            f"AUDIT DATE: {datetime.now().strftime('%B %d, %Y')}\n")
        context_parts.append(f"TOTAL TOOLS: {len(enriched_tools)}\n\n")

        # Tool details
        context_parts.append("TOOL INVENTORY WITH FINDINGS:\n")
        context_parts.append("=" * 70 + "\n\n")

        for tool in enriched_tools:
            context_parts.append(f"Tool: {tool['name']}\n")
            context_parts.append(f"Category: {tool['category']}\n")
            context_parts.append(f"Criticality: {tool['criticality']}\n")
            context_parts.append(f"Users: {', '.join(tool['users'])}\n")

            research = tool.get('research_result', {})
            if research.get('success'):
                updates = tool.get('analyzed_updates', [])
                context_parts.append(f"Updates Found: {len(updates)}\n")

                if updates:
                    context_parts.append("Recent Updates:\n")
                    for update in updates[:5]:  # Top 5
                        context_parts.append(
                            f"  - {update.get('feature_name', 'Unknown')}\n")
                        context_parts.append(
                            f"    Category: {update.get('update_category', 'N/A')}\n")
                        context_parts.append(
                            f"    Automation Potential: {update.get('automation_potential', 'Unknown')}\n")
                        if update.get('business_impact'):
                            context_parts.append(
                                f"    Impact: {update['business_impact']}\n")
            else:
                context_parts.append(
                    f"Research Status: {research.get('error', 'No updates found')}\n")

            context_parts.append("\n" + "-" * 70 + "\n\n")

        # Integration opportunities
        context_parts.append("\nINTEGRATION OPPORTUNITIES ANALYSIS:\n")
        context_parts.append("=" * 70 + "\n\n")

        for opp in opportunities:
            if 'raw_analysis' in opp:
                context_parts.append(opp['raw_analysis'])
                context_parts.append("\n\n")

        return "".join(context_parts)

    def _save_report(self, crew_result: Any, client_name: str) -> Path:
        """Save report to markdown file"""

        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_client_name = client_name.replace(" ", "_").replace("/", "_")
        filename = f"audit_{safe_client_name}_{timestamp}.md"

        report_path = self.output_dir / filename

        # Extract report text
        report_content = str(crew_result)

        # Ensure proper markdown formatting
        if not report_content.startswith("#"):
            # Add header if agent didn't include it
            header = f"# Tech Stack Audit Report: {client_name}\n\n"
            header += f"**Generated:** {datetime.now().strftime('%B %d, %Y at %I:%M %p')}\n\n"
            header += "---\n\n"
            report_content = header + report_content

        # Write to file
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"📄 Report saved: {report_path}")

        return report_path


def generate_markdown_report(
    enriched_tools: List[Dict[str, Any]],
    opportunities: List[Dict[str, Any]],
    client_name: str
) -> str:
    """
    Convenience function for report generation
    Can be called synchronously
    """
    import asyncio

    writer = ReportWriter()

    # Run async function in sync context
    if asyncio.get_event_loop().is_running():
        # Already in async context
        return asyncio.create_task(
            writer.generate_report(enriched_tools, opportunities, client_name)
        )
    else:
        # Create new event loop
        return asyncio.run(
            writer.generate_report(enriched_tools, opportunities, client_name)
        )
