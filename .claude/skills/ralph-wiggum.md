# Skill: Ralph Wiggum Loop

## Description
Autonomous multi-step task completion loop. Keeps Claude working on a task until it's marked complete (moved to /Done folder). Implements the "Stop hook" pattern from the hackathon spec.

> "I'm helping!" - Ralph Wiggum

## Pattern
```
1. Task created in /Needs_Action/
         │
         ▼
2. Ralph Wiggum loop starts
         │
         ▼
3. Execute step → Check if in /Done/
         │            │
         NO           YES
         │            │
         ▼            ▼
    Continue      Stop loop
    iterating
```

## Key Features
- **Persistence**: Saves state to `.ralph_state.json`
- **Max iterations**: Prevents infinite loops (default: 10)
- **Completion check**: Task must be in /Done to exit
- **Logging**: Full execution log in /Logs/

## Usage

### Programmatic
```python
from ralph_wiggum import RalphWiggum

ralph = RalphWiggum("/path/to/vault", max_iterations=10)

def my_step():
    # Do one step of work
    return "Step completed"

result = ralph.run_until_complete("TASK_001", my_step)
# Returns: {'task_id': 'TASK_001', 'status': 'completed', 'iterations': 3}
```

### Process Task File
```python
result = ralph.process_task_file(Path("/vault/Needs_Action/task.md"))
```

### Test Run
```bash
uv run python src/ai_employee_watchers/ralph_wiggum.py
```

## Completion Criteria
Task is considered complete when:
1. File is found in /Done/ folder, OR
2. File content in /Done/ contains the task_id

## Exit Conditions
- Task moved to /Done → **Success**
- Max iterations reached → **Incomplete**
- Task file deleted/cancelled → **Aborted**

## Output
```json
{
  "task_id": "TASK_001",
  "status": "completed",
  "iterations": 3,
  "log_file": "/Logs/ralph_wiggum_TASK_001_*.json"
}
```

---
*AI Employee Gold Tier Skill*
