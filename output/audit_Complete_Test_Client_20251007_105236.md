# Tech Stack Audit Report: Complete Test Client

Audit Date: October 07, 2025

## Executive Summary
- Scope: Reviewed the research/data tooling used by Portfolio Management and identified high-ROI automation opportunities using open-source n8n workflows and lightweight data storage (Postgres/SQLite).
- Total tools analyzed: 3 (FactSet, Morningstar Direct, Bloomberg Terminal)
- Key findings: All three tools are mission-critical and currently leveraged via manual exports, terminal screens, and spreadsheets. No recent vendor updates were identified this period. Significant gains are available by standardizing identifiers, centralizing data via APIs/exports, and introducing scheduled n8n pipelines with alerting and audit logs.
- Total opportunities identified: 5 prioritized automations
- Estimated total time savings: 14–22 hours per week (≈0.35–0.55 FTE), equivalent to ~728–1,144 hours annually. At a conservative fully loaded cost of $100/hour, this yields $72.8k–$114.4k annual productivity ROI, plus risk/error reduction.

## Tools Analyzed

### FactSet (Category: Research)
- Recent updates discovered: None this audit period.
- Key automation features available:
  - Robust REST APIs: Symbology, Prices, Fundamentals, Corporate Actions, Estimates/Recommendations, Classifications.
  - OAuth2 authentication supported (works well with n8n HTTP Request nodes).
- Current utilization assessment:
  - High criticality. Data pulled ad hoc by PMs; exports and manual joins in Excel increase operational risk and cycle time.
  - Strong candidate for central API-driven data layer feeding analytics and alerts.

### Morningstar Direct (Category: Research)
- Recent updates discovered: None this audit period.
- Key automation features available:
  - Scheduled exports to SFTP or email (CSV/XLSX) commonly used for integration.
  - In some tenants, limited APIs may be available (to be confirmed); otherwise, rely on SFTP/email ingestion via n8n.
- Current utilization assessment:
  - High criticality. Portfolio holdings/exposures are exported and then manually combined with external data. Good source of portfolio truth for downstream pipelines.

### Bloomberg Terminal (Category: Research)
- Recent updates discovered: None this audit period.
- Key automation features available:
  - Terminal itself is not automatable. For automated data feeds, Bloomberg Data License (DL) via SFTP is required.
- Current utilization assessment:
  - High criticality for real-time research and checks. For process automation (e.g., corporate actions), rely on Bloomberg DL SFTP files combined with FactSet APIs for cross-validation.

## Integration Opportunities

1) Daily Master Data Sync for Portfolio Analytics
- Tools involved: Morningstar Direct (SFTP/email export), FactSet APIs (Symbology, Prices, Fundamentals), optional Postgres
- Current manual process:
  - PMs export Morningstar holdings and separately gather FactSet data, then copy/paste and transform in Excel to produce daily dashboards and review emails.
- Proposed n8n workflow:
  - Trigger: Weekdays 06:00 local
  - Ingest: SFTP/IMAP download of Morningstar holdings CSV/XLSX; parse to JSON
  - Standardize: OAuth2 to FactSet; resolve identifiers via Symbology; batch in 100s
  - Enrich: Fetch latest prices and fundamentals
  - Merge and validate: Join on standardized IDs; route missing mappings to remediation log
  - Persist: Upsert to Postgres (holdings_raw, prices, fundamentals, holdings_enriched)
  - Notify: Email success summary with snapshot and count of missing mappings; error trigger on failure
- Time savings estimate: 6–8 hours/week
- Implementation complexity: Medium
- Priority ranking: High
- Notes:
  - Prereqs: FactSet API entitlements/credentials; Morningstar scheduled export; DB credentials; network allowlists.

2) Corporate Actions Aggregator (Bloomberg DL + FactSet cross-check)
- Tools involved: Bloomberg Data License SFTP, FactSet Corporate Actions & Symbology APIs, optional Postgres
- Current manual process:
  - PMs check terminal screens and emails; reconcile with FactSet manually; risk of missed/incorrect events.
- Proposed n8n workflow:
  - Trigger: Daily 03:30 local (post Bloomberg DL run)
  - Ingest: SFTP list/download DL files; parse to normalized JSON
  - Standardize: Resolve IDs via FactSet Symbology
  - Enrich & validate: Query FactSet Corporate Actions for same universe/date window; deduplicate and flag discrepancies
  - Persist & notify: Upsert unified feed; email digest with unified events + discrepancy list
- Time savings estimate: 3–5 hours/week (plus high error reduction)
- Implementation complexity: Medium-High
- Priority ranking: High
- Notes:
  - Bloomberg Terminal alone is insufficient; requires Data License SFTP.

3) Research Signal Alerts
- Tools involved: FactSet Estimates/Recommendations API, Morningstar Direct ratings export, optional Postgres
- Current manual process:
  - Analysts/PMs periodically check both sources and compile internal emails manually.
- Proposed n8n workflow:
  - Trigger: Every 30 minutes (market hours) for FactSet; nightly for Morningstar ratings export
  - Ingest & query: FactSet recommendations/targets for watchlist; fetch Morningstar ratings CSV via SFTP/IMAP
  - Detect deltas: Compare to prior snapshot; threshold filter (e.g., target changes >5%)
  - Notify & persist: Email alerts with concise summaries and CSV; upsert snapshot for next comparison
- Time savings estimate: 2–4 hours/week; improved reaction time
- Implementation complexity: Medium
- Priority ranking: Medium

4) Data Coverage/Entitlement Watchdog
- Tools involved: Morningstar holdings export, FactSet Symbology + sample data endpoints, email
- Current manual process:
  - Coverage gaps discovered ad hoc, leading to reactive firefighting.
- Proposed n8n workflow:
  - Trigger: Weekly (e.g., Monday 07:00)
  - Ingest: Latest holdings; resolve IDs; sample calls to Prices/Fundamentals
  - Detect: Capture 403/404/empty results as coverage/entitlement issues
  - Report: Summarize issues; email exception report with ready-to-send entitlement request template
- Time savings estimate: 1–2 hours/week; reduces incidents
- Implementation complexity: Low-Medium
- Priority ranking: Medium

5) Sector/Region Exposure Reconciliation
- Tools involved: Morningstar holdings/exposure exports, FactSet Classification APIs (RBICS/GICS, Country), optional Postgres
- Current manual process:
  - PMs manually compare Morningstar exposures with internally computed exposures using spreadsheets.
- Proposed n8n workflow:
  - Trigger: Weekly after holdings refresh
  - Ingest: Morningstar holdings and exposure reports; resolve IDs
  - Classify & compute: Fetch FactSet classifications; compute exposures from holdings; compare to Morningstar
  - Report: Flag deltas >1%; generate discrepancy CSV with constituent contributors; email and optionally persist for trend tracking
- Time savings estimate: 2–3 hours/week
- Implementation complexity: Medium
- Priority ranking: Medium

Overall prioritization by ROI:
1. Daily Master Data Sync (High)
2. Corporate Actions Aggregator (High)
3. Research Signal Alerts (Medium)
4. Data Coverage/Entitlement Watchdog (Medium)
5. Exposure Reconciliation (Medium)

Security and observability (applies to all):
- Use n8n credentials for OAuth2/SFTP; store secrets in environment variables
- Restrict n8n host by IP allowlists; enable HTTPS
- Add centralized error-trigger workflows and Postgres logging for auditability
- Least-privilege DB accounts; rotation of keys/secrets

## Quick Wins (implementable in <1 week)

1) Data Coverage/Entitlement Watchdog (MVP)
- Why: Low-Medium complexity, immediate visibility into data gaps, reduces incidents.
- Deliverables: Weekly exception email with CSV of unresolved symbols and dataset gaps; entitlement request template.
- Dependencies: Morningstar holdings export; FactSet OAuth2; distribution list.

2) Research Signal Alerts (Phase 1: FactSet-only)
- Why: Moderate effort; immediate benefit to PM decision speed.
- Deliverables: Intraday email alerts on recommendation level changes and >5% target price moves for a defined watchlist.
- Dependencies: FactSet Estimates/Recommendations API; PM watchlist; SMTP.

3) Exposure Reconciliation (Pilot for one portfolio)
- Why: Constrained pilot fits within a week and surfaces controllable discrepancies.
- Deliverables: Weekly CSV comparing Morningstar vs FactSet-derived sector exposures for a single representative portfolio.
- Dependencies: Morningstar holdings/exposure exports; FactSet Classification; agreed sector scheme (RBICS or GICS).

## Implementation Roadmap

Phase 1: Quick Wins (Weeks 1–2)
- Week 1
  - Set up n8n environment hardening (HTTPS, credentials store, IP allowlist).
  - Implement Data Coverage/Entitlement Watchdog MVP; validate with last two holdings files.
  - Implement Research Signal Alerts (FactSet-only) for a defined watchlist; set delta thresholds; UAT with PMs.
- Week 2
  - Pilot Exposure Reconciliation for one portfolio; calibrate sector mapping and thresholds.
  - Establish Error Trigger workflow template and Postgres logging for all Phase 1 jobs.
  - Training: 60-minute handover session and runbook.

Phase 2: Medium Complexity (Weeks 3–6)
- Weeks 3–4: Daily Master Data Sync (foundation)
  - Build Morningstar ingestion via SFTP/IMAP; implement FactSet Symbology/Prices/Fundamentals enrichment.
  - Stand up Postgres schema (holdings_raw, prices, fundamentals, holdings_enriched) and upsert logic.
  - UAT with sample days; finalize daily email summary.
- Weeks 5–6: Research Signal Alerts (Phase 2)
  - Add Morningstar ratings nightly comparison; persist snapshots; refine alert formatting and routing.
  - Extend to multiple watchlists/portfolios; add alert suppression rules to avoid noise.

Phase 3: Advanced Integrations (Weeks 7–12)
- Weeks 7–9: Corporate Actions Aggregator
  - Connect to Bloomberg DL SFTP; parse CA files; implement FactSet cross-check, deduplication, and discrepancy routing.
  - UAT with historical files; define operating procedures for discrepancies.
- Weeks 10–12: Exposure Reconciliation (scale-up) and Hardening
  - Expand reconciliation to all portfolios; add trend tracking in Postgres and monthly QA report.
  - Performance tuning, credential rotation schedule, dashboards for job health and SLAs.

Success metrics (by end of Phase 3)
- 90% reduction in manual Excel joins for daily portfolio data prep
- >80% of corporate actions captured via unified feed before market open
- Alert lead time: <10 minutes from data availability
- <1% unresolved identifier rate sustained week-over-week
- Documented runbooks and on-call error notifications with <1-hour MTTR

## Next Steps

Action items (owners and target dates)
- Appoint owners
  - Sponsor: Head of Portfolio Management (confirm) – by Oct 10, 2025
  - Technical lead: Data Engineering Manager – by Oct 10, 2025
  - Workflow operator: Operations Analyst – by Oct 10, 2025
- Access and prerequisites
  - Provision FactSet API OAuth2 credentials (Symbology, Prices, Fundamentals, Estimates) – Data Engineering – by Oct 14, 2025
  - Confirm Morningstar Direct scheduled exports (file names, SFTP path or mailbox) – Operations – by Oct 14, 2025
  - Decide sector scheme (RBICS vs GICS) for reconciliations – PM Team – by Oct 14, 2025
  - If proceeding with corporate actions: confirm Bloomberg Data License SFTP entitlement and directory paths – Market Data Team – by Oct 21, 2025
- Environment setup
  - Deploy n8n (self-hosted) with HTTPS, IP allowlist, environment secrets – IT/SRE – by Oct 14, 2025
  - Provision Postgres (managed or on-prem) with least-privilege user for n8n – IT/DBA – by Oct 14, 2025
- Build and UAT (Phase 1)
  - Implement Coverage/Entitlement Watchdog MVP – Data Engineering – by Oct 17, 2025
  - Implement Research Signal Alerts (FactSet-only, watchlist defined) – Data Engineering – by Oct 17, 2025
  - Pilot Exposure Reconciliation for one portfolio – Data Engineering + PM – by Oct 21, 2025
- Governance and operations
  - Create runbooks, alert routing, and escalation paths – Operations – by Oct 21, 2025
  - Schedule weekly 15-minute review of exceptions and KPI dashboard – PM/Operations – start Oct 21, 2025

Notes
- If Morningstar Direct API endpoints are available in your tenant, replace SFTP/email steps with HTTP Request nodes or webhook pushes to reduce latency and simplify operations.
- All proposed solutions use open-source n8n; no proprietary iPaaS required.

This plan delivers fast, measurable ROI, establishes a reusable data foundation, and reduces operational risk while keeping costs low through open-source tooling.