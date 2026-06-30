# Interface Design

## Tickets

### 1. Foundation
- [x] Router
- [x] Auth store (login, JWT role and name, logout)
- [ ] API store

### 2. Login and Navbar
- [x] Login page
- [x] Navbar with current user and logout

### 3. Dashboard
- [ ] Stat tiles
- [ ] Filterable paginated table
- [ ] My requests toggle
- [ ] Overdue indicator
- [ ] New Request button

### 4. New Request form
- [ ] Four sections with inline validation and conditional budget/ROI

### 5. Review screen
- [ ] Status header
- [ ] Workflow progress
- [ ] Role and state gated actions
- [ ] Decision modal
- [ ] Comment and audit timeline

## Requirements

### Login Page
- Email
- Password

### Dashboard
- Stat tiles (Total / Pending / Approved / In Progress)
- Filterable paginated table
- My requests  toggle
- Overdue indicator
- New Request button

### New Request Form
- All 4 sections
- Inline validation
- Budget/ROI fields appear only when funding is checked

### Request Review Screen
- Category badge + status header
- Workflow progress component (current / complete / pending steps)
- Role+state-gated action buttons
- Committee decision modal with dynamic conditional fields
- Comments/audit timeline distinguishing human comments from system events

