# Skill: CEO Briefing

## Description
Generate comprehensive weekly business and accounting audit with executive briefing. Pulls data from all integrated systems and produces a formatted report.

## Trigger
- Run weekly (recommended: Monday morning)
- Run on-demand with `/ceo-briefing` command

## Instructions

1. **Gather financial data from Odoo**
   - Total revenue (paid invoices)
   - Outstanding invoices (unpaid)
   - Recent payments received
   - Partner/customer counts

2. **Aggregate social media metrics**
   - Posts published per platform (Facebook, Instagram, Twitter)
   - Recent post summaries

3. **Compile communication stats**
   - Emails processed
   - WhatsApp messages handled
   - Response rates

4. **Review task pipeline**
   - Items in Needs_Action (Personal + Business)
   - Pending approvals
   - Completed tasks
   - Error count from logs

5. **Generate health indicators**
   - Cash flow status (Healthy/Warning/Critical)
   - Task backlog status
   - System health

6. **Output formatted briefing**
   - Save to `/Briefings/CEO_BRIEFING_YYYY-MM-DD.md`
   - Include actionable insights and recommendations

## Example Usage
```bash
uv run python src/ai_employee_watchers/ceo_briefing.py
```

## Output
```markdown
# CEO Briefing - Week of [Date]

## Financial Summary
- Revenue: $X,XXX
- Outstanding: $X,XXX
- Cash Flow: [STATUS]

## Activity Summary
- Social Posts: X
- Emails: X
- Tasks Completed: X

## Action Items
- [ ] Review pending approvals
- [ ] Follow up on outstanding invoices
```

---
*AI Employee Gold Tier Skill*
