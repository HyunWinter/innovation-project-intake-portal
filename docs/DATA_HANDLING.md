# Data Handling

## Tickets


## Requirements

- No in-memory stores
- Migration/schema file to recreate from empty
- Request entity with all fields + workflow state columns
- Typed audit-trail entity
- Soft deletes

## Data Models

### User (Mandatory)

| Entity | Type | Description |
|---|---|---|
| id | uuid | primary key |
| email | string | unique |
| name | string | |
| role | Role | for permission check |
| password | string | hashed |
| created_at | datetime | |

Requirements specifically state that role checks should be enforced in the server side. Wrong role should result in a 403 Forbidden error.

| Enum | Values |
|---|---|
| Role | submitter |
| | committee |
| | management |

### Request / Submission Form (Mandatory)

#### Workflow

| Field | Type | Description |
|---|---|---|
| id | uuid | primary key |
| category | Category | derived from funding_required / immutable |
| status | Status | default pending |
| committee_decision | CommitteeDecision | nullable, last committee outcome |
| presentation_status | PresentationStatus | default not_requested |
| funding_status | FundingStatus | not_required for A, pending for B |
| decision_reasoning | text | nullable |
| decision_made_by | User FK | nullable |
| decision_made_at | datetime | nullable |

| Enum | Values |
|---|---|
| Category | A (no funding) |
| | B (funding required) |
| Status | pending |
| | under_review |
| | approved |
| | in_progress |
| | completed |
| | rejected |
| | on_hold |
| | merged |
| CommitteeDecision | proceed_independently |
| | collaboration_recommended |
| | hold |
| | search_insufficient |
| | request_presentation |
| | combine_existing |
| | enhance_search |
| | reject |
| FundingStatus | not_required |
| | pending |
| | approved |
| | denied |

#### 1 · Prior-Art

| Field | Type | Description |
|---|---|---|
| keywords | text | |
| similar_projects_found | text | |
| differentiation | text | |
| collaboration_opportunities | text | |

#### 2 · Basic Info

| Field | Type | Notes |
|---|---|---|
| contact_name | string | required |
| contact_email | string | required |
| site_or_team | string | |
| tech_category | TechCategory | |
| collaboration_interest | boolean | |

Unlike other Enum fields in this project, I can see tech categories might change over time. So they could be stored in a separate table (e.g. snippet in Django) for easy updates.

| Enum | Values |
|---|---|
| TechCategory | ai_ml |
| | automation |
| | business_process |
| | other |

#### 3 · Scope

| Field | Type | Notes |
|---|---|---|
| title | string | required |
| description | text | required |
| objectives | text | required |
| outcomes | text | |
| start_date | date | |
| end_date | date | must be >= start_date |
| phases | jsonb | list of phases |

#### 4 · Resources

| Field | Type | Notes |
|---|---|---|
| funding_required | boolean | true = category B |
| personnel | text | |
| equipment | text | |
| budget | decimal | required and must be > 0 when funded |
| estimated_roi | text | required when funded |

#### Others

| Field | Type | Notes |
|---|---|---|
| presentation_date | datetime | nullable, set on schedule |
| presentation_requirements | text | nullable, set on request_presentation |
| expected_resume_date | date | nullable, set on hold |
| suggested_collaborators | jsonb | nullable, set on collaboration_recommended |
| submitter | User FK | |
| created_at | datetime | |
| updated_at | datetime | |
| deleted_at | datetime | nullable, soft delete |

### DraftRequest (Not Mandatory)

Model for incomplete submissions for users to save/auto-save and resume later. Because data is saved in a json field, it should be validated on submit.

This model is also designed to accumulate data over time, but kept as a separate table to avoid bloating the main Request table. As our application scale, we can purge it periodically every ~30 days.

| Field | Type | Notes |
|---|---|---|
| id | uuid | primary key |
| author | User FK | |
| data | jsonb | should be validated on submit |
| created_at | datetime | |
| updated_at | datetime | nullable, soft delete |

### AuditEvent (Mandatory)

This model is for append only for the `typed audit-trail entity` purpose. One row written in the same transaction as every state change.

| Field | Type | Notes |
|---|---|---|
| id | uuid | primary key |
| request | Request FK | |
| actor | User FK | the person who triggered the change |
| event_type | string | transition or action name |
| from_status | Status | nullable |
| to_status | Status | nullable |
| payload | jsonb | structured, typed per event_type |
| created_at | datetime | |

Status Enum is located in Submission Form - Workflow section.

### Comment (Not Mandatory)

| Field | Type | Notes |
|---|---|---|
| id | uuid | primary key |
| request | Request FK | |
| author | User FK | |
| body | text | |
| created_at | datetime | |
| deleted_at | datetime | nullable, soft delete |
