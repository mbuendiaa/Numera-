# Authentication UX fix

The authentication flow now uses a simple JSON login payload:

```json
{
  "email": "marta@empresa.com",
  "password": "StrongPass123!"
}
```

Swagger exposes an HTTP Bearer authorization dialog. After calling `POST /auth/login`, copy only the `access_token`, click **Authorize**, paste the token, and then call protected endpoints such as `POST /companies/`.

The previous OAuth2 form fields (`grant_type`, `scope`, `client_id`, and `client_secret`) are no longer shown on the login endpoint.
