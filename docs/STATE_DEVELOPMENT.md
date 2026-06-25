# State Development

## Tickets

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

As I wrote in [Data Handling](docs/DATA_HANDLING.md), access from a wrong role should result in a 403 Forbidden error.

## Transitions - Committee Decision Category A (No Funding)

| Method | Path | From | Role | Decision | To |
|---|---|---|---|---|---|
| POST | /requests | `new` (funding not required) | submitter | | `pending` |
| POST | .../committee-decision | `pending` | committee | `proceed_independently` | `approved` |
| POST | .../committee-decision | `pending` | committee | `collaboration_recommended` | `approved` |
| POST | .../committee-decision | `pending` | committee | `hold` | `on_hold` |
| POST | .../committee-decision | `pending` | committee | `search_insufficient` | `pending` (redo) |
| POST | .../committee-decision | `pending` | committee | `reject` | `rejected` (terminal) |
| POST | .../resume | `on_hold` | committee | | `pending` |

## Transitions - Committee Decision Category B (Funding Required)

| Method | Path | From | Role | Decision | To |
|---|---|---|---|---|---|
| POST | /requests | `new` (funding required) | submitter | | `pending` |
| POST | .../committee-decision | `pending` or `under_review` | committee | `request_presentation` | `under_review`, presentation_status `requested` |
| POST | .../committee-decision | `pending` or `under_review` | committee | `combine_existing` | merged (terminal) |
| POST | .../committee-decision | `pending` or `under_review` | committee | `enhance_search` | `pending` (redo) |
| POST | .../committee-decision | `pending` or `under_review` | committee | `reject` | `rejected` (terminal) |
| POST | .../presentation | `under_review`, presentation_status `requested` | committee | | `under_review`, presentation_status `scheduled` |
| POST | .../presentation-outcome | `under_review`, presentation_status `scheduled` | committee | `advanced` | `under_review`, presentation_status `completed` |
| POST | .../presentation-outcome | `under_review`, presentation_status `scheduled` | committee | `not_advanced` | `rejected` (terminal) |
| POST | .../funding-decision | `under_review`, presentation_status `completed`, funding_status `pending` | management | `go` | `approved`, funding_status ``approved`` |
| POST | .../funding-decision | `under_review`, presentation_status `completed`, funding_status `pending` | management | `no_go` | `rejected` (terminal), funding_status `denied` |

### Transitions — Both A and B

| Method | Path | From | Role | Decision | To |
|---|---|---|---|---|---|
| PATCH | /requests/:id | `pending` after a redo | submitter | | `pending` |
| POST | .../execution | `approved` | committee or management | `start` | `in_progress` |
| POST | .../execution | `in_progress` | committee or management | `complete` | `completed` (terminal) |
| POST | .../comments | any non terminal status | any role | | |

## Incorrect State Transitions

- Funding a Category A (no funding) request
- Changing a presentation outcome before a date is set
- Changing a request after a terminal (rejected, completed, or merged) status