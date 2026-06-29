# Quality Assurance

## Tickets

### 1. Unit tests
- [ ] State machine tests
- [ ] Validator tests

### 2. Integration tests
- [ ] API endpoint and error contract tests
- [ ] Authentication tests

### 3. Frontend tests
- [ ] Vitest

## Stack

- Django test runner
- Django Rest Framework `APIClient` for integration tests
- Temporary test database

## Run

```bash
docker compose exec backend python manage.py test
docker compose exec backend python manage.py test proposals.tests.test_state_machine
```

## Unit Tests

Call the component directly, no HTTP.

### State machine (`proposals/tests/test_state_machine.py`)

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

### Validators (`proposals/tests/test_validators.py`)

| Test | Expected |
|---|---|
| end_date vs start_date | end must be after start |
| Funded budget | must be positive |
| Funded ROI | required |
| Unfunded minimal | valid |
| Category derivation | A when unfunded, B when funded |
| Schedule date | must be in the future |
| Hold date | must be well formed |

## Integration Tests

Full stack through `APIClient`.

### API (`proposals/tests/test_api.py`)

| Test | Expected |
|---|---|
| List | requires authentication (Anyone) |
| Filter | returns only the matching category |
| Create | returns 201 with derived category |
| Non-submitter create | rejected |
| Invalid create | returns 400 |
| Detail | returns available actions and workflow |
| Committee decision | approves over HTTP |
| Comment | saved over HTTP |
| Resubmit | owner only |
| Error contract | 400, 403, 404, 409 |

### Authentication (`accounts/tests.py`)

| Test | Expected |
|---|---|
| Login token | carries role and name |
| Wrong password | returns 401 |
| No token | returns 401 |
