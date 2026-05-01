Platinum Tier: Always-On Cloud + Local Executive (Production-ish AI Employee)
Estimated time: 60+ hours
All Gold requirements plus:
Run the AI Employee on Cloud 24/7 (always-on watchers + orchestrator + health monitoring). You can deploy a Cloud VM (Oracle/AWS/etc.) - Oracle Cloud Free VMs can be used for this (subject to limits/availability).
Work-Zone Specialization (domain ownership):
Cloud owns: Email triage + draft replies + social post drafts/scheduling (draft-only; requires Local approval before send/post)
Local owns: approvals, WhatsApp session, payments/banking, and final “send/post” actions
Delegation via Synced Vault (Phase 1)
Agents communicate by writing files into:
/Needs_Action/<domain>/, /Plans/<domain>/, /Pending_Approval/<domain>/
Prevent double-work using:
/In_Progress/<agent>/ claim-by-move rule
single-writer rule for Dashboard.md (Local)
Cloud writes updates to /Updates/ (or /Signals/), and Local merges them into Dashboard.md.
For Vault sync (Phase 1) use Git (recommended) or Syncthing.
Claim-by-move rule: first agent to move an item from /Needs_Action to /In_Progress/<agent>/ owns it; other agents must ignore it.
Security rule: Vault sync includes only markdown/state. Secrets never sync (.env, tokens, WhatsApp sessions, banking creds). So Cloud never stores or uses WhatsApp sessions, banking credentials, or payment tokens.
Deploy Odoo Community on a Cloud VM (24/7) with HTTPS, backups, and health monitoring; integrate Cloud Agent with Odoo via MCP for draft-only accounting actions and Local approval for posting invoices/payments.
Optional A2A Upgrade (Phase 2): Replace some file handoffs with direct A2A messages later, while keeping the vault as the audit record
Platinum demo (minimum passing gate): Email arrives while Local is offline → Cloud drafts reply + writes approval file → when Local returns, user approves → Local executes send via MCP → logs → moves task to /Done.
