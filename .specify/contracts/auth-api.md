# Authentication API Contract

## Overview
The authentication API provides secure user login and registration functionality using JWT tokens.

## Endpoints

### POST /api/v1/auth/login
Authenticate user credentials and return JWT token.

**Request:**
```json
{
  "username": "string",
  "password": "string"
}
```

**Response (200):**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

**Error Responses:**
- 401: Incorrect username or password
- 422: Validation error

**HTMX Usage:**
```html
<form hx-post="/api/v1/auth/login" hx-target="#result">
  <input name="username" required>
  <input name="password" type="password" required>
  <button type="submit">Login</button>
</form>
```

### POST /api/v1/auth/register
Register a new user account (admin only).

**Request:**
```json
{
  "username": "string",
  "email": "string",
  "full_name": "string",
  "role": "nurse|physician|admin",
  "password": "string"
}
```

**Response (200):**
```json
{
  "access_token": "string",
  "token_type": "bearer"
}
```

**Error Responses:**
- 400: Username or email already registered
- 403: Insufficient permissions

## Security Requirements
- HTTPS required
- Password minimum 8 characters
- JWT tokens expire after 30 minutes
- Refresh token mechanism available

## Frontend Integration
- Store token in localStorage
- Include in Authorization header for all requests
- Handle token expiry with re-login
- Clear token on logout</content>
<parameter name="filePath">/home/mohamed/lab/.specify/contracts/auth-api.md