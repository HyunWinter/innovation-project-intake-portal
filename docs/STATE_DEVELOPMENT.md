# State Development

## Tickets

### 1. Transition registry
- [x] Create workflow states and the transition table

### 2. Transition service
- [x] Create the apply_transition service that writes an audit row in one transaction

### 3. Engine
- [x] Create available_actions and workflow_progress

### 4. Serializers and validators
- [x] Create the request serializer with validation
- [x] Add decision payload validation

### 5. Read endpoints
- [x] Create GET /requests with filters
- [x] Create GET /requests/:id with audit trail

### 6. Transition endpoints
- [x] Create transition endpoints (committee-decision, presentation, presentation-outcome, funding-decision, comments, execution, resume, resubmit)
- [x] Enforce role permissions

### 7. Error contract
- [x] Implement error responses (400, 403, 404, 409)

## Permissions

| Personas | Can Do |
| --- | --- |
| **Submitter** | Create proposals |
| | View own request status |
| **Committee Member** | Review all requests |
| | Render decisions |
| | Schedule presentations |
| **Management** | Final funding go/no-go |
| **Anyone** | Read-only dashboard |

As I wrote in [Data Handling](DATA_HANDLING.md), access from a wrong role should result in a 403 Forbidden error.

## Reads

| Method | Path | Role | Purpose |
|---|---|---|---|
| GET | /requests | any role | List with filters (status, category, funding, free-text), paginated |
| GET | /requests/:id | any role | Detail with audit trail and comments |

## Transitions - Committee Decision Category A (No Funding)

| Method | Path | From | Role | Decision / Action | Required fields | To |
|---|---|---|---|---|---|---|
| POST | /requests | new (funding not required) | `submitter` | `create` | 4 sections | `pending` |
| POST | .../committee-decision | `pending` | `committee` | `proceed_independently` | `decision_reasoning` | `approved` |
| POST | .../committee-decision | `pending` | `committee` | `collaboration_recommended` | `decision_reasoning`, `suggested_collaborators` | `approved` |
| POST | .../committee-decision | `pending` | `committee` | `hold` | `decision_reasoning`, `expected_resume_date` | `on_hold` |
| POST | .../committee-decision | `pending` | `committee` | `search_insufficient` | `decision_reasoning` | `pending` (redo) |
| POST | .../committee-decision | `pending` | `committee` | `reject` | `decision_reasoning` | `rejected` (terminal) |
| POST | .../resume | `on_hold` | `committee` | `resume` | none | `pending` |

## Transitions — Committee Decision Category B (Funding Required)

| Method | Path | From | Role | Decision / Action | Required fields | To |
|---|---|---|---|---|---|---|
| POST | /requests | new (funding required) | `submitter` | `create` | 4 sections | `pending` |
| POST | .../committee-decision | `pending` or `under_review` | `committee` | `request_presentation` | `decision_reasoning`, `presentation_requirements` | `under_review`, `presentation_status` `requested` |
| POST | .../committee-decision | `pending` or `under_review` | `committee` | `combine_existing` | `decision_reasoning` | `merged` (terminal) |
| POST | .../committee-decision | `pending` or `under_review` | `committee` | `enhance_search` | `decision_reasoning` | `pending` (redo) |
| POST | .../committee-decision | `pending` or `under_review` | `committee` | `reject` | `decision_reasoning` | `rejected` (terminal) |
| POST | .../presentation | `under_review`, `presentation_status` `requested` | `committee` | `schedule` | `presentation_date` (future) | `under_review`, `presentation_status` `scheduled` |
| POST | .../presentation-outcome | `under_review`, `presentation_status` `scheduled` | `committee` | `advanced` | none | `under_review`, `presentation_status` `completed` |
| POST | .../presentation-outcome | `under_review`, `presentation_status` `scheduled` | `committee` | `not_advanced` | none | `rejected` (terminal) |
| POST | .../funding-decision | `under_review`, `presentation_status` `completed`, `funding_status` `pending` | `management` | `go` | `decision_reasoning` | `approved`, `funding_status` `approved` |
| POST | .../funding-decision | `under_review`, `presentation_status` `completed`, `funding_status` `pending` | `management` | `no_go` | `decision_reasoning` | `rejected` (terminal), `funding_status` `denied` |

## Transitions — Both A and B

| Method | Path | From | Role | Decision / Action | Required fields | To |
|---|---|---|---|---|---|---|
| PATCH | /requests/:id | `pending` | `submitter` | `resubmit` | 4 sections | `pending` |
| POST | .../execution | `approved` | `committee` or `management` | `start` | none | `in_progress` |
| POST | .../execution | `in_progress` | `committee` or `management` | `complete` | none | `completed` (terminal) |
| POST | .../comments | any non terminal status | any role | `comment` | `body` | no change |

## Incorrect State Transitions

- Funding a Category A (no funding) request
- Changing a presentation outcome before a date is set
- Changing a request after a terminal (rejected, completed, or merged) status