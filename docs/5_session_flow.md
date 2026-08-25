# Session Flow

In simple:

```text
cookie = session key + session value
```

After register or login, the backend creates a session in the database with
7 days of expiry.

Then the backend sends a cookie to the browser.

The browser sends that cookie automatically on later requests.

---

## Why Session Exists

I do not want the user to send their password on every request.

So the flow is:

```text
password used once

        |
        v

backend creates session

        |
        v

browser stores cookie

        |
        v

future requests use cookie
```

---

## Token Storage

The backend creates a raw random token.

Example shape:

```text
P0QPaN...random...token
```

The browser stores the raw token.

The database stores:

```text
SHA256(raw token)
```

So:

```text
Browser cookie
    |
    v
raw session token


Database sessions table
    |
    v
hashed session token
```

This is better than storing the raw token directly in the database.

---

## Creating A Session

File:

```text
backend/app/service/auth.py
```

The service does:

```text
generate session token

        |
        v

hash session token

        |
        v

expires_at = now + 7 days

        |
        v

insert into sessions
```

The table stores:

```text
user_id
token_hash
created_at
expires_at
```

---

## Setting The Cookie

File:

```text
backend/app/router/auth.py
```

After register or login works:

```python
_set_session_cookie(
    response,
    session_token,
)
```

The cookie settings are:

```text
HttpOnly
SameSite=Lax
path=/
max_age from env
secure=False locally
```

`HttpOnly` means JavaScript cannot read the cookie.

The browser still sends it with requests.

---

## Frontend Fetch

When frontend needs cookies, fetch must include:

```javascript
credentials: "include"
```

Used in:

```text
frontend/scripts/register.js
frontend/scripts/login.js
```

Without this, the frontend and backend can talk, but the browser may not keep
the session cookie.

---

## Logout

Logout uses the cookie to find the session.

```text
browser sends cookie

        |
        v

backend hashes cookie value

        |
        v

DELETE FROM sessions
WHERE token_hash = ...

        |
        v

delete browser cookie
```

So logout removes both sides:

```text
database session
browser cookie
```

---

## Full Flow

```text
register or login

        |
        v

create sessions row

        |
        v

Set-Cookie header

        |
        v

browser stores cookie

        |
        v

later request includes cookie

        |
        v

backend hashes token

        |
        v

sessions table proves who the user is
```

---

## Things I learned

- Cookies live in the browser.
- Sessions live in the database.
- The cookie should contain the raw random token.
- The database should store the hashed token.
- `HttpOnly` protects the cookie from frontend JavaScript.
- `credentials: "include"` is needed when using cookies with `fetch()`.
- Logout should delete the database session and the browser cookie.

---

[<- Back to Index](./README.md)
