# Tech Stack Audit Report: Dearborn Partners

Audit Date: October 07, 2025
Total Tools Analyzed: 9

## Executive Summary
- Scope: Assessed Dearborn Partners’ core applications across Operations, Research, CRM, Custody, Productivity, and Distribution to identify automation and integration opportunities using n8n (self-hosted, open-source).
- Key findings: Multiple high-value, repeatable workflows are performed manually today (AUM updates, meeting pack assembly, onboarding, compliance filing). Wealthbox and Microsoft 365 offer strong API surfaces that can anchor low-risk automations. Advent Axys and Schwab are best ingested via scheduled file exports (SFTP).
- Total opportunities identified: 5 prioritized automation workflows.
- Estimated total time savings: 21–35 hours per week (conservative), plus reduced errors, faster client service, and stronger compliance audit trails.

## Tools Analyzed

1) Advent Axys (Category: Operations)
- Recent updates discovered: No vendor updates identified as of October 07, 2025.
- Key automation features added: File-based integrations via scheduled CSV exports to SFTP or mounted secure directories; stable schemas enable reliable parsing. No native REST API typically available.
- Current utilization assessment: High reliance for portfolio accounting and performance. Likely under-utilized for scheduled exports structured for downstream automation (e.g., household-level summaries). Opportunity to standardize export schemas and timing to feed CRM and dashboards.

2) CSSI (Category: Distribution)
- Recent updates discovered: No updates found.
- Key automation features added: Limited public integration details; often serviced via reports/exports or custodial feeds depending on use-case.
- Current utilization assessment: Low criticality in current stack; integrate only where a clear downstream consumer exists (e.g., distribution reporting). Defer automation until higher ROI workflows are live.

3) FactSet (Category: Research)
- Recent updates discovered: No updates found.
- Key automation features added: Robust APIs (Symbology, content, estimates) available by entitlement with IP allowlisting. Email alerting via research inbox is common.
- Current utilization assessment: High use by PMs; currently manual downstream sharing/tagging. Strong opportunity to enrich research with holdings impact and push to advisors via Teams/Wealthbox.

4) Bloomberg (Category: Research)
- Recent updates discovered: No updates found.
- Key automation features added: BLPAPI for data retrieval (desktop/server) subject to licensing. Automation constrained by entitlement and infrastructure requirements.
- Current utilization assessment: Critical for PM workflow but lower near-term automation ROI vs. FactSet and Axys. Keep as-is; consider targeted automations where licensing allows.

5) RightCapital (Category: Distribution/CS)
- Recent updates discovered: No updates found.
- Key automation features added: Advisor-level API may be available by request/plan; otherwise support for secure intake/invite links via email.
- Current utilization assessment: High-value for planning; currently manual re-keying from CRM in onboarding. Automate client creation and invitations when API access is available; otherwise use standardized email workflows.

6) Wealthbox (Category: CRM)
- Recent updates discovered: No updates found.
- Key automation features added: Public REST API; webhooks for events (plan-dependent). Supports custom fields and notes/activities—ideal for AUM syncs, onboarding triggers, and logging.
- Current utilization assessment: Central relationship system; currently updated manually with AUM/metrics. High ROI to automate updates and activity logging.

7) Schwab (Category: Custodian)
- Recent updates discovered: No updates found.
- Key automation features added: Schwab Data Delivery (SDD) via SFTP for files (positions/transactions). Direct APIs limited for RIAs; file-based ingestion standard.
- Current utilization assessment: Critical data source. If files are more consistent or timely than Axys, workflows can pivot to Schwab files with minimal parsing changes.

8) Zoom (Category: Productivity)
- Recent updates discovered: No updates found.
- Key automation features added: Webhooks (recording.completed, meeting.created), REST API, cloud recording and transcript retrieval.
- Current utilization assessment: Broadly used across the firm. Compliance capture is manual today—fast win to automate upload to SharePoint and CRM logging.

9) Microsoft 365 (Outlook/SharePoint/Teams/Excel) (Category: Productivity)
- Recent updates discovered: No updates found.
- Key automation features added: Microsoft Graph API access; n8n nodes for Outlook, SharePoint, Teams, Excel; supports service principals and app registrations.
- Current utilization assessment: Ubiquitous. Notably under-leveraged for automated dashboards (Excel/SharePoint) and orchestrated communications (Teams/Outlook).

## Integration Opportunities

Priority 1: Daily portfolio/AUM sync from Advent Axys exports to Wealthbox CRM and 365 dashboards
- Tools involved: Advent Axys (SFTP exports), Wealthbox, Microsoft 365 (SharePoint/Excel/Teams/Outlook), optional PostgreSQL.
- Current manual process:
  - Ops downloads daily positions/transactions, aggregates to household/rep, manually updates AUM/custom fields in Wealthbox, uploads CSVs to 365, emails advisors.
- Proposed n8n workflow:
  - Schedule Trigger: Daily 6:30 AM.
  - SFTP node: Pull Axys CSVs (positions, transactions, performance).
  - Spreadsheet File node: Parse CSVs to JSON.
  - Function node: Normalize and aggregate to household/advisor; compute AUM, 1/3/12M returns, cash %, large cash movements.
  - PostgreSQL node (optional): Upsert daily snapshots for history/audit.
  - HTTP Request (Wealthbox API): Upsert Contacts/Households custom fields; create daily note with changes.
  - Microsoft Excel (SharePoint): Append daily snapshot to AUM dashboard table.
  - Microsoft Teams: Post morning summary to Advisors channel with dashboard link.
  - Outlook: Send exception report if data gaps/inconsistencies; IF node validates file freshness and row counts.
- Time savings estimate: 10–15 hours/week; fewer CRM errors.
- Implementation complexity: Medium.
- Priority ranking: High.

Priority 2: Automated client review meeting pack (briefing PDF) generation
- Tools involved: Microsoft 365 (Outlook/SharePoint/OneDrive), Advent Axys (SFTP exports), Wealthbox, optional RightCapital, self-hosted Gotenberg (open-source).
- Current manual process:
  - Analyst assembles review materials from Axys, CRM notes, planning; builds PDF/deck; saves/emails—30–60 minutes per meeting.
- Proposed n8n workflow:
  - Schedule Trigger: Hourly scan next 7 days.
  - Outlook: List calendar events with category “Client Review.”
  - HTTP Request (Wealthbox API): Map attendees to households, pull recent notes.
  - SFTP + Spreadsheet File: Pull/parse Axys holdings/performance; compute YTD/1/3-year returns, top holdings, cash %, flows.
  - HTTP Request (RightCapital API, if available): Pull plan summary; IF node to skip if unavailable.
  - Function: Merge data into HTML template (household summary, goals, performance, cash, tasks).
  - HTTP Request (Gotenberg): Convert HTML to PDF.
  - SharePoint: Save PDF to client folder path Clients/Household/Reviews/YYYY-MM-DD.pdf.
  - Outlook: Email PDF to advisors; attach to calendar; include SharePoint link.
  - HTTP Request (Wealthbox API): Create note/activity with link; set follow-up if cash % > policy threshold.
- Time savings estimate: 5–10 hours/week.
- Implementation complexity: Medium-High.
- Priority ranking: High.

Priority 3: Wealthbox-driven client onboarding to RightCapital, 365 workspace, Zoom welcome call, and tasking
- Tools involved: Wealthbox, RightCapital (optional API), Microsoft 365 (SharePoint/Planner/Outlook), Zoom.
- Current manual process:
  - Advisors create client in Wealthbox, re-key to RightCapital, create folder structure, schedule welcome call, assign tasks—45–90 minutes/client.
- Proposed n8n workflow:
  - Webhook: Trigger on Wealthbox contact.created or opportunity to “Client” (or poll).
  - HTTP Request (Wealthbox): Fetch contact/household; set “Onboarding: Started.”
  - SharePoint: Create client folder structure from template (Agreements, Statements, Planning Docs).
  - Planner/To Do: Create onboarding checklist with owners/dates.
  - Zoom: Create welcome meeting (templated settings).
  - Outlook: Send calendar invites with Zoom link and Microsoft Form for data.
  - IF (RightCapital API available):
    - Yes: Create RightCapital client and send invitation.
    - No: Send standardized secure intake email; log note in Wealthbox.
  - HTTP Request (Wealthbox): Update custom fields with links/status; create activity.
- Time savings estimate: 3–5 hours/week; fewer re-keying errors.
- Implementation complexity: Medium.
- Priority ranking: Medium-High.

Priority 4: Zoom recording and transcript compliance capture to SharePoint + Wealthbox logging
- Tools involved: Zoom, Microsoft 365 (SharePoint/Outlook), Wealthbox.
- Current manual process:
  - Staff downloads recordings, renames, uploads to SharePoint, creates CRM notes, emails Compliance—often delayed.
- Proposed n8n workflow:
  - Webhook: Zoom recording.completed event.
  - HTTP Request (Zoom): Fetch metadata and download URLs for recording/transcript.
  - Move Binary Data: Handle binary streams.
  - SharePoint: Upload with naming “YYYYMMDD_MeetingTitle.mp4/.vtt” to client folder.
  - Function: Match to Wealthbox contact via registrant email/topic; fallback to manual review task.
  - HTTP Request (Wealthbox): Create note/activity with SharePoint links and tags.
  - Outlook: Notify Compliance; alert if no transcript.
- Time savings estimate: 1–2 hours/week; improved compliance.
- Implementation complexity: Low-Medium.
- Priority ranking: Medium.

Priority 5: Research note capture and enrichment from email to SharePoint with client impact alerts
- Tools involved: FactSet (API), Microsoft 365 (Outlook/SharePoint/Teams), Advent Axys exports, Wealthbox.
- Current manual process:
  - PMs receive research PDFs, manually save/tag, notify advisors; limited linkage to clients holding affected securities.
- Proposed n8n workflow:
  - IMAP/Graph: Watch research@dearbornpartners.com for new messages with attachments.
  - IF: Filter approved senders/subjects.
  - SharePoint: Upload PDFs to Research library; set metadata (source, date).
  - Function: Extract tickers/ISINs from email subject/body.
  - HTTP Request (FactSet Symbology/Content): Validate symbols; enrich with company, sector, market cap.
  - SFTP + Spreadsheet File: Retrieve latest Axys positions; map tickers to accounts/households.
  - Function: Identify impacted advisors/households; build summary.
  - Teams: Post to Research channel with summary and SharePoint link.
  - HTTP Request (Wealthbox): Create notes/tasks on impacted households for advisor follow-up.
- Time savings estimate: 2–3 hours/week; stronger research traceability.
- Implementation complexity: Medium-High.
- Priority ranking: Medium.

## Quick Wins (implementable in < 1 week)

1) Zoom compliance capture (Priority 4)
- Why: Low-Medium complexity; immediate compliance and time savings.
- Scope for week 1: Webhook app, SharePoint upload, Wealthbox note creation, Compliance email.
- Expected impact: 1–2 hours/week saved; faster, consistent retention.

2) AUM sync (Phase 1 “lite”) to Wealthbox + Excel (subset of Priority 1)
- Why: High ROI, can start without historical DB or Teams post.
- Scope for week 1: SFTP pull, CSV parse, compute AUM per household/advisor, update Wealthbox custom fields, append to Excel dashboard table in SharePoint.
- Expected impact: 6–8 hours/week saved immediately; eliminates manual CRM updates.

3) Onboarding scaffolding (Priority 3 “starter”)
- Why: Medium complexity overall, but a minimal version is quick.
- Scope for week 1: Wealthbox webhook/poll trigger, SharePoint folder creation, Planner checklist creation, Outlook invite template (manual Zoom link for first iteration).
- Expected impact: 1–2 hours/week saved; reduces re-keying and improves consistency.

## Implementation Roadmap

Phase 1: Quick Wins (Weeks 1–2)
- Deliverables:
  - Zoom compliance capture in production (webhook → SharePoint → Wealthbox → Compliance email).
  - AUM sync “lite” to Wealthbox and Excel dashboard (daily schedule).
  - Onboarding scaffolding (Wealthbox trigger → SharePoint folders → Planner tasks → Outlook invite).
- Infrastructure:
  - Stand up n8n (self-hosted) and credentials vault.
  - App registrations for Microsoft 365; Zoom OAuth app; Wealthbox API token.
  - Configure Axys scheduled SFTP exports with stable schemas.
- Outcomes:
  - 8–12 hours/week saved; audit-friendly logging begins.

Phase 2: Medium Complexity (Weeks 3–6)
- Enhance AUM sync:
  - Add Teams morning summary; exception handling; optional PostgreSQL for history/audit.
- Automated client review pack:
  - Build HTML template; integrate Axys performance, Wealthbox notes; Gotenberg PDF; SharePoint saving; Outlook distribution; task triggers on cash thresholds.
- Onboarding expansion:
  - Zoom meeting auto-creation; RightCapital API integration or standardized secure invite; Wealthbox status field updates and link writing.
- Outcomes:
  - Cumulative 16–25 hours/week saved; higher data quality; consistent client deliverables.

Phase 3: Advanced Integrations (Weeks 7–12)
- Research capture and enrichment:
  - Email parsing, FactSet enrichment, holdings joins, Teams distribution, Wealthbox notes/tasks.
- AUM sync hardening:
  - Add Schwab file ingestion option; crosswalk tables; data quality KPIs; full audit trails in PostgreSQL.
- Governance and monitoring:
  - Centralized workflow run logs, error alerting, access reviews, and periodic data reconciliation reports.
- Outcomes:
  - Cumulative 21–35 hours/week saved; robust governance and compliance posture.

## Next Steps

Immediate actions (Week 1)
- Owner: IT Admin
  - Stand up n8n on a hardened VM or container; restrict by IP/VPN; enable HTTPS; configure backups.
  - Create Microsoft Entra app registrations for Graph (SharePoint, Outlook, Teams, Excel) with least-privilege scopes; set service principals.
- Owner: Operations Lead
  - Configure Advent Axys nightly CSV exports to SFTP with fixed schemas and naming; confirm 6:00 AM availability.
  - Provide household/account-to-Wealthbox ID mapping (CSV) for initial sync.
- Owner: CRM Admin
  - In Wealthbox, create custom fields for Current AUM, Last Position Date, 1/3/12M returns, Cash %; generate API token; confirm webhook availability.
- Owner: Compliance Officer
  - Approve Zoom webhook usage and retention policy; confirm SharePoint storage path and permissions for recordings and transcripts.
- Owner: PM Team
  - Approve the “Client Review” calendar category convention; validate performance metrics definitions for review packs.

Short-term (Weeks 2–4)
- Owner: IT Admin
  - Deploy Gotenberg container behind firewall for HTML-to-PDF; allow n8n egress; set auth.
  - Optional: Provision PostgreSQL for workflow run logs and AUM snapshots.
- Owner: Advisor Ops
  - Finalize onboarding checklist in Planner/To Do; define folder template structure; finalize welcome email and meeting templates.
- Owner: Vendor Liaison
  - Confirm RightCapital API availability and scopes; if unavailable, finalize secure intake email process.
  - Confirm FactSet API entitlements and IP allowlisting steps.

Mid-term (Weeks 5–8)
- Owner: Data Steward (Ops/PM)
  - Implement crosswalk table maintenance (CUSIP/ISIN/Ticker and account→household→Wealthbox mappings).
  - Define exception thresholds and data quality KPIs (file freshness, row counts, variance limits).
- Owner: Compliance Officer
  - Review and document audit trails, retention schedules, and access controls for new SharePoint libraries and dashboards.
- Owner: CRM Admin
  - Pilot advisor dashboards; gather feedback; iterate on fields and summaries posted to Teams.

Dependencies and prerequisites to validate
- Wealthbox: API token and webhook availability for your plan.
- RightCapital: API access confirmed; fallback to invite email if not.
- Advent Axys: Nightly SFTP exports with stable column headers.
- Schwab: Optional SDD SFTP files if chosen as primary data source.
- FactSet: Symbology/Content API entitlements and IP allowlisting.
- Zoom and Microsoft 365: OAuth apps, tenant admin consent, and service principals.
- Security: Store all secrets in n8n credentials vault; restrict access; enable workflow run logging and PII minimization.

Business Value Summary
- Faster advisor mornings: Automated AUM visibility and exception alerts improve client readiness.
- Consistent client experience: Standardized review packs and onboarding reduce variability and errors.
- Compliance strength: Automatic capture and logging of meetings/recordings improves audit readiness.
- Scalable operations: Open-source n8n keeps cost low while allowing iterative build-out and ownership of workflows.

Estimated ROI
- Time savings: 21–35 hours/week across Ops, Advisors, and PM teams.
- Payback: With open-source n8n and existing licenses, payback measured in weeks from reduced manual effort and error remediation.
- Risk reduction: Automated, logged processes with access controls lower operational and compliance risk.

Notes on Technology Approach (open-source first)
- Orchestrator: n8n (self-hosted) with built-in nodes: Schedule Trigger, Webhook, HTTP Request, SFTP, Spreadsheet File, Function, IF, Microsoft 365 (Outlook/SharePoint/Excel/Teams), Zoom; optional PostgreSQL.
- PDF service: Gotenberg (open-source) for dependable HTML-to-PDF rendering.
- Data storage: Prefer SharePoint for team access; PostgreSQL for history/audit and metrics where needed.

If desired, we can begin with a 2-week pilot covering Phase 1 deliverables and a success review at the end of Week 2 to confirm expansion into Phase 2.