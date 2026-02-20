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
- Homepage includes both entry cards:
  - Clinical Scales Center
  - Interactive Tests Center
- Full user-management UI is deferred. Reserved endpoint `/api/admin/users` currently returns not-implemented response.
