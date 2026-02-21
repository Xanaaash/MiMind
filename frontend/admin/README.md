# Admin Frontend Console

## Run

```bash
scripts/run-web-app.sh
```

Open `http://127.0.0.1:8000`.

## Admin auth

- Username is fixed: `admin`
- Password comes from env var `ADMIN_PASSWORD`
- Session uses HttpOnly cookie `mc_admin_session`

Example:

```bash
export ADMIN_PASSWORD="change-me-now"
scripts/run-web-app.sh
```

Optional session TTL (hours, default `8`):

```bash
export ADMIN_SESSION_TTL_HOURS="8"
```

## Notes

- UI is login-gated and module-driven (sidebar on desktop, top tabs on mobile).
- Includes admin observability dashboard for model invocation totals, latency distribution and error rate.
- Includes prompt pack management panel (`/api/prompts/*`) for viewing and activating prompt versions.
- Includes user management panel (`/api/admin/users`) with manual triage override action.
- Includes compliance panel (`/api/compliance/{user_id}/export|erase`) for export/delete operations.
- Homepage includes both entry cards:
  - Clinical Scales Center
  - Interactive Tests Center
- Full user-management UI is deferred. Reserved endpoint `/api/admin/users` currently returns not-implemented response.
