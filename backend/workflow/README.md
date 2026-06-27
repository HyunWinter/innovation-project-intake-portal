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

## Flow

| Type | Description |
|---|---|
| Write | Transitions -> Service -> Request |
| Read | Transitions + Request -> Engine -> UI |