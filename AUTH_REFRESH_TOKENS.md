# Refresh Token Documentation (Medica Marketplace API)

This project uses:

- **Access token**: short-lived JWT used on every API request.
- **Refresh token**: long-lived opaque token used only to obtain new access tokens.

Refresh tokens are **rotated** (a new refresh token is issued on every refresh, and the previous one is revoked).

## What The Server Stores

Refresh tokens are stored in the database table `refresh_tokens`:

- `token_hash`: SHA-256 hash of the refresh token (the raw token is never stored)
- `user_id`: token owner
- `expires_at`: refresh token expiry
- `revoked_at`: set when token is revoked or rotated
- `replaced_by_token_id`: links old token to the new token after rotation
- `created_ip`, `user_agent`: optional audit context

Settings:

- `REFRESH_TOKEN_EXPIRE_DAYS` in `.env`
- Access token lifetime: `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`

## Endpoints

### 1) Login / Signup (OTP)

Login:

`POST /auth/login/otp/verify`

Signup:

`POST /auth/signup/otp/verify`

Response includes both tokens:

```json
{
  "token_type": "bearer",
  "access_token": "eyJhbGciOi...",
  "refresh_token": "uQe0yYc8...opaque...",
  "expires_in": 1800,
  "user": { "id": "...", "phone": "...", "roles": [] },
  "roles": ["buyer"]
}
```

### 2) Use Access Token For API Calls

Send on every request:

`Authorization: Bearer <access_token>`

### 3) Refresh (Rotate Tokens)

`POST /auth/token/refresh`

Request:

```json
{ "refresh_token": "uQe0yYc8...opaque..." }
```

Response:

- returns a **new** `access_token`
- returns a **new** `refresh_token`
- the old refresh token is revoked server-side

### 4) Logout (Revoke Refresh Token)

`POST /auth/logout`

Request:

```json
{ "refresh_token": "latest_refresh_token_here" }
```

This revokes the provided refresh token. The client must also clear local tokens.

## Frontend Flow (Concept Diagram)

### A) Normal flow

1. OTP verify succeeds
2. Frontend stores `access_token` + `refresh_token`
3. Frontend calls API with `Authorization: Bearer <access_token>`

### B) When access token expires (recommended patterns)

Pattern 1: Reactive refresh (on 401)

1. API request returns `401`
2. Frontend calls `POST /auth/token/refresh` with the current refresh token
3. If refresh succeeds:
   - replace both tokens locally (IMPORTANT: refresh tokens rotate)
   - retry the original request once
4. If refresh fails:
   - clear tokens
   - send user to login

Pattern 2: Proactive refresh (before expiry)

1. Frontend tracks `expires_in` from login/refresh responses
2. Shortly before expiry (example: 30-60s), call refresh
3. Replace both tokens

## Concurrency: Avoid Refresh Stampedes

Because refresh tokens rotate, multiple simultaneous refresh calls can cause failures.

Frontend should implement a single refresh-in-flight lock:

1. If a refresh is already in progress, wait for it.
2. When it completes, use the newest tokens and retry requests.

## Security Notes (Practical)

1. **Do not put sensitive data in JWTs**
   - JWTs are signed, not encrypted. Anyone holding it can decode claims.
2. **Prefer HttpOnly cookies for refresh tokens**
   - Current API returns refresh tokens in JSON. That works, but is more exposed to XSS.
   - If you want the safest setup, switch to a cookie-based refresh token.
3. **Rotation reduces damage**
   - If a refresh token is stolen, rotation + server-side revocation helps limit reuse.
4. **Rate limiting**
   - Refresh is rate limited per IP (see `AUTH_REFRESH_PER_IP_PER_MINUTE`).
