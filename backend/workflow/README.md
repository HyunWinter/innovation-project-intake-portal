# Workflow

The state machine that handles all transition rules.

## Structure

| File | Description |
|---|---|
| `transitions.py` | The transition rules for: |
| | Which roles can run an action |
| | From state and to state |
| | Data required |
| | What it changes |
| `exceptions.py` | Maps each errors to an HTTP status | 
| `service.py` | `apply_transition`: Check the request against the rules |
| | `AuditEvent`: Records state changes. |
| `engine.py` | Read only |
| | `available_actions`: What this user can do now. |
| | `workflow_progress`: Request progress for the UI. |

## Flow

| Type | Description |
|---|---|
| Write | Transitions -> Service -> Request |
| Read | Transitions + Request -> Engine -> UI |