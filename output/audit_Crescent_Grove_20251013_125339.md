# Tech Stack Audit Report: Crescent Grove

Audit date: October 13, 2025

## Executive Summary
- Scope: Comprehensive review of 17 tools across research, productivity, collaboration, portfolio management, CRM, planning, operations, accounting, HR, and custodial systems. Focus on automation opportunities using open-source n8n to reduce manual work and risk.
- Total tools analyzed: 17
- Key findings:
  - The stack is mature and standardized (Microsoft 365, Redtail, Orion/PortfolioCenter, DocuSign, custodial SFTP). Documentation, trading file handling, and client communications present the highest automation ROI and risk reduction.
  - No critical vendor updates were identified during the audit window; however, strong API/SFTP/Graph capabilities across current tools enable impactful n8n workflows without new licenses.
- Total opportunities identified: 5 prioritized automations
- Estimated total time savings: ~19.5–32.5 hours per week (≈ 78–130 hours per month), plus improved compliance and reduced operational risk

## Tools Analyzed

1) FactSet (Research)
- Recent updates discovered: None during this audit window.
- Key automation features added: None identified; typical integration path is CSV/PDF exports to SharePoint for archival; API access generally enterprise-controlled.
- Current utilization assessment: High-criticality research tool used by Portfolio Management. Automation impact likely indirect (report distribution/archival).

2) Morningstar Direct (Research)
- Recent updates discovered: None during this audit window.
- Key automation features added: None identified; leverage scheduled exports to SharePoint; potential for API if licensed.
- Current utilization assessment: High-criticality for research analytics. Automation focus: consistent report filing and meeting prep packets.

3) Bloomberg Terminal (Research)
- Recent updates discovered: None during this audit window.
- Key automation features added: None identified; consider exporting analyses to SharePoint; API (BLP) is desktop/Entitlement-bound and out-of-scope for n8n.
- Current utilization assessment: High-criticality for portfolio team; automation opportunities center on document handling and task tracking.

4) Microsoft Excel (Productivity)
- Recent updates discovered: None during this audit window.
- Key automation features added: N/A this period; n8n can process Excel/CSV via Spreadsheet nodes for trade confirms and reporting.
- Current utilization assessment: Ubiquitous. Use for data prep may be reduced via automated pipelines.

5) Microsoft Teams (Communication)
- Recent updates discovered: None during this audit window.
- Key automation features added: N/A this period; n8n can post to channels for operational alerts (trading, document completion, inbox triage).
- Current utilization assessment: High across all users; ideal notification endpoint for automations.

6) Microsoft Outlook (Communication)
- Recent updates discovered: None during this audit window.
- Key automation features added: N/A this period; IMAP/Graph-accessible for shared mailbox monitoring in n8n.
- Current utilization assessment: High across all users; central for client/custodian intake workflows.

7) Microsoft SharePoint (Collaboration)
- Recent updates discovered: None during this audit window.
- Key automation features added: N/A this period; Graph/SharePoint nodes in n8n support folder creation and file uploads.
- Current utilization assessment: High; system of record for documents. Strong candidate for automated filing from DocuSign and email attachments.

8) Microsoft365 (Research)
- Recent updates discovered: None during this audit window.
- Key automation features added: N/A; platform capabilities (Azure AD, Graph API) enable secure OAuth-based integrations with n8n.
- Current utilization assessment: Medium-criticality for Portfolio Management; principal value is enabling Graph-based automation across Outlook/SharePoint/Teams.

9) Schwab PortfolioCenter (Portfolio Management)
- Recent updates discovered: None during this audit window.
- Key automation features added: N/A; supports exports suitable for SFTP-based trade file delivery/archival.
- Current utilization assessment: High-criticality; automation focus: trade file push and confirmation handling.

10) Orion Eclipse (Portfolio Management)
- Recent updates discovered: None during this audit window.
- Key automation features added: N/A; exports can drive automated custodial delivery and confirm reconciliation.
- Current utilization assessment: High-criticality; key integration in trading pipeline automation.

11) Redtail CRM (CRM)
- Recent updates discovered: None during this audit window.
- Key automation features added: N/A; API supports activities, notes, workflows, and contact search—ideal hub for logging and tasking via n8n.
- Current utilization assessment: High-criticality for Client Services; anchor for documentation and task traceability.

12) RightCapital (Financial Planning)
- Recent updates discovered: None during this audit window.
- Key automation features added: N/A; API availability varies by subscription—confirm endpoints for client upsert/report retrieval.
- Current utilization assessment: High-criticality for Advisors; integration focus: CRM sync and meeting prep assets.

13) DocuSign (Operations)
- Recent updates discovered: None during this audit window.
- Key automation features added: N/A; DocuSign Connect webhooks and REST API enable event-driven filing and CRM logging.
- Current utilization assessment: Medium-criticality, widely used across teams; prime target for auto-filing and notifications.

14) QuickBooks Desktop (Accounting)
- Recent updates discovered: None during this audit window.
- Key automation features added: N/A; desktop environment limits direct API access. Possible automations via file imports/exports or Web Connector if configured.
- Current utilization assessment: High-criticality for Operations; near-term automation limited; consider longer-term assessment of migration to QuickBooks Online for API-native workflows.

15) ADP Workforce Now (HR)
- Recent updates discovered: None during this audit window.
- Key automation features added: N/A; ADP APIs available by agreement. Out-of-scope for immediate n8n work but viable for future HR-to-CRM syncs.
- Current utilization assessment: Medium-criticality for Operations; low immediate overlap with current high-ROI automations.

16) Charles Schwab (Custodial)
- Recent updates discovered: None during this audit window.
- Key automation features added: N/A; custodial SFTP endpoints support automated trade file delivery and inbound confirms.
- Current utilization assessment: High-criticality for Trading; strong candidate for SFTP automations.

17) Fidelity Institutional (Custodial)
- Recent updates discovered: None during this audit window.
- Key automation features added: N/A; custodial SFTP endpoints support automated workflows similar to Schwab.
- Current utilization assessment: High-criticality for Trading; integrate alongside Schwab in unified workflow.

## Integration Opportunities

1) Auto-file executed DocuSign envelopes to SharePoint and log in Redtail
- Tools involved: DocuSign, Microsoft SharePoint, Redtail CRM, Microsoft Teams/Outlook
- Current manual process:
  - Staff monitor DocuSign, download/rename PDFs, upload to client SharePoint folders
  - Create Redtail activities/notes and email confirmations to the team
- Proposed n8n workflow:
  - Trigger: Webhook to receive DocuSign Connect Envelope-Completed events
  - DocuSign API: Get envelope details and download documents (binary)
  - Function Item: Standardize filename: {ClientName}_{Subject}_{YYYY-MM-DD}_{EnvelopeId}.pdf
  - SharePoint: Ensure folder path /Client Documents/{Client}/DocuSign/{YYYY}/ exists; upload file(s)
  - Redtail API: Find contact by recipient email/name; create Activity/Note with SharePoint link and metadata
  - Teams/Outlook: Post completion notification with links
  - Error handling: Branch for contact not found (create triage task) and upload retries with Teams alert
- Time savings estimate: ~12–15 minutes per envelope; ~25/week ≈ 5–6 hours/week
- Implementation complexity: Medium
- Priority ranking: High

2) Client email-to-CRM activity capture with attachment filing
- Tools involved: Microsoft Outlook/Exchange (shared mailbox), SharePoint, Redtail CRM, Microsoft Teams
- Current manual process:
  - CS team triages shared inbox, files attachments to SharePoint, logs Redtail activities, assigns tasks, posts urgent messages in Teams
- Proposed n8n workflow:
  - Trigger: IMAP Email (watch shared mailbox every 1–5 minutes)
  - Filters: Sender domain/keywords/attachments; classify urgency
  - SharePoint: Upload attachments to /Client Documents/{Client}/Inbox/{YYYY-MM}/; return links
  - Redtail API: Create Activity/Note with email body, metadata, and SharePoint links; optionally start workflow based on keywords (e.g., RMD)
  - Teams: Post to “Client Inbox” channel for urgent items
  - Error handling: If no contact match, create “Unmatched” activity and Teams alert for triage
- Time savings estimate: ~1–2 minutes per email; 150–250/week ≈ 3–7 hours/week
- Implementation complexity: Low–Medium
- Priority ranking: High

3) Automated trade file push to custodians with confirm ingestion and alerts
- Tools involved: Orion Eclipse and/or Schwab PortfolioCenter, Charles Schwab (SFTP), Fidelity Institutional (SFTP), Redtail CRM, Microsoft Teams, SharePoint (optional archival)
- Current manual process:
  - Export trade files, manually upload via SFTP, later download confirms/fails, update logs/CRM, notify team
- Proposed n8n workflow:
  - Outbound: SFTP Trigger or scheduled poll of internal Outbox; upload to Schwab/Fidelity SFTP; move to Sent/{date}; retry/backoff on failure; Teams status messages; optional SharePoint archival
  - Inbound: SFTP Trigger on custodial confirm folders; parse CSV/TSV/fixed-width; create/update Redtail activities (“Trade Confirm”/“Trade Exception”) with next-business-day due dates; daily Teams summary via Cron
- Time savings estimate: ~1–1.75 hours/day ≈ 5–8 hours/week; strong error reduction
- Implementation complexity: Medium–High
- Priority ranking: High

4) Calendar-driven creation of client meeting prep packets
- Tools involved: Microsoft Outlook/Graph (calendar), Redtail CRM, RightCapital, Orion/PortfolioCenter, SharePoint, Microsoft Teams
- Current manual process:
  - Assemble notes, planning snapshots, performance reports; create SharePoint folders; email links to team
- Proposed n8n workflow:
  - Trigger: Daily schedule; pull next 7 days of client review events
  - Identify client via attendees/title mapping
  - Redtail API: Fetch recent notes, household details, open tasks; build summary
  - RightCapital: Retrieve plan snapshot/report if API available; otherwise include app link
  - Orion/PortfolioCenter: Fetch latest performance/positions export/PDF
  - SharePoint: Create folder /Client Documents/{Client}/Meetings/{YYYY-MM-DD}_{Title}/; upload assets
  - Optional: Generate a one-page summary PDF (self-hosted HTML→PDF service)
  - Teams: Post folder link to “Upcoming Meetings” channel
- Time savings estimate: ~30–45 minutes per meeting; 8–10/week ≈ 4–7.5 hours/week
- Implementation complexity: Medium–High
- Priority ranking: Medium

5) Bi-directional client/household sync between Redtail and RightCapital
- Tools involved: Redtail CRM, RightCapital, Microsoft Teams
- Current manual process:
  - Duplicate client creation/updates across systems; CSV imports; risk of mismatches
- Proposed n8n workflow:
  - Trigger: Every 15 minutes
  - Redtail API: GET contacts updated_since last run; transform to RightCapital schema
  - RightCapital API: Upsert households/clients by externalId/email
  - Optional reverse sync: Pull RightCapital changes; update Redtail based on authoritative field policy
  - Error handling: Batch paging, rate-limit handling, Teams alerts for conflicts/duplicates
- Time savings estimate: Onboarding 10–15 minutes/household; updates 3–5 minutes each; ≈ 2.5–4 hours/week
- Implementation complexity: Medium (dependent on RightCapital API access)
- Priority ranking: Medium

## Quick Wins

- DocuSign → SharePoint auto-filing + Redtail activity logging
  - Why quick: Event-driven via DocuSign Connect; standard SharePoint/Redtail APIs; clear file naming and folder rules.
  - Effort: ~3–5 days including testing and permissions.
  - Impact: 5–6 hours/week saved; improved auditability.

- Centralized email intake → Redtail logging + SharePoint filing
  - Why quick: Uses IMAP/Graph and existing shared mailbox; straightforward classification and filing.
  - Effort: ~3–5 days with keyword tuning and contact match logic.
  - Impact: 3–7 hours/week saved; fewer missed items, faster triage.

- Teams operational alerts for trading and documents (as part of both above)
  - Why quick: Minimal configuration once Teams OAuth/app is set.
  - Effort: ~1–2 days embedded in other workflows.
  - Impact: Faster visibility; reduces follow-ups and status meetings.

## Implementation Roadmap

- Phase 1: Quick wins (Weeks 1–2)
  - Deliverables:
    - Production n8n instance hardened (HTTPS, credentials vault, backups)
    - DocuSign → SharePoint + Redtail workflow live for 1–2 client segments
    - Email intake → Redtail + SharePoint workflow in pilot on shared mailbox
    - Teams notification channels set (“Docs – Executed”, “Client Inbox”)
  - Success metrics:
    - 80%+ of executed envelopes auto-filed with correct naming
    - 70%+ of tagged inbox emails auto-logged to Redtail with links
    - <2% error/retry rate in first two weeks

- Phase 2: Medium complexity (Weeks 3–6)
  - Deliverables:
    - Trading: Outbound SFTP upload automation to Schwab/Fidelity with retries and Teams alerts
    - Trading: Inbound confirm ingestion, exception tasking in Redtail, daily summary to Teams
    - Optional: SharePoint archival for trade files
  - Success metrics:
    - 100% of trade files delivered via automation; zero missed uploads
    - Exceptions logged in Redtail same day; daily Teams summary by 4:30pm

- Phase 3: Advanced integrations (Weeks 7–12)
  - Deliverables:
    - Calendar-driven meeting prep packets (summary generation, plan/performance inclusion)
    - Redtail ↔ RightCapital client sync with authoritative field policy and Teams hygiene alerts
  - Success metrics:
    - 90% of upcoming client meetings have prep folders and assets created automatically
    - 95%+ match rate in CRM↔Planning sync; conflicts resolved within 1 business day

## Next Steps

- Stand up and secure n8n
  - Owner: IT
  - Timeline: Week 1
  - Actions:
    - Provision n8n (self-hosted), enable HTTPS/TLS, restrict access
    - Configure credentials vault; set up OAuth apps for Microsoft Graph, DocuSign, Teams

- Confirm API and SFTP access
  - Owner: IT + Vendors
  - Timeline: Week 1
  - Actions:
    - DocuSign: Create Integration Key/Secret and configure Connect webhook to n8n
    - Microsoft: Register Azure AD app with Graph scopes (Mail, Files, Sites, Calendars, Teams as needed)
    - Redtail: Obtain API key and user key; validate rate limits
    - Custodians: Validate Schwab/Fidelity SFTP endpoints, keys, firewall/VPN rules
    - RightCapital: Confirm API availability and scopes (create/update clients, reports)

- Define data mappings and folder conventions
  - Owner: Operations + Client Services
  - Timeline: Week 1–2
  - Actions:
    - Establish client folder schema in SharePoint (DocuSign/{YYYY}, Inbox/{YYYY-MM}, Meetings/{date})
    - Create mapping rules: recipient email → Redtail contact; calendar titles/attendees → household
    - Standardize naming pattern for documents

- Implement Phase 1 workflows
  - Owner: IT + Operations
  - Timeline: Weeks 1–2
  - Actions:
    - Build DocuSign → SharePoint + Redtail n8n workflow; test in sandbox; go-live
    - Build Email intake → Redtail + SharePoint workflow; pilot on shared mailbox; iterate filters
    - Set up Teams channels and alerts; document SOPs

- Implement Phase 2 trading automations
  - Owner: Trading + IT
  - Timeline: Weeks 3–6
  - Actions:
    - Configure outbound SFTP upload with retries and logging
    - Configure inbound confirm parsing and Redtail task generation
    - Daily Teams roll-up; optional SharePoint archival

- Implement Phase 3 meeting prep and CRM↔Planning sync
  - Owner: Advisors + Client Services + IT
  - Timeline: Weeks 7–12
  - Actions:
    - Build calendar-driven prep packet generation; confirm availability of plan/performance assets
    - Implement Redtail↔RightCapital sync; define authoritative fields and conflict resolution
    - Create “Data Hygiene” Teams channel for sync alerts

- Governance, monitoring, and training
  - Owner: Compliance + Operations
  - Timeline: Ongoing, initiate Week 2
  - Actions:
    - Enable n8n execution logs and alerting; monthly audit of automation outcomes
    - Document runbooks and exception handling
    - Train CS, Trading, and Advisors on new workflows and Teams channels

- KPI tracking and ROI review
  - Owner: COO
  - Timeline: 30/60/90 days post go-live
  - Actions:
    - Measure hours saved vs. baseline; error rates; turnaround times
    - Prioritize backlog improvements (e.g., QuickBooks Desktop data exports, ADP HR sync if needed)

Security and compliance notes
- Store all secrets in n8n credentials; enforce least-privilege scopes on Azure AD and vendor apps
- Prefer OAuth2 for Microsoft Graph and DocuSign; key-based auth for SFTP where supported
- Maintain audit trail via n8n execution history and Redtail activities; ensure data retention policies align with RIA recordkeeping requirements

Estimated cumulative ROI
- Weekly time savings: ~19.5–32.5 hours
- Monthly time savings: ~78–130 hours
- Qualitative gains: Lower regulatory/documentation risk, faster client response, fewer missed trades/files, and improved meeting readiness

This plan leverages only open-source n8n with native nodes and generic HTTP/SFTP integrations, avoiding proprietary iPaaS costs while focusing on concrete, high-impact workflows across Crescent Grove’s stack.