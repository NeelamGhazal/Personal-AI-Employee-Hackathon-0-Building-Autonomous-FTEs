# Skill: Create Plan

## Description
Create a structured Plan.md file for a given task, following the human-in-the-loop workflow.

## Trigger
Run this skill when a task requires multiple steps or human approval.

## Arguments
- `task_description`: Description of the task to plan
- `source_file`: (Optional) The source file that triggered this plan

## Instructions

1. **Analyze the task**
   - Identify the objective
   - Determine required steps
   - Check against Company_Handbook.md rules

2. **Identify approval requirements**
   Review the task against Permission Boundaries in Company_Handbook.md:
   - Auto-approve actions: Reading files, creating plans, drafting
   - Requires approval: Sending emails, payments, external actions

3. **Create Plan.md file**
   Create a new file in `/Plans/` with format:
   ```
   PLAN_<task_type>_<timestamp>.md
   ```

4. **Plan structure**
   ```markdown
   ---
   created: <ISO timestamp>
   status: pending_approval | auto_approved
   source: <source_file if any>
   ---

   ## Objective
   <Clear statement of goal>

   ## Steps
   - [ ] Step 1
   - [ ] Step 2
   - [ ] Step 3

   ## Approval Required
   <List actions needing approval, or "None - auto-approved">

   ## Risk Assessment
   <Low | Medium | High>
   ```

5. **Create approval file if needed**
   If any step requires approval, create corresponding file in `/Pending_Approval/`

## Example Usage
```
/create-plan "Generate and send invoice to Client A for $1500"
```

## Output
Path to created Plan.md file and any approval files created.
