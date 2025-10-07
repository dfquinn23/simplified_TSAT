#!/usr/bin/env python3
"""
Tech Stack Audit Tool - Main Entry Point
Simple single-pass workflow: CSV → Research → Analyze → Report
"""

import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import sys

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.csv_loader import load_input, convert_df_to_tool_inventory
from core.tool_researcher import SoftwareUpdateResearchAgent
from core.integration_analyzer import IntegrationAnalyzer
from core.report_writer import ReportWriter
from core.feature_analyzer import FeatureAnalyzer


class TechStackAudit:
    """
    Main audit orchestrator
    Runs complete workflow from CSV to final report
    """
    
    def __init__(self, research_window_years: int = 2):
        self.research_window_years = research_window_years
        self.research_agent = SoftwareUpdateResearchAgent()
        self.feature_analyzer = FeatureAnalyzer()
        self.integration_analyzer = IntegrationAnalyzer()
        self.report_writer = ReportWriter()
        
    def _calculate_date_window(self) -> tuple[str, str]:
        """Calculate start and end dates for research"""
        end_date = datetime.now()
        start_date = datetime(
            end_date.year - self.research_window_years,
            end_date.month,
            end_date.day
        )
        return start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")
    
    async def run_audit(
        self, 
        csv_path: str, 
        client_name: str,
        research_depth: str = "medium"
    ) -> str:
        """
        Complete audit workflow
        
        Args:
            csv_path: Path to CSV file with tool inventory
            client_name: Name of client for report
            research_depth: 'quick', 'medium', or 'deep'
            
        Returns:
            Path to generated report file
        """
        print("\n" + "="*60)
        print("🚀 TECH STACK AUDIT - Starting")
        print("="*60)
        print(f"   Client: {client_name}")
        print(f"   Research window: {self.research_window_years} years")
        print(f"   Research depth: {research_depth}")
        print("="*60 + "\n")
        
        # PHASE 1: Load CSV and research all tools
        print("\n" + "="*60)
        print("📋 PHASE 1: TOOL RESEARCH")
        print("="*60)
        
        enriched_tools = await self._research_phase(csv_path, research_depth)
        
        print(f"\n✅ Phase 1 complete: {len(enriched_tools)} tools researched\n")
        
        # PHASE 2: Analyze integration opportunities
        print("\n" + "="*60)
        print("🔗 PHASE 2: INTEGRATION ANALYSIS")
        print("="*60)
        
        opportunities = await self._integration_phase(enriched_tools, client_name)
        
        print(f"\n✅ Phase 2 complete: {len(opportunities)} opportunities identified\n")
        
        # PHASE 3: Generate report
        print("\n" + "="*60)
        print("📄 PHASE 3: REPORT GENERATION")
        print("="*60)
        
        report_path = await self._report_phase(
            enriched_tools, 
            opportunities, 
            client_name
        )
        
        print(f"\n✅ Phase 3 complete: Report saved to {report_path}\n")
        
        # Final summary
        print("\n" + "="*60)
        print("🎉 AUDIT COMPLETE")
        print("="*60)
        print(f"   Tools analyzed: {len(enriched_tools)}")
        print(f"   Opportunities found: {len(opportunities)}")
        print(f"   Report location: {report_path}")
        print("="*60 + "\n")
        
        return report_path
    
    async def _research_phase(
        self, 
        csv_path: str, 
        research_depth: str
    ) -> List[Dict[str, Any]]:
        """
        Phase 1: Load CSV and research all tools in parallel
        """
        # Load tools from CSV
        print(f"📂 Loading tools from: {csv_path}")
        df = load_input(csv_path)
        tool_inventory = convert_df_to_tool_inventory(df)
        
        print(f"✅ Loaded {len(tool_inventory)} tools from CSV\n")
        
        # Convert to research format
        tools_to_research = []
        for tool_name, tool_data in tool_inventory.items():
            tools_to_research.append({
                'name': tool_name,
                'type': self._infer_tool_type(tool_data['category']),
                'category': tool_data['category'],
                'users': tool_data['users'],
                'criticality': tool_data['criticality']
            })
        
        # Calculate research window
        start_date, end_date = self._calculate_date_window()
        
        print(f"🔬 Researching updates from {start_date} to {end_date}\n")
        
        # Research all tools
        research_results = await self.research_agent.research_tool_stack(
            tools=tools_to_research,
            start_date=start_date,
            end_date=end_date,
            research_depth=research_depth
        )
        
        # Enhance with feature analysis
        enriched_tools = []
        for tool in tools_to_research:
            tool_name = tool['name']
            research_data = research_results.get(tool_name, {})
            
            # Analyze features if updates found
            analyzed_updates = []
            if research_data.get('success') and research_data.get('updates'):
                for update in research_data['updates']:
                    analyzed = self.feature_analyzer.analyze_update(
                        update, 
                        tool['type']
                    )
                    analyzed_updates.append(analyzed)
            
            enriched_tools.append({
                'name': tool_name,
                'type': tool['type'],
                'category': tool['category'],
                'users': tool['users'],
                'criticality': tool['criticality'],
                'research_result': research_data,
                'analyzed_updates': analyzed_updates,
                'update_count': len(analyzed_updates)
            })
        
        return enriched_tools
    
    async def _integration_phase(
        self, 
        enriched_tools: List[Dict[str, Any]], 
        client_name: str
    ) -> List[Dict[str, Any]]:
        """
        Phase 2: Analyze integration opportunities across full stack
        """
        print(f"🤖 Analyzing integration opportunities for {client_name}\n")
        
        opportunities = await self.integration_analyzer.analyze_stack(
            enriched_tools=enriched_tools,
            client_name=client_name
        )
        
        return opportunities
    
    async def _report_phase(
        self,
        enriched_tools: List[Dict[str, Any]],
        opportunities: List[Dict[str, Any]],
        client_name: str
    ) -> str:
        """
        Phase 3: Generate client-ready report
        """
        print(f"✍️  Generating report for {client_name}\n")
        
        report_path = await self.report_writer.generate_report(
            enriched_tools=enriched_tools,
            opportunities=opportunities,
            client_name=client_name
        )
        
        return report_path
    
    def _infer_tool_type(self, category: str) -> str:
        """Infer tool type from category"""
        category_lower = category.lower()
        
        if 'crm' in category_lower:
            return 'crm'
        elif 'portfolio' in category_lower:
            return 'portfolio_management'
        elif 'research' in category_lower:
            return 'research_platform'
        elif 'custod' in category_lower or 'trading' in category_lower:
            return 'custodial'
        elif 'planning' in category_lower:
            return 'financial_planning'
        elif 'communication' in category_lower or 'video' in category_lower:
            return 'communication'
        elif 'productivity' in category_lower or 'office' in category_lower:
            return 'productivity_suite'
        elif 'operation' in category_lower or 'accounting' in category_lower:
            return 'operations'
        elif 'compliance' in category_lower:
            return 'compliance'
        else:
            return 'unknown'


async def main():
    """
    CLI entry point for running audits
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Tech Stack Audit Tool - Automated software update research'
    )
    parser.add_argument(
        'csv_path',
        help='Path to CSV file with tool inventory'
    )
    parser.add_argument(
        'client_name',
        help='Client name for report'
    )
    parser.add_argument(
        '--years',
        type=int,
        default=2,
        help='Years of history to research (default: 2)'
    )
    parser.add_argument(
        '--depth',
        choices=['quick', 'medium', 'deep'],
        default='medium',
        help='Research depth (default: medium)'
    )
    
    args = parser.parse_args()
    
    # Validate CSV exists
    if not Path(args.csv_path).exists():
        print(f"❌ Error: CSV file not found: {args.csv_path}")
        return 1
    
    # Run audit
    audit = TechStackAudit(research_window_years=args.years)
    
    try:
        report_path = await audit.run_audit(
            csv_path=args.csv_path,
            client_name=args.client_name,
            research_depth=args.depth
        )
        
        print(f"\n✅ Success! Report available at: {report_path}")
        return 0
        
    except Exception as e:
        print(f"\n❌ Error during audit: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
