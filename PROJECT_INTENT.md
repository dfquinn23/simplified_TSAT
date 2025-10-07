# Tech Stack Audit Tool - Project Intent

**Document Version:** 1.0  
**Date:** October 6, 2025  
**Status:** Active - Single Source of Truth

---

## Purpose of This Document

This document defines the **core intent** of this project. Before adding any feature, changing architecture, or introducing complexity, **read this document first**. If a proposed change doesn't serve this intent, don't build it.

---

## The Business Problem

As a technology consultant for financial advisory firms, I am sometimes asked to audit a client's tech stack at the outset of a relationship. The audit needs to deliver:

1. **What they have** - Current software inventory
2. **What's new** - Updates/features released in the last 2 years they might have missed
3. **What's possible** - Automation opportunities using tools like n8n
4. **What to do** - Actionable recommendations with implementation guidance

**Current state:** I make up the workflow as I go, leading to repeated steps and inefficiency.

**Desired state:** Automated tool that produces a client-ready audit report in < 30 minutes.

---

## Success Criteria

A successful audit tool:

✅ **Fast** - Complete audit in under 30 minutes  
✅ **Automated** - Minimal manual work required  
✅ **Accurate** - LLM-researched information, not stale databases  
✅ **Actionable** - Specific recommendations clients can implement  
✅ **Zero maintenance** - No quarterly database updates required  
✅ **Scalable** - Works for any software stack, not just financial services  
✅ **Client-ready** - Professional markdown report ready to deliver  

---

## Core Workflow (DO BUILD THIS)

```
CSV Input → Research Tools → Analyze Integrations → Generate Report
   ↓              ↓                    ↓                    ↓
Load tools   CrewAI finds      CrewAI identifies    Markdown report
from CSV     updates/APIs      opportunities        in /output
```

**That's it.** Single pass, no stages, no gates, no validation layers.

### Phase 1: Tool Research (Parallel)
- Load CSV with tool inventory
- For each tool, CrewAI agent researches:
  - Updates from last 2 years
  - New automation features
  - API capabilities
- Use existing registries where helpful (API endpoints)
- Return enriched tool data

### Phase 2: Integration Analysis
- Single CrewAI agent analyzes complete stack
- Identifies cross-tool automation opportunities
- Focuses on open-source solutions (n8n)
- Considers APIs, data flows, manual processes
- Returns prioritized opportunities

### Phase 3: Report Generation
- Single CrewAI agent synthesizes findings
- Creates professional markdown report
- Includes: summary, updates, opportunities, roadmap
- Saves to /output folder
- Done.

---

## What to Build (Green Light)

### ✅ Core Features
- CSV loading and validation
- Parallel tool research using CrewAI
- Integration opportunity analysis
- Markdown report generation
- CLI interface for running audits

### ✅ Helpful Enhancements
- Progress indicators during research
- Caching to avoid re-researching same tools
- Better error handling and logging
- Research depth options (quick/medium/deep)
- Export formats (PDF from markdown)

### ✅ Quality Improvements
- More comprehensive tests
- Better prompt engineering for agents
- Improved report formatting
- Research quality validation

---

## What NOT to Build (Red Light)

### ❌ Complexity Anti-Patterns
- **Stage-gate systems** - Single pass is sufficient
- **State persistence** - Each audit is independent
- **Validation gates** - Trust the LLM agents
- **Manual databases** - Let CrewAI research automatically
- **Integration health checkers** - Can't check without API access
- **Gap analyzers** - Just ask LLM "what opportunities exist?"
- **Sophisticated orchestration** - Keep it simple

### ❌ Maintenance Traps
- **Quarterly database updates** - Defeats automation purpose
- **Hardcoded feature lists** - LLMs can research this
- **Tool-specific logic** - Keep it generic
- **Complex configuration** - Environment variables are enough

### ❌ Over-Engineering
- **Authentication systems** - Not needed for research
- **User management** - Single user (you)
- **Web UI** - CLI is sufficient (for now)
- **Database** - Files are fine
- **API server** - Direct execution works

---

## Decision Framework

Before adding anything, ask these questions:

### The "Why" Test
**Question:** Why are we adding this?  
**Answer must be:** "Because it directly solves [specific business problem from above]"  
**Red flag:** "Because it would be nice to have" or "Because the old system had it"

### The Maintenance Test
**Question:** Will this require manual updates or maintenance?  
**Answer must be:** "No, it's self-maintaining" or "Only code changes, no data updates"  
**Red flag:** "We'll update the database quarterly" or "We'll maintain the registry"

### The LLM Test
**Question:** Could an LLM agent do this automatically?  
**Answer must be:** "No, this requires human judgment" or "LLM can't access this"  
**Red flag:** "LLM could, but we'll do it manually for accuracy"

### The Explain Test
**Question:** Can you explain the system in 3 sentences to a non-technical person?  
**Answer must be:** Clear, simple explanation without jargon  
**Red flag:** Requires diagrams, stage definitions, or technical terminology

---

## Architecture Principles

### 1. Leverage LLM Strengths
- LLMs are excellent at research, synthesis, and writing
- Don't fight this with manual databases or validation layers
- Trust the agents to do their job

### 2. Single Pass, No Stages
- Load → Research → Analyze → Report
- No artificial barriers or validation gates
- Each phase has full context from previous phases

### 3. Open Source First
- Recommend n8n, not Zapier/Make
- Focus on tools clients can own
- No vendor lock-in

### 4. Zero Maintenance
- System researches fresh information every time
- No databases that require quarterly updates
- Code changes only, never data maintenance

### 5. Files Over Databases
- CSV input, markdown output
- JSON for structured data if needed
- No database server required

---

## Red Flags to Watch For

If you hear these phrases in a development session, **stop and reconsider**:

⚠️ "We should validate..."  
⚠️ "Let's add a stage for..."  
⚠️ "We need a database of..."  
⚠️ "This requires quarterly updates..."  
⚠️ "Let's build a sophisticated..."  
⚠️ "We should check if..."  
⚠️ "What if the LLM is wrong about..."  

**Response:** "Does this serve the original intent? Could we solve this differently?"

---

## Evolution Guidelines

### When to Add Complexity
**Only when:**
1. Current system provably cannot handle a real use case
2. Simpler solutions have been tried and failed
3. Added complexity directly serves core business need
4. No maintenance burden is introduced

**Document:**
```
Feature: [Name]
Why: [Specific business problem it solves]
Alternatives Considered: [List]
Maintenance Required: [None/Minimal/Describe]
Serves Core Intent: [Yes - explain how]
```

### When to Refactor
**Red flags that indicate need to simplify:**
- Can't explain the system in < 5 minutes
- New features take longer than 1 day
- Bug fixes require touching > 3 files
- Need documentation to remember how it works
- Tests are harder to write than features

**Response:** Return to this document, remove complexity

---

## Historical Context

### What Went Wrong Before (October 2025)
Through 5+ handoff sessions, the original simple intent evolved into:
- 4-stage pipeline with validation gates
- Manual feature database (22 features, 9 tools)
- Integration health checker generating dummy data
- Gap analyzer that couldn't analyze the dummy data
- Stage 1 finding 36 features that Stage 3 ignored
- 20+ files, complex orchestration, quarterly maintenance

**Root cause:** No single source of truth, feature creep, fighting LLM strengths

**This time:** This document exists to prevent that drift

---

## Conclusion

**Remember:**
- Simple is better than complex
- Automated is better than manual
- Research is better than databases
- LLMs are tools, not enemies
- Working is better than perfect

**When in doubt:**
- Re-read this document
- Ask: "Does this serve the core business need?"
- Choose simplicity

---

**This document is the north star. Follow it.**