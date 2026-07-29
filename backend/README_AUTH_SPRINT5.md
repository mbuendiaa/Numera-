# Numera Sprint 5 — Authentication

## Included endpoints

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/refresh`
- `POST /auth/logout`
- `GET /auth/me`
- `PATCH /users/me`

## Run locally

```bash
python -m pip install -e ".[dev]"
uvicorn numera.main:app --reload
```

Open: <http://127.0.0.1:8000/docs>

## Test in Swagger

1. Use `POST /auth/register` with an email and a password of at least 8 characters.
2. Click **Authorize**.
3. Enter the same email in `username` and your password.
4. Swagger obtains the access token using `POST /auth/login`.
5. Test `GET /auth/me` and `PATCH /users/me`.

The login endpoint uses OAuth2 form fields, so the email is entered in the `username` field.

## Environment variables

Set a strong secret before production:

```bash
export JWT_SECRET_KEY="replace-this-with-a-long-random-secret"
export ACCESS_TOKEN_EXPIRE_MINUTES=30
export REFRESH_TOKEN_EXPIRE_DAYS=7
```

Passwords use bcrypt when the dependency is installed. A PBKDF2-SHA256 fallback is included for environments where bcrypt is unavailable.

## Tests

```bash
PYTHONPATH=src pytest -q
```

Expected result for this build: `66 passed`.
