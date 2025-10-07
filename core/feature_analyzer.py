# core/feature_analyzer.py
"""
Feature Analyzer - Analyzes discovered updates for automation potential and business impact
"""

from typing import Dict, List, Any
from datetime import datetime
import json
from pathlib import Path


class FeatureAnalyzer:
    """
    Analyzes discovered software updates and categorizes them by:
    - Automation potential (high/medium/low)
    - Implementation difficulty (quick/medium/complex)
    - Business impact (time savings, cost reduction)
    """
    
    def __init__(self):
        self.automation_keywords = {
            'high': [
                'api', 'automation', 'workflow', 'integration', 'automated',
                'connector', 'webhook', 'sync', 'real-time', 'batch process',
                'scheduled', 'trigger', 'export', 'import', 'bulk'
            ],
            'medium': [
                'enhancement', 'improved', 'streamlined', 'simplified',
                'faster', 'optimization', 'upgrade', 'update'
            ]
        }
        
        self.tool_type_priorities = {
            'crm': ['data entry', 'client communication', 'reporting'],
            'portfolio_management': ['rebalancing', 'reporting', 'data feeds'],
            'research_platform': ['data extraction', 'alerts', 'exports'],
            'custodial': ['account opening', 'reconciliation', 'trading'],
            'financial_planning': ['plan generation', 'client reports', 'updates'],
            'productivity_suite': ['workflow automation', 'integration', 'templates'],
            'communication': ['scheduling', 'recording', 'integration'],
            'operations': ['document processing', 'approval workflows', 'notifications']
        }
    
    def analyze_update(self, update: Dict, tool_type: str) -> Dict[str, Any]:
        """
        Analyze a single update for automation potential
        
        Args:
            update: Dictionary with update information
            tool_type: Type of tool (e.g., 'crm', 'portfolio_management')
            
        Returns:
            Enhanced update dictionary with analysis
        """
        feature_name = update.get('feature_name', '')
        description = update.get('description', '')
        automation_value = update.get('automation_value', '')
        
        # Combine text for analysis
        full_text = f"{feature_name} {description} {automation_value}".lower()
        
        # Calculate automation potential score
        automation_score = self._calculate_automation_score(full_text, tool_type)
        
        # Estimate time savings
        time_savings = self._estimate_time_savings(full_text, tool_type)
        
        # Determine implementation priority
        priority = self._determine_priority(
            automation_score, 
            time_savings, 
            update.get('implementation_difficulty', 'medium')
        )
        
        # Add analysis to update
        update['analysis'] = {
            'automation_potential': self._score_to_level(automation_score),
            'automation_score': automation_score,
            'estimated_time_savings': time_savings,
            'priority': priority,
            'tool_type_relevance': self._check_tool_type_relevance(full_text, tool_type),
            'analyzed_at': datetime.now().isoformat()
        }
        
        return update
    
    def _calculate_automation_score(self, text: str, tool_type: str) -> int:
        """Calculate automation potential score (0-100)"""
        score = 0
        
        # Check for high-value automation keywords
        for keyword in self.automation_keywords['high']:
            if keyword in text:
                score += 15
        
        # Check for medium-value keywords
        for keyword in self.automation_keywords['medium']:
            if keyword in text:
                score += 5
        
        # Boost score based on tool type priorities
        priorities = self.tool_type_priorities.get(tool_type, [])
        for priority_area in priorities:
            if priority_area in text:
                score += 10
        
        # Cap at 100
        return min(score, 100)
    
    def _estimate_time_savings(self, text: str, tool_type: str) -> str:
        """Estimate potential time savings"""
        score = 0
        
        # High-impact indicators
        if any(word in text for word in ['automate', 'eliminate', 'automated']):
            score += 30
        
        if any(word in text for word in ['manual', 'repetitive', 'daily']):
            score += 20
        
        if any(word in text for word in ['integration', 'api', 'sync']):
            score += 15
        
        # Tool-type specific estimates
        if tool_type in ['crm', 'portfolio_management']:
            score += 10
        
        # Return estimate range
        if score >= 50:
            return "10-20 hours/week"
        elif score >= 30:
            return "5-10 hours/week"
        elif score >= 15:
            return "2-5 hours/week"
        else:
            return "1-2 hours/week"
    
    def _determine_priority(
        self, 
        automation_score: int, 
        time_savings: str,
        implementation_difficulty: str
    ) -> str:
        """Determine implementation priority"""
        # High automation score + reasonable difficulty = high priority
        if automation_score >= 60 and implementation_difficulty in ['quick', 'medium']:
            return "high"
        
        # Good score or high time savings = medium priority
        if automation_score >= 40 or 'hours/week' in time_savings:
            return "medium"
        
        return "low"
    
    def _check_tool_type_relevance(self, text: str, tool_type: str) -> str:
        """Check how relevant the update is to the tool type's core functions"""
        priorities = self.tool_type_priorities.get(tool_type, [])
        
        matches = sum(1 for priority in priorities if priority in text)
        
        if matches >= 2:
            return "high"
        elif matches >= 1:
            return "medium"
        else:
            return "low"
    
    def _score_to_level(self, score: int) -> str:
        """Convert numeric score to level"""
        if score >= 60:
            return "high"
        elif score >= 30:
            return "medium"
        else:
            return "low"
    
    def analyze_tool_updates(
        self, 
        tool_name: str, 
        updates: List[Dict], 
        tool_type: str
    ) -> Dict[str, Any]:
        """
        Analyze all updates for a tool
        
        Returns:
            Summary with categorized updates
        """
        if not updates:
            return {
                'tool_name': tool_name,
                'tool_type': tool_type,
                'total_updates': 0,
                'high_priority': [],
                'medium_priority': [],
                'low_priority': [],
                'summary': f"No updates found for {tool_name}"
            }
        
        # Analyze each update
        analyzed_updates = [
            self.analyze_update(update, tool_type) 
            for update in updates
        ]
        
        # Categorize by priority
        high_priority = [u for u in analyzed_updates if u['analysis']['priority'] == 'high']
        medium_priority = [u for u in analyzed_updates if u['analysis']['priority'] == 'medium']
        low_priority = [u for u in analyzed_updates if u['analysis']['priority'] == 'low']
        
        # Calculate total potential impact
        total_impact = self._calculate_total_impact(analyzed_updates)
        
        return {
            'tool_name': tool_name,
            'tool_type': tool_type,
            'total_updates': len(analyzed_updates),
            'high_priority': high_priority,
            'medium_priority': medium_priority,
            'low_priority': low_priority,
            'total_potential_impact': total_impact,
            'summary': self._generate_summary(tool_name, analyzed_updates, total_impact),
            'analyzed_at': datetime.now().isoformat()
        }
    
    def _calculate_total_impact(self, updates: List[Dict]) -> Dict[str, Any]:
        """Calculate total potential impact across all updates"""
        high_count = len([u for u in updates if u['analysis']['automation_potential'] == 'high'])
        medium_count = len([u for u in updates if u['analysis']['automation_potential'] == 'medium'])
        
        # Rough time savings estimate
        estimated_hours_per_week = (high_count * 15) + (medium_count * 5)
        
        return {
            'high_automation_features': high_count,
            'medium_automation_features': medium_count,
            'estimated_hours_saved_per_week': estimated_hours_per_week,
            'estimated_annual_value': estimated_hours_per_week * 52 * 100  # $100/hour assumption
        }
    
    def _generate_summary(
        self, 
        tool_name: str, 
        updates: List[Dict], 
        impact: Dict
    ) -> str:
        """Generate executive summary"""
        high_count = impact['high_automation_features']
        hours = impact['estimated_hours_saved_per_week']
        
        if high_count >= 3:
            return f"{tool_name} has {high_count} high-value automation features that could save approximately {hours} hours/week"
        elif high_count >= 1:
            return f"{tool_name} has {high_count} high-value automation feature(s) worth implementing"
        else:
            return f"{tool_name} has {len(updates)} update(s) with moderate automation potential"
    
    def create_implementation_roadmap(
        self, 
        analyzed_tools: List[Dict]
    ) -> Dict[str, Any]:
        """
        Create an implementation roadmap across all tools
        
        Args:
            analyzed_tools: List of analyzed tool results
            
        Returns:
            Prioritized roadmap
        """
        # Collect all high-priority items
        quick_wins = []
        medium_term = []
        long_term = []
        
        for tool_analysis in analyzed_tools:
            tool_name = tool_analysis['tool_name']
            
            for update in tool_analysis.get('high_priority', []):
                difficulty = update.get('implementation_difficulty', 'medium')
                item = {
                    'tool': tool_name,
                    'feature': update['feature_name'],
                    'impact': update['analysis']['estimated_time_savings'],
                    'difficulty': difficulty
                }
                
                if difficulty == 'quick':
                    quick_wins.append(item)
                elif difficulty == 'medium':
                    medium_term.append(item)
                else:
                    long_term.append(item)
        
        # Calculate totals
        total_features = len(quick_wins) + len(medium_term) + len(long_term)
        total_tools_with_opportunities = len([t for t in analyzed_tools if t['total_updates'] > 0])
        
        return {
            'total_opportunities': total_features,
            'tools_with_opportunities': total_tools_with_opportunities,
            'quick_wins': {
                'count': len(quick_wins),
                'items': quick_wins,
                'recommendation': 'Implement in next 30 days'
            },
            'medium_term': {
                'count': len(medium_term),
                'items': medium_term,
                'recommendation': 'Implement in 30-90 days'
            },
            'long_term': {
                'count': len(long_term),
                'items': long_term,
                'recommendation': 'Plan for 90+ days'
            },
            'executive_summary': self._generate_roadmap_summary(
                quick_wins, medium_term, long_term, total_tools_with_opportunities
            )
        }
    
    def _generate_roadmap_summary(
        self, 
        quick_wins: List, 
        medium_term: List, 
        long_term: List,
        total_tools: int
    ) -> str:
        """Generate executive summary for roadmap"""
        total = len(quick_wins) + len(medium_term) + len(long_term)
        
        summary = f"Identified {total} automation opportunities across {total_tools} tools. "
        
        if quick_wins:
            summary += f"{len(quick_wins)} quick wins can be implemented in the next 30 days for immediate impact. "
        
        if medium_term:
            summary += f"{len(medium_term)} medium-complexity features should be prioritized for 30-90 day implementation. "
        
        return summary


# Convenience function
def analyze_research_results(research_results: Dict) -> Dict[str, Any]:
    """Analyze research results from the Research Agent"""
    analyzer = FeatureAnalyzer()
    
    analyzed_tools = []
    
    for tool_name, research_data in research_results.get('results', {}).items():
        if not research_data.get('success'):
            continue
        
        updates = research_data.get('updates', [])
        tool_type = research_data.get('tool_type', 'unknown')
        
        analysis = analyzer.analyze_tool_updates(tool_name, updates, tool_type)
        analyzed_tools.append(analysis)
    
    # Create implementation roadmap
    roadmap = analyzer.create_implementation_roadmap(analyzed_tools)
    
    return {
        'analyzed_tools': analyzed_tools,
        'implementation_roadmap': roadmap,
        'timestamp': datetime.now().isoformat()
    }


# Example usage
if __name__ == "__main__":
    # Example update data
    sample_update = {
        'feature_name': 'Power Automate Premium Connectors',
        'release_date': '2024-Q2',
        'description': 'New premium connectors for Excel, SharePoint, and custom APIs enabling automated data flows',
        'automation_value': 'Eliminate manual data entry between systems',
        'business_impact': 'Save 10-15 hours per week on data transfer tasks',
        'implementation_difficulty': 'medium'
    }
    
    analyzer = FeatureAnalyzer()
    analyzed = analyzer.analyze_update(sample_update, 'productivity_suite')
    
    print("📊 Feature Analysis Example:")
    print(json.dumps(analyzed, indent=2))
