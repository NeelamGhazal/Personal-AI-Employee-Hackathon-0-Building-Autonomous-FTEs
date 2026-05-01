# Skill: Error Handler

## Description
Centralized error handling with recovery strategies and graceful degradation. Ensures system continues operating even when components fail.

## Recovery Strategies

### RETRY
Retry failed operation up to max_retries times.
```python
handler.handle(error, "context", strategy=RecoveryStrategy.RETRY)
```

### FALLBACK
Return a safe default value and continue.
```python
handler.handle(error, "odoo_connection", strategy=RecoveryStrategy.FALLBACK)
# Returns: {'status': 'disconnected', 'data': []}
```

### SKIP
Skip the failed operation and continue with next.
```python
handler.handle(error, "optional_task", strategy=RecoveryStrategy.SKIP)
```

### NOTIFY
Create notification file for human attention.
```python
handler.handle(error, "critical_op", strategy=RecoveryStrategy.NOTIFY)
# Creates: /Needs_Action/ERROR_NOTIFICATION_*.md
```

### ABORT
Stop execution for fatal errors.
```python
handler.handle(error, "critical", strategy=RecoveryStrategy.ABORT)
```

## Built-in Fallback Values
| Context | Fallback |
|---------|----------|
| odoo_connection | `{'status': 'disconnected', 'data': []}` |
| gmail_fetch | `{'messages': [], 'status': 'unavailable'}` |
| whatsapp_fetch | `{'messages': [], 'status': 'unavailable'}` |
| social_post | `{'status': 'queued', 'message': 'Will retry later'}` |

## Circuit Breaker Pattern
Automatically disable failing services to prevent cascade failures:
```python
@GracefulDegradation.circuit_breaker(failure_threshold=5, reset_timeout=60)
def call_external_service():
    ...
```

## Decorator Usage
```python
@with_error_handling("my_context", severity=ErrorSeverity.MEDIUM)
def my_function():
    ...
```

## Error Logs
All errors logged to `/Logs/errors/ERR_*.json`

---
*AI Employee Gold Tier Skill*
