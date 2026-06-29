# Quality Assurance

## Tickets

### 1. Unit tests
- [x] State machine tests
- [x] Validator tests

### 2. Integration tests
- [x] API endpoint and error contract tests
- [x] Authentication tests

### 3. Frontend tests
- [ ] Vitest

## Stack

- Django test runner
- Django Rest Framework `APIClient` for integration tests
- Temporary test database
- Vitest

## Run

```bash
cd backend

# All tests
docker compose exec backend python manage.py test

# Individual Tests
docker compose exec backend python manage.py test proposals.tests.test_state_machine
docker compose exec backend python manage.py test proposals.tests.test_validators
docker compose exec backend python manage.py test proposals.tests.test_api
docker compose exec backend python manage.py test accounts.tests
```

## Unit Tests

Call the component directly, no HTTP.

### State machine (`backend/proposals/tests/test_state_machine.py`)

| Test | Expected |
|---|---|
| Committee approval | approved and writes an audit row |
| Category A path | completed |
| Category B path | presentation, schedule, advance, fund |
| Hold then resume | pending |
| Comment | no changes to status and audit |
| Funding a category A request | rejected |
| Outcome before scheduled | rejected |
| Action after terminal | rejected |
| Wrong role | rejected |
| Missing field | rejected |
| Unknown action | rejected |

### Validators (`backend/proposals/tests/test_validators.py`)

| Test | Expected |
|---|---|
| end_date vs start_date | invalid, end_date error |
| Funded without budget | invalid, budget error |
| Funded budget not positive | invalid, budget error |
| Funded without ROI | invalid, estimated_roi error |
| Unfunded minimal | valid |
| Category A derivation | category A, funding not required |
| Category B derivation | category B, funding pending |
| Schedule past date | rejected |
| Schedule future date | passes |
| Schedule missing date | passes |
| Hold malformed date | rejected |
| Hold valid date | passes |
| Action without typed checks | passes |

## Integration Tests

Full stack through `APIClient`.

### API (`backend/proposals/tests/test_api.py`)

| Test | Expected |
|---|---|
| List | requires authentication (Anyone) |
| Create | returns 201 with derived category |
| Non-submitter create | rejected with 403 |
| Invalid create | returns 400 |
| Filter | returns only the matching category |
| Detail | returns available actions and workflow |
| Committee decision | approves over HTTP |
| Comment | saved over HTTP |
| Resubmit (owner) | updates the request |
| Resubmit (non-owner) | rejected with 403 |
| Illegal transition | returns 409 |
| Wrong role | returns 403 |
| Unknown action | returns 404 |
| Missing field | returns 400 with the field listed |

### Authentication (`backend/accounts/tests.py`)

| Test | Expected |
|---|---|
| Login token | carries role and name |
| Wrong password | returns 401 |
| No token | returns 401 |

## Frontend Tests (`frontend/tests`)