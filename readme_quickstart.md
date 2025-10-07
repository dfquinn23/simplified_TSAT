# Tech Stack Audit Tool - Simplified Edition

**Single-pass workflow:** CSV → Research → Analyze → Report in ~30 minutes

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file:
```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4
```

### 3. Run Tests
```bash
python tests/test_simple_audit.py
```

This will run 5 tests:
- ✅ CSV loading
- ✅ Quick research (2 tools)
- ✅ Integration analysis
- ✅ Report generation
- ✅ Complete workflow (3 tools)

### 4. Run Your First Audit
```bash
python simple_audit.py data/cga_real_tools.csv "Client Name"
```

**Options:**
```bash
# Custom research window (default: 2 years)
python simple_audit.py data/tools.csv "Client" --years 3

# Research depth (quick/medium/deep, default: medium)
python simple_audit.py data/tools.csv "Client" --depth deep
```

## CSV Format

Your CSV must have these columns:
- **Tool Name** (required)
- **Category** (required)
- **Used By** (required)
- **Criticality** (required)

Example:
```csv
Tool Name,Category,Used By,Criticality
Redtail CRM,CRM,Advisors,High
Orion,Portfolio Management,Portfolio Team,High
Microsoft 365,Productivity,All,High
```

## How It Works

### Phase 1: Tool Research (Parallel)
- Loads CSV with tool inventory
- Researches each tool independently using CrewAI
- Finds updates from last 2 years
- Identifies automation features and API capabilities
- Uses: `tool_researcher.py`, `api_changelog_registry.py`, `feature_analyzer.py`

### Phase 2: Integration Analysis
- Analyzes complete tool stack holistically
- Identifies cross-tool automation opportunities
- Focuses on n8n workflow possibilities
- Considers data flows and API availability
- Uses: `integration_analyzer.py`

### Phase 3: Report Generation
- Synthesizes findings into client-ready markdown
- Includes executive summary, tool updates, opportunities
- Prioritizes by ROI and implementation complexity
- Provides phased implementation roadmap
- Uses: `report_writer.py`

## Project Structure

```
tech_stack_audit_tool/
├── simple_audit.py              # Main entry point
├── requirements.txt             # Dependencies
├── .env                         # API keys (create this)
├── core/
│   ├── csv_loader.py            # CSV loading
│   ├── tool_researcher.py       # Tool research agent
│   ├── integration_analyzer.py  # Integration analysis agent
│   ├── report_writer.py         # Report generation agent
│   ├── api_changelog_registry.py # API endpoints database
│   └── feature_analyzer.py      # Update categorization
├── data/
│   ├── cga_real_tools.csv       # Sample data
│   └── tech_stack_list-CGA-Test.csv # Sample data
├── output/
│   └── *.md                     # Generated reports
└── tests/
    └── test_simple_audit.py     # Test suite
```

## Architecture Principles

### ✅ What This System Does Right
- **No stage gates** - Single workflow pass, no artificial barriers
- **No manual databases** - CrewAI researches everything automatically
- **No dummy data** - If we can't check it, we don't generate fake results
- **Full context** - Integration analyzer sees all research at once
- **Parallel research** - All tools researched simultaneously
- **Open source focus** - n8n recommendations, not SaaS platforms

### ✅ What We Kept from Old System
- Working CrewAI research engine (5/5 tests passing)
- API registry (20 tools with known endpoints)
- Feature analyzer (proven update categorization)
- CSV format (clients already use this)

### ✅ What We Removed
- Stage-gate architecture (added complexity without value)
- Manual feature database (required quarterly maintenance)
- Integration health checker (generated dummy data)
- Gap analyzer (couldn't analyze dummy data)
- Disconnected opportunity engine (ignored discovered features)

## Troubleshooting

**"No module named 'crewai'"**
- Run: `pip install -r requirements.txt`

**"OpenAI API key not found"**
- Create `.env` file with `OPENAI_API_KEY=your_key`

**"CSV file not found"**
- Check CSV path and ensure columns match required format

**Tests fail with API errors**
- Verify OpenAI API key is valid
- Check you have sufficient API credits

## Output

Reports are saved to `output/audit_ClientName_TIMESTAMP.md`

Example structure:
- Executive Summary
- Tools Analyzed (with updates)
- Integration Opportunities (prioritized)
- Quick Wins
- Implementation Roadmap
- Next Steps

## Support

For issues or questions, review:
1. Test output: `python tests/test_simple_audit.py`
2. Sample CSVs in `data/` folder
3. Generated reports in `output/` folder
