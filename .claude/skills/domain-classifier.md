# Skill: Domain Classifier

## Description
Automatically classify incoming items as Personal or Business and route them to the appropriate folder structure.

## Trigger
Run when new items arrive in the generic /Inbox folder or when watchers detect new content.

## Instructions

1. **Analyze incoming content**
   - Extract sender, subject, and body text
   - Check source type (email, WhatsApp, file)

2. **Apply classification rules**

   **Business Keywords:**
   - Financial: invoice, payment, billing, revenue, expense
   - Operations: client, project, deadline, meeting, contract
   - Marketing: campaign, social media, promotion, analytics

   **Personal Keywords:**
   - Life: family, friend, birthday, vacation, personal
   - Health: doctor, appointment, medication
   - Personal finance: bank statement, rent, subscription

3. **Score and classify**
   - Count keyword matches for each domain
   - Higher score determines classification
   - Default to Personal if tied or uncertain

4. **Route to appropriate folder**
   - Business items → `/Business/Needs_Action/`
   - Personal items → `/Personal/Needs_Action/`

## Example Usage
```bash
uv run python src/ai_employee_watchers/domain_classifier.py --test
```

## Integration
The classifier is automatically used by:
- `whatsapp_watcher.py`
- `gmail_watcher.py`
- `filesystem_watcher.py`

## Output
- Files routed to `/Personal/Needs_Action/` or `/Business/Needs_Action/`
- Classification logged in audit trail

---
*AI Employee Gold Tier Skill*
