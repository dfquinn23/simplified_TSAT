# Tech Stack Audit Report: Crescent Grove Advisors

Audit Date: October 07, 2025
Total Tools Analyzed: 14

## Executive Summary
- Scope: Reviewed 14 tools across Operations, Research, Distribution/CS, CRM, Custodian, and Productivity. Assessed current utilization, recent updates, and automation potential using open-source n8n.
- Key findings:
  - High-value automation opportunities exist around custodian data ingestion, client onboarding, and meeting documentation where manual steps create delays and error risk.
  - Core platforms (Microsoft 365, Redtail, Addepar, Global Relay, Zoom) provide robust APIs or SFTP that n8n can orchestrate securely within your AWS environment.
  - No critical vendor updates were discovered during the audit window; however, standardizing file, folder, and field mappings is a prerequisite to maximize automation ROI.
- Total opportunities identified: 6 prioritized n8n workflows.
- Estimated total time savings: 108–168 hours per month (27–42 hours per week), equating to approximately 0.6–1.0 FTE. With conservative loaded FTE cost assumptions, payback on n8n deployment is under 2 months.

## Tools Analyzed

1) Venn (Operations)
- Recent updates discovered: None identified during audit window.
- Key automation features: API-based report generation/download where licensed; email delivery fallback; supports periodic reporting cycles.
- Current utilization assessment: High criticality for PM; reports are exported manually. Strong candidate for scheduled retrieval and distribution to clients/CRM.

2) Citrix (Distribution)
- Recent updates discovered: None identified.
- Key automation features: Not typically an automation target; focus on secure remote access and MFA enforcement.
- Current utilization assessment: Low criticality in this stack; ensure version currency, MFA, and least-privilege access.

3) AWS EFS (Research)
- Recent updates discovered: None identified.
- Key automation features: NFS mount for centralized archival; lifecycle policies; integrates with n8n via Write Binary File when mounted on host.
- Current utilization assessment: High criticality for data archival. Ensure encryption at rest, IAM-controlled access, lifecycle policies, and backup strategy.

4) Microsoft 365 (Research)
- Recent updates discovered: None identified.
- Key automation features: Outlook, Teams, SharePoint/OneDrive, Contacts APIs; OAuth2; service accounts.
- Current utilization assessment: High criticality. Primary channel for notifications, document storage, and compliance capture (via Global Relay journaling).

5) Zoom (Distribution/CS)
- Recent updates discovered: None identified.
- Key automation features: Webhooks for meeting/recording events; REST API for recordings/transcripts.
- Current utilization assessment: High criticality. Underutilized for automated CRM logging and compliant storage workflows.

6) Redtail (CRM)
- Recent updates discovered: None identified.
- Key automation features: REST API for contacts, activities, notes; webhook/automation triggers vary by plan; supports polling.
- Current utilization assessment: High criticality. Ideal hub for onboarding orchestration and contact hygiene with M365.

7) Jump (Custodian)
- Recent updates discovered: None identified.
- Key automation features: Typically portal-based; verify SFTP or secure email intake options.
- Current utilization assessment: High criticality for advisors. Standardize intake method to integrate with onboarding flow.

8) Zocks (Productivity)
- Recent updates discovered: None identified.
- Key automation features: Unknown/public details limited. Confirm if APIs exist or if it’s a local utility.
- Current utilization assessment: Medium criticality but unclear integration value. Action: Validate vendor/API capabilities or consider replacement if it’s a bottleneck.

9) Addepar (Productivity)
- Recent updates discovered: None identified.
- Key automation features: SFTP intake; Import API with job polling; supports batch CSV ingestion.
- Current utilization assessment: High criticality. Prime target for automated nightly feeds and Canoe-parsed data import.

10) Canoe (Productivity)
- Recent updates discovered: None identified.
- Key automation features: API/webhooks (enterprise); SFTP; structured output from documents.
- Current utilization assessment: Medium criticality. Good candidate for automated intake, parsing, and downstream Addepar import.

11) Fidelity (Productivity)
- Recent updates discovered: None identified.
- Key automation features: SFTP/portal exports for positions/transactions/prices; email intake for onboarding in some cases.
- Current utilization assessment: High criticality. Standardize SFTP feeds; clarify overlap with Wealthscape.

12) Wealthscape (Productivity)
- Recent updates discovered: None identified.
- Key automation features: SFTP/portal reports; may duplicate Fidelity data surfaces. Confirm canonical source.
- Current utilization assessment: Medium criticality. Action: Rationalize “Fidelity” vs. “Wealthscape” naming and feeds to prevent duplicate handling.

13) DocuSign (Productivity)
- Recent updates discovered: None identified.
- Key automation features: Templates, role-based recipients, Connect webhooks; robust API.
- Current utilization assessment: Low criticality listed, but functionally critical to onboarding. High ROI when orchestrated with Redtail and custodian submissions.

14) Global Relay (Productivity)
- Recent updates discovered: None identified.
- Key automation features: Email journaling capture; API optional; best used via journaled mailbox.
- Current utilization assessment: High criticality. Ensure all client communications from automations are journaled for compliance.

## Integration Opportunities

1) Custodian-to-Addepar data pipeline with archival (Nightly)
- Tools involved: Fidelity/Wealthscape (SFTP), Addepar (SFTP/API), AWS EFS, Microsoft 365 (Outlook/Teams/SharePoint).
- Current manual process: Ops downloads files, renames/archives on EFS, uploads to Addepar, monitors, and emails status.
- Proposed n8n workflow:
  - Schedule Trigger nightly (e.g., 02:00 AM).
  - SFTP List/Download → de-dup via hash → Write Binary File to EFS with standardized path → Upload to Addepar via SFTP or API → Poll import job status.
  - IF nodes for missing files/exceptions; Teams/Outlook summary with file counts, hashes, and job IDs.
  - Error Trigger for alerting and retry guidance.
- Time savings estimate: 8–12 hours/week (32–48 hours/month).
- Implementation complexity: Medium–High.
- Priority ranking: High (Priority 1).

2) Client onboarding orchestration: Redtail → DocuSign → Custodian → Archive to SharePoint and CRM
- Tools involved: Redtail, DocuSign, Fidelity/Wealthscape/Jump (email/SFTP submissions), Microsoft 365 SharePoint/Outlook, Global Relay.
- Current manual process: Advisors create in CRM; Ops sets up DocuSign, tracks completion, files docs, submits to custodian, updates CRM, emails compliance.
- Proposed n8n workflow:
  - Webhook (preferred) or scheduled poll from Redtail to detect onboarding events.
  - Create DocuSign envelopes from templates; receive completion via Connect webhook.
  - Upload completed docs to SharePoint; update Redtail notes/status with links.
  - Submit to custodian via secure email or SFTP; BCC journaled mailbox for Global Relay.
  - Teams notifications to onboarding channel.
- Time savings estimate: 8–12 hours/week (32–48 hours/month).
- Implementation complexity: High.
- Priority ranking: High (Priority 2).

3) Zoom meetings → Redtail activity with recording storage and compliance capture
- Tools involved: Zoom, Redtail, Microsoft 365 SharePoint/OneDrive, Global Relay.
- Current manual process: Advisors log meetings after the fact; recordings/transcripts saved manually; compliance notified separately.
- Proposed n8n workflow:
  - Zoom Trigger on “Recording Completed” and “Meeting Ended”.
  - Fetch details/recording URLs; resolve participants to Redtail contacts.
  - Upload recording/transcript to client folder in SharePoint; create Redtail Activity with links.
  - Email summary to compliance/journaled inbox; handle unmatched contacts via Ops queue.
- Time savings estimate: 3–5 hours/week (12–20 hours/month).
- Implementation complexity: Medium.
- Priority ranking: Medium (Priority 3).

4) Canoe document intake → parsed data delivery → Addepar import
- Tools involved: Microsoft 365 Outlook, Canoe, AWS EFS, Addepar (SFTP/API), Microsoft Teams.
- Current manual process: Ops gathers statements/K-1s, uploads to Canoe, waits, exports normalized data, prepares CSVs for Addepar, archives, and notifies PM.
- Proposed n8n workflow:
  - Outlook Trigger on statements mailbox/folder; upload attachments to Canoe; archive originals to EFS.
  - Webhook on parse completion; transform JSON to Addepar schema; generate CSVs and upload to Addepar.
  - Teams notification with counts/exceptions and EFS links.
- Time savings estimate: 4–6 hours/week (16–24 hours/month).
- Implementation complexity: Medium.
- Priority ranking: Medium (Priority 4).

5) Redtail ↔ Microsoft 365 contact synchronization (address book hygiene)
- Tools involved: Redtail, Microsoft 365 Outlook/People, SharePoint (audit log).
- Current manual process: Contacts maintained in both systems; duplicates and stale info; no audit trail.
- Proposed n8n workflow:
  - Every 6 hours: Redtail → M365 upsert to shared contacts folder using Redtail ID as external key; optional M365 → Redtail updates for allowed fields.
  - SharePoint list for change audit; conflict alerts to Ops.
- Time savings estimate: 2–4 hours/week (8–16 hours/month) plus error reduction.
- Implementation complexity: Medium (one-way) to Medium–High (bi-directional).
- Priority ranking: Medium (Priority 5).

6) Venn report retrieval and distribution to clients and CRM
- Tools involved: Venn, Microsoft 365 SharePoint/Outlook, Redtail.
- Current manual process: PM exports reports, files to client folders, emails clients, updates CRM manually.
- Proposed n8n workflow:
  - Monthly/quarterly schedule.
  - Preferred: Venn API to generate and download PDFs; fallback: watch Outlook for Venn emails and ingest attachments.
  - Upload to SharePoint client folder; create Redtail Activity/Note with link; email client template with SharePoint link; BCC compliance for Global Relay capture.
- Time savings estimate: 2–3 hours/week in reporting cycles (8–12 hours/month during busy periods).
- Implementation complexity: Low–Medium (depends on API availability).
- Priority ranking: Low–Medium (Priority 6).

## Quick Wins (implementable in under 1 week)

1) Venn report retrieval via Outlook fallback
- Why: Low dependency and simple flow; immediate relief during reporting cycles.
- Scope: Outlook trigger → SharePoint upload → Redtail note → client email with compliance BCC.
- Expected savings: 8–12 hours/month in reporting periods.

2) Redtail → M365 one-way contact sync (to shared address book)
- Why: Reduces duplicate manual updates; improves client communications quickly.
- Scope: Redtail updated-since → normalize → upsert to shared contacts folder; SharePoint audit log.
- Expected savings: 6–8 hours/month plus reduced communication errors.

3) Zoom → Redtail “activity only” MVP
- Why: Fast path to better documentation; can defer recording storage to Phase 2.
- Scope: Zoom meeting-ended trigger → create Redtail activity with participants and Zoom link; email summary to compliance mailbox.
- Expected savings: 8–12 hours/month.

## Implementation Roadmap

Phase 1: Quick Wins (Weeks 1–2)
- Stand up n8n in AWS (Docker/VM) within VPC; mount AWS EFS; configure HTTPS behind reverse proxy.
- Provision service accounts and OAuth apps for Microsoft 365 and Zoom; store credentials in n8n vault.
- Implement:
  - Venn report retrieval (email-trigger path).
  - Redtail → M365 one-way contact sync.
  - Zoom → Redtail “activity-only” MVP with compliance email.

Phase 2: Medium Complexity (Weeks 3–6)
- Custodian-to-Addepar nightly pipeline:
  - Validate SFTP access, file specs, and Addepar intake; finalize file/folder naming conventions and EFS archival structure.
  - Build hash-based dedupe, job polling, and Teams reporting.
- Zoom workflow expansion:
  - Add recording/transcript upload to SharePoint and links in CRM.
- Canoe intake pipeline (initial):
  - Connect mailbox → Canoe upload → parse-complete webhook → transform to Addepar CSV → SFTP import.

Phase 3: Advanced Integrations (Weeks 7–12)
- Client onboarding orchestration:
  - Redtail webhook/polling, DocuSign templates/roles, custodian routing (email/SFTP), SharePoint filing, CRM updates, compliance journaling.
  - Create Runbook dashboard in SharePoint/Teams for status and exceptions.
- Contact sync bi-directional (optional):
  - Define authoritative fields and merge rules; implement conflict handling and audit expansion.
- Venn API enhancement (if accessible):
  - Switch from email-trigger to API-driven generation and retrieval with retry logic.

Cross-cutting security and monitoring (ongoing in all phases)
- Security:
  - Enforce MFA for all vendor portals; restrict n8n webhook URLs via API gateway and IP allowlists; validate signatures (Zoom/DocuSign).
  - Encrypt EFS, enable lifecycle policies, and backup/snapshot strategy.
- Monitoring:
  - Error Trigger nodes to email Ops and write to SharePoint log.
  - Weekly Teams digest summarizing last-run status, counts, exceptions.

## Next Steps

1) Appoint project owners (by October 11, 2025)
- Executive sponsor: COO
- Technical owner: IT Lead
- Process owners: Ops Lead (Data Ops), Advisors Lead (Onboarding), PM Lead (Reporting), Compliance Officer, CRM Admin

2) Access and prerequisites (by October 18, 2025)
- Provision n8n host in AWS with EFS mount and HTTPS.
- Create service accounts and credentials:
  - Microsoft 365 (Outlook, SharePoint, Teams, Contacts) with least-privilege scopes.
  - Zoom OAuth app and webhook validation.
  - Redtail API key.
  - Addepar SFTP/API credentials.
  - Canoe API/webhook (confirm plan).
  - Custodian SFTP and intake emails (Fidelity/Wealthscape/Jump).
- Confirm Global Relay journaled mailbox addresses.

3) Data and structure decisions (by October 18, 2025)
- Finalize:
  - File naming and expected delivery schedule per custodian.
  - EFS folder taxonomy (custodian, YYYY/MM/DD, client).
  - SharePoint site/library and client folder structure.
  - Redtail field mappings (contacts, activities, notes).
  - Contact sync rules (authoritative fields, unique IDs, merge policy).
  - DocuSign templates and recipient roles; Connect endpoint URL.

4) Build Phase 1 quick wins (October 21, 2025)
- Deliverables:
  - Venn email-ingest workflow live.
  - Redtail → M365 contact sync live with SharePoint audit.
  - Zoom → Redtail MVP live with compliance journaling.
- Success criteria:
  - Zero manual interventions in normal runs for 5 business days.
  - Teams/Outlook notifications with clear success/failure summaries.
  - SharePoint audit entries populated for every run.

5) Build Phase 2 workflows (November 15, 2025)
- Deliverables:
  - Custodian → Addepar nightly feed with EFS archival, dedupe, and job monitoring.
  - Zoom workflow enriched with recording/transcript storage.
  - Canoe intake to Addepar v1 live for a pilot set of clients.
- Success criteria:
  - 95%+ of daily custodian files processed automatically.
  - End-to-end runbook dashboard live in Teams/SharePoint.

6) Build Phase 3 advanced orchestrations (December 12, 2025)
- Deliverables:
  - End-to-end onboarding orchestration live for one custodian, then expand.
  - Optional bi-directional contact sync with conflict handling.
  - Venn API-based reporting (if enabled) replacing email fallback.
- Success criteria:
  - 8–12 hours/week reclaimed in onboarding; measurable reduction in NIGO/error rates.
  - Compliance confirmations captured automatically in Global Relay.

7) Governance and continuous improvement (ongoing)
- Monthly review of automation KPIs: time saved, exceptions, error causes, rework rates.
- Quarterly tool rationalization: clarify “Fidelity vs. Wealthscape” canonical source; reassess Zocks utility/API options.
- Security posture check: credentials rotation, audit logs, webhook access controls, vendor MFA enforcement.

By executing this roadmap with a self-hosted, open-source n8n approach, Crescent Grove Advisors can materially reduce manual workload, lower error rates, and accelerate client service—while maintaining strong security and compliance controls.