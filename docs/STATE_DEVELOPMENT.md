# State Development

## Tickets


## Permissions

| Personas | Can Do |
| :--- | :--- |
| **Submitter** | Create proposals |
| | View own request status |
| **Committee Member** | Review all requests |
| | Render decisions |
| | Schedule presentations |
| **Management** | Final funding go/no-go |
| **Anyone** | Read-only dashboard |

## API Endpoints

| Endpoint | Purpose |
| :--- | :--- |
| `POST /requests`  | Create |
| | Full server-side validation |
| `GET /requests ` | List |
| | Filter by status, category, funding, free-text |
| `GET /requests/:id` | Detail + audit trail |
| `POST …/committeedecision` | Committee renders outcome |
| `POST …/presentation` | Schedule presentation |
| `POST …/presentationoutcome` | Record outcome |
| `POST …/funding-decision` | Management go/no-go |
| `POST …/comments ` | Free-text comment |