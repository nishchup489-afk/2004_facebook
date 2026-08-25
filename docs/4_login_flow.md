# Login Flow

Login is simpler than registration.

Registration proves:

```text
this student belongs to the university record
```

Login proves:

```text
this user knows the password
```

After registration, the registration code is not used again.

---

## Frontend Page

File:

```text
frontend/index.html
```

The login form asks for:

```text
university email
password
```

File:

```text
frontend/scripts/login.js
```

The frontend sends:

```javascript
const credentials = {
    university_email: email.value.trim(),
    password: password.value
};
```

To:

```text
POST http://127.0.0.1:8000/login
```

Important:

```javascript
credentials: "include"
```

Again, this is needed because login creates a cookie session.

---

## Backend Route

File:

```text
backend/app/router/auth.py
```

Route:

```text
POST /login
```

The route calls:

```python
login_user(credentials)
```

If login works, it sets the session cookie.

If login fails, it returns:

```text
401 Unauthorized
```

---

## Backend Checks

File:

```text
backend/app/service/auth.py
```

The backend looks up the user:

```sql
SELECT
    id,
    first_name,
    last_name,
    university_email,
    password_hash,
    is_active
FROM users
WHERE LOWER(university_email) = LOWER(%s);
```

Then it checks:

```text
user exists
user is active
password matches password_hash
```

If the user does not exist:

```text
Invalid email or password.
```

If the password is wrong:

```text
Invalid email or password.
```

Same message for both.

That is good because the app does not reveal which emails already have an
account.

---

## Password Check

The password hash was created during registration.

On login:

```text
typed password

        |
        v

Argon2 verify

        |
        v

true or false
```

The backend uses:

```python
password_hasher.verify(
    password_hash,
    password,
)
```

If Argon2 says the password matches, the user is logged in.

---

## Creating Session

Login creates a new session just like registration.

```text
generate random token

        |
        v

hash token

        |
        v

insert hash into sessions

        |
        v

send raw token as cookie
```

The session lasts:

```text
7 days
```

because the service uses:

```python
SESSION_DURATION = timedelta(days=7)
```

---

## Cookie

The route sets:

```python
response.set_cookie(
    key=COOKIE_NAME,
    value=session_token,
    httponly=True,
    secure=False,
    samesite="lax",
    max_age=COOKIE_MAX_AGE,
    path="/",
)
```

`HttpOnly` means frontend JavaScript cannot read the cookie.

`SameSite=Lax` gives some protection against cross-site requests.

`secure=False` is for local development.

In production with HTTPS, this should become:

```text
secure=True
```

---

## Full Flow

```text
index.html login form

        |
        v

POST /login

        |
        v

find user by email

        |
        v

verify password

        |
        v

create session

        |
        v

set cookie

        |
        v

redirect to home.html
```

---

## Things I learned

- Login should use the `users` table, not the `students` table.
- Registration code is only for registration.
- Wrong email and wrong password should return the same login error.
- Argon2 verifies the password without storing the raw password.
- Login creates a server-side session.
- The browser stores the raw session token in a cookie.

---

[<- Back to Index](./README.md)
