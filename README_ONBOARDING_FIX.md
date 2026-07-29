# Numera onboarding fix

The public signup flow no longer accepts `company_id` or `role`.

Correct first-use flow:

1. `POST /auth/register` with email, password and name.
2. Authorize in Swagger with the same email/password.
3. `POST /companies/` to create the first company.
4. The creator is automatically added as `owner` and the new company becomes active.
5. `GET /companies/my` confirms the selected company.

A user can only join an existing company through the authenticated member-management endpoint, preventing self-assigned tenant access.
