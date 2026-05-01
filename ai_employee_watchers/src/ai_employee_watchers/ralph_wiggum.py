# ralph_wiggum.py - Autonomous multi-step task completion loop
# "I'm helping!" - Ralph Wiggum
#
# This implements the Ralph Wiggum pattern from the hackathon spec:
# A Stop hook that prevents exit until the task is complete,
# re-injecting the prompt to keep Claude working autonomously.

import logging
import sys
import json
import time
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('RalphWiggum')


class TaskState:
    """Represents the state of a task being worked on"""

    def __init__(self, task_id: str, vault_path: str):
        self.task_id = task_id
        self.vault_path = Path(vault_path)
        self.state_file = self.vault_path / '.ralph_state.json'
        self.iterations = 0
        self.max_iterations = 10
        self.started_at = datetime.now()
        self.last_output = ''
        self.status = 'pending'

    def save(self):
        """Save state to file"""
        state = {
            'task_id': self.task_id,
            'iterations': self.iterations,
            'max_iterations': self.max_iterations,
            'started_at': self.started_at.isoformat(),
            'last_output': self.last_output[:1000],  # Truncate
            'status': self.status,
            'updated_at': datetime.now().isoformat()
        }
        self.state_file.write_text(json.dumps(state, indent=2))

    def load(self):
        """Load state from file"""
        if self.state_file.exists():
            state = json.loads(self.state_file.read_text())
            self.iterations = state.get('iterations', 0)
            self.last_output = state.get('last_output', '')
            self.status = state.get('status', 'pending')
            return True
        return False


class RalphWiggum:
    """
    The Ralph Wiggum loop - keeps Claude working until task is complete.

    Pattern:
    1. Orchestrator creates state file with prompt
    2. Claude works on task
    3. Claude tries to exit
    4. Stop hook checks: Is task file in /Done?
       - YES → Allow exit (complete)
       - NO → Block exit, re-inject prompt, continue
    5. Repeat until complete or max iterations
    """

    def __init__(self, vault_path: str, max_iterations: int = 10):
        self.vault_path = Path(vault_path)
        self.max_iterations = max_iterations

        self.needs_action = self.vault_path / 'Needs_Action'
        self.in_progress = self.vault_path / 'In_Progress'
        self.done_path = self.vault_path / 'Done'
        self.logs_path = self.vault_path / 'Logs'

        # Ensure folders exist
        for path in [self.needs_action, self.in_progress, self.done_path, self.logs_path]:
            path.mkdir(parents=True, exist_ok=True)

        self.current_task: Optional[TaskState] = None

    def is_task_complete(self, task_id: str) -> bool:
        """Check if task is in /Done folder"""
        for file in self.done_path.glob(f'*{task_id}*'):
            return True

        # Also check if source file was moved to Done
        for file in self.done_path.glob('*.md'):
            content = file.read_text()
            if task_id in content:
                return True

        return False

    def should_continue(self, task: TaskState) -> tuple[bool, str]:
        """
        The Ralph Wiggum decision point.
        Returns (should_continue, reason)
        """
        # Check if task is complete
        if self.is_task_complete(task.task_id):
            return False, 'Task completed - found in /Done'

        # Check iteration limit
        if task.iterations >= task.max_iterations:
            return False, f'Max iterations ({task.max_iterations}) reached'

        # Check if task file still exists (wasn't deleted/cancelled)
        task_exists = False
        for folder in [self.needs_action, self.in_progress]:
            for file in folder.glob(f'*{task.task_id}*'):
                task_exists = True
                break

        if not task_exists:
            return False, 'Task file no longer exists'

        return True, 'Task not yet complete'

    def execute_step(self, task: TaskState, step_function: Callable[[], Any]) -> Any:
        """Execute one step of the task"""
        task.iterations += 1
        logger.info(f'[Ralph] Iteration {task.iterations}/{task.max_iterations} for {task.task_id}')

        try:
            result = step_function()
            task.last_output = str(result)[:1000]
            task.save()
            return result
        except Exception as e:
            task.last_output = f'Error: {str(e)}'
            task.save()
            raise

    def run_until_complete(self, task_id: str, step_function: Callable[[], Any],
                          check_interval: float = 1.0) -> dict:
        """
        Run the Ralph Wiggum loop until task is complete.

        Args:
            task_id: Unique identifier for the task
            step_function: Function to call each iteration
            check_interval: Seconds between iterations

        Returns:
            dict with completion status and details
        """
        task = TaskState(task_id, str(self.vault_path))
        task.max_iterations = self.max_iterations
        self.current_task = task

        logger.info('')
        logger.info('=' * 60)
        logger.info("RALPH WIGGUM LOOP ACTIVATED")
        logger.info(f"I'm helping! Task: {task_id}")
        logger.info('=' * 60)

        results = []

        while True:
            should_continue, reason = self.should_continue(task)

            if not should_continue:
                logger.info(f'[Ralph] Stopping: {reason}')
                break

            logger.info(f'[Ralph] Continuing... {reason}')

            try:
                result = self.execute_step(task, step_function)
                results.append({
                    'iteration': task.iterations,
                    'result': str(result)[:200],
                    'timestamp': datetime.now().isoformat()
                })
            except Exception as e:
                logger.error(f'[Ralph] Step failed: {e}')
                results.append({
                    'iteration': task.iterations,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })

            time.sleep(check_interval)

        # Final status
        task.status = 'completed' if self.is_task_complete(task_id) else 'incomplete'
        task.save()

        # Log completion
        log_file = self.logs_path / f'ralph_wiggum_{task_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        log_file.write_text(json.dumps({
            'task_id': task_id,
            'status': task.status,
            'total_iterations': task.iterations,
            'max_iterations': task.max_iterations,
            'results': results,
            'completed_at': datetime.now().isoformat()
        }, indent=2))

        logger.info('')
        logger.info('=' * 60)
        logger.info(f"RALPH WIGGUM COMPLETE: {task.status.upper()}")
        logger.info(f"Iterations: {task.iterations}/{task.max_iterations}")
        logger.info('=' * 60)

        return {
            'task_id': task_id,
            'status': task.status,
            'iterations': task.iterations,
            'log_file': str(log_file)
        }

    def process_task_file(self, task_file: Path) -> dict:
        """Process a task file using Ralph Wiggum loop"""
        task_id = task_file.stem

        def step():
            # Read task file
            content = task_file.read_text()

            # Simulate processing (in real implementation, this would
            # call Claude Code or execute the task actions)
            logger.info(f'[Ralph] Processing: {task_file.name}')

            # For demo: move to Done after 3 iterations
            if self.current_task and self.current_task.iterations >= 3:
                dest = self.done_path / task_file.name
                task_file.rename(dest)
                logger.info(f'[Ralph] Moved to Done: {dest.name}')
                return 'Task completed and moved to Done'

            return f'Processing iteration {self.current_task.iterations if self.current_task else 0}'

        return self.run_until_complete(task_id, step)


def main():
    """Test Ralph Wiggum loop"""
    import sys

    default_vault = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault'

    ralph = RalphWiggum(str(default_vault), max_iterations=5)

    print("=" * 60)
    print("RALPH WIGGUM LOOP TEST")
    print("I'm helping!")
    print("=" * 60)

    # Create a test task
    test_task_id = f"TEST_RALPH_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    test_file = ralph.needs_action / f'{test_task_id}.md'
    test_file.write_text(f'''---
type: test_task
created_at: {datetime.now().isoformat()}
---

# Test Task for Ralph Wiggum

This is a test task to verify the Ralph Wiggum loop works correctly.

## Actions
- [ ] Process step 1
- [ ] Process step 2
- [ ] Process step 3
- [ ] Complete task
''')

    print(f"Created test task: {test_file}")
    print("")

    # Run the loop
    result = ralph.process_task_file(test_file)

    print("")
    print("Results:")
    print(f"  Status: {result['status']}")
    print(f"  Iterations: {result['iterations']}")
    print(f"  Log: {result['log_file']}")

    print("")
    print("=" * 60)
    print("RALPH WIGGUM TEST COMPLETE")
    print("=" * 60)


if __name__ == '__main__':
    main()
