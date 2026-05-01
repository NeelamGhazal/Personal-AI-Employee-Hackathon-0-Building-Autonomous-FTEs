# error_handler.py - Centralized error handling with recovery and graceful degradation
import logging
import json
import traceback
from pathlib import Path
from datetime import datetime
from functools import wraps
from enum import Enum
from typing import Callable, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ErrorHandler')


class ErrorSeverity(Enum):
    LOW = 'low'           # Non-critical, can continue
    MEDIUM = 'medium'     # Important but recoverable
    HIGH = 'high'         # Critical, needs attention
    FATAL = 'fatal'       # System cannot continue


class RecoveryStrategy(Enum):
    RETRY = 'retry'           # Retry the operation
    FALLBACK = 'fallback'     # Use fallback value
    SKIP = 'skip'             # Skip and continue
    ABORT = 'abort'           # Stop execution
    NOTIFY = 'notify'         # Log and notify, continue


class ErrorHandler:
    """Centralized error handling with recovery strategies"""

    def __init__(self, vault_path: str, max_retries: int = 3):
        self.vault_path = Path(vault_path)
        self.logs_path = self.vault_path / 'Logs'
        self.logs_path.mkdir(parents=True, exist_ok=True)

        self.errors_path = self.vault_path / 'Logs' / 'errors'
        self.errors_path.mkdir(parents=True, exist_ok=True)

        self.max_retries = max_retries
        self.error_counts = {}  # Track error frequency

    def log_error(self, error: Exception, context: str, severity: ErrorSeverity,
                  additional_info: dict = None) -> Path:
        """Log error to file"""
        timestamp = datetime.now()
        error_id = f"ERR_{timestamp.strftime('%Y%m%d_%H%M%S')}_{id(error)}"

        error_data = {
            'error_id': error_id,
            'timestamp': timestamp.isoformat(),
            'context': context,
            'severity': severity.value,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'additional_info': additional_info or {}
        }

        # Write error log
        error_file = self.errors_path / f'{error_id}.json'
        error_file.write_text(json.dumps(error_data, indent=2))

        # Also log to standard logger
        logger.error(f'[{severity.value.upper()}] {context}: {error}')

        # Track error frequency
        error_key = f"{context}:{type(error).__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

        return error_file

    def should_retry(self, context: str, error: Exception) -> bool:
        """Determine if operation should be retried"""
        error_key = f"{context}:{type(error).__name__}"
        return self.error_counts.get(error_key, 0) <= self.max_retries

    def get_fallback_value(self, context: str, default: Any = None) -> Any:
        """Get fallback value for failed operation"""
        fallbacks = {
            'odoo_connection': {'status': 'disconnected', 'data': []},
            'gmail_fetch': {'messages': [], 'status': 'unavailable'},
            'whatsapp_fetch': {'messages': [], 'status': 'unavailable'},
            'social_post': {'status': 'queued', 'message': 'Will retry later'},
            'file_read': '',
            'file_write': False,
        }
        return fallbacks.get(context, default)

    def handle(self, error: Exception, context: str,
               severity: ErrorSeverity = ErrorSeverity.MEDIUM,
               strategy: RecoveryStrategy = RecoveryStrategy.FALLBACK,
               fallback_value: Any = None,
               additional_info: dict = None) -> Any:
        """Handle error with specified recovery strategy"""

        # Log the error
        self.log_error(error, context, severity, additional_info)

        # Apply recovery strategy
        if strategy == RecoveryStrategy.RETRY:
            if self.should_retry(context, error):
                logger.info(f'Retrying {context}...')
                return {'action': 'retry', 'attempts': self.error_counts.get(f"{context}:{type(error).__name__}", 0)}
            else:
                logger.warning(f'Max retries exceeded for {context}')
                return self.get_fallback_value(context, fallback_value)

        elif strategy == RecoveryStrategy.FALLBACK:
            fallback = fallback_value if fallback_value is not None else self.get_fallback_value(context)
            logger.info(f'Using fallback for {context}: {type(fallback).__name__}')
            return fallback

        elif strategy == RecoveryStrategy.SKIP:
            logger.info(f'Skipping {context} due to error')
            return None

        elif strategy == RecoveryStrategy.NOTIFY:
            # Create notification file
            self._create_notification(context, error, severity)
            return None

        elif strategy == RecoveryStrategy.ABORT:
            logger.critical(f'Aborting due to error in {context}')
            raise error

        return None

    def _create_notification(self, context: str, error: Exception, severity: ErrorSeverity):
        """Create notification file for error"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        notification_path = self.vault_path / 'Needs_Action'
        notification_path.mkdir(parents=True, exist_ok=True)

        filename = f"ERROR_NOTIFICATION_{timestamp}.md"
        filepath = notification_path / filename

        content = f'''---
type: error_notification
severity: {severity.value}
context: {context}
detected_at: {datetime.now().isoformat()}
status: pending
---

# Error Notification

## Severity
**{severity.value.upper()}**

## Context
{context}

## Error
{type(error).__name__}: {str(error)}

## Action Required
- [ ] Investigate error
- [ ] Apply fix
- [ ] Test resolution

---
*Generated by ErrorHandler*
'''
        filepath.write_text(content)
        logger.info(f'Error notification created: {filename}')


# Decorator for automatic error handling
def with_error_handling(context: str,
                       severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                       strategy: RecoveryStrategy = RecoveryStrategy.FALLBACK,
                       fallback_value: Any = None):
    """Decorator to add error handling to functions"""

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Try to find vault_path in args
            vault_path = kwargs.get('vault_path')
            if vault_path is None and len(args) > 0:
                # Check if first arg is self with vault_path attribute
                if hasattr(args[0], 'vault_path'):
                    vault_path = str(args[0].vault_path)

            if vault_path is None:
                vault_path = '/tmp/ai_employee_errors'

            handler = ErrorHandler(vault_path)

            try:
                return func(*args, **kwargs)
            except Exception as e:
                return handler.handle(
                    error=e,
                    context=f"{context}:{func.__name__}",
                    severity=severity,
                    strategy=strategy,
                    fallback_value=fallback_value,
                    additional_info={'function': func.__name__, 'args': str(args)[:100]}
                )

        return wrapper
    return decorator


# Graceful degradation utilities
class GracefulDegradation:
    """Utilities for graceful degradation"""

    @staticmethod
    def with_timeout(func: Callable, timeout: int, fallback: Any = None):
        """Execute function with timeout, return fallback on timeout"""
        import signal

        def handler(signum, frame):
            raise TimeoutError(f"Function timed out after {timeout}s")

        try:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout)
            result = func()
            signal.alarm(0)
            return result
        except TimeoutError:
            logger.warning(f'Timeout in {func.__name__}, using fallback')
            return fallback
        except Exception as e:
            logger.warning(f'Error in {func.__name__}: {e}, using fallback')
            return fallback

    @staticmethod
    def circuit_breaker(failure_threshold: int = 5, reset_timeout: int = 60):
        """Circuit breaker pattern for protecting failing services"""
        state = {'failures': 0, 'last_failure': None, 'open': False}

        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if state['open']:
                    # Check if reset timeout has passed
                    if state['last_failure']:
                        elapsed = (datetime.now() - state['last_failure']).seconds
                        if elapsed >= reset_timeout:
                            state['open'] = False
                            state['failures'] = 0
                            logger.info(f'Circuit breaker reset for {func.__name__}')
                        else:
                            logger.warning(f'Circuit breaker open for {func.__name__}')
                            return None

                try:
                    result = func(*args, **kwargs)
                    state['failures'] = 0
                    return result
                except Exception as e:
                    state['failures'] += 1
                    state['last_failure'] = datetime.now()

                    if state['failures'] >= failure_threshold:
                        state['open'] = True
                        logger.error(f'Circuit breaker opened for {func.__name__}')

                    raise e

            return wrapper
        return decorator


def main():
    """Test error handling"""
    import sys

    default_vault = Path(__file__).parent.parent.parent.parent / 'AI_Employee_Vault'
    handler = ErrorHandler(str(default_vault))

    print("=" * 60)
    print("ERROR HANDLER TEST")
    print("=" * 60)

    # Test 1: Log an error
    try:
        raise ValueError("Test error for demonstration")
    except Exception as e:
        error_file = handler.log_error(
            e, "test_context", ErrorSeverity.MEDIUM,
            {'test': True, 'module': 'error_handler'}
        )
        print(f"✓ Error logged to: {error_file}")

    # Test 2: Handle with fallback
    try:
        raise ConnectionError("Simulated connection failure")
    except Exception as e:
        result = handler.handle(
            e, "odoo_connection",
            severity=ErrorSeverity.MEDIUM,
            strategy=RecoveryStrategy.FALLBACK
        )
        print(f"✓ Fallback result: {result}")

    # Test 3: Create notification
    try:
        raise RuntimeError("Critical system error")
    except Exception as e:
        handler.handle(
            e, "critical_operation",
            severity=ErrorSeverity.HIGH,
            strategy=RecoveryStrategy.NOTIFY
        )
        print("✓ Notification created")

    print("=" * 60)
    print("ERROR HANDLER TEST COMPLETE")
    print("=" * 60)

    # Show error files
    print("\nError files created:")
    for f in handler.errors_path.glob('*.json'):
        print(f"  - {f.name}")


if __name__ == '__main__':
    main()
