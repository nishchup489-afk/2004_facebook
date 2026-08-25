# Registration Flow

Registration is where a university student becomes a Thefacebook user.

The student needs:

```text
university email
first name
last name
registration code
password
```

The university email and registration code come from the university student
card.

---

## Frontend Page

File:

```text
frontend/register.html
```

The form asks for:

```text
email
password
confirm password
first name
last name
registration code
```

Before sending anything to the backend, JavaScript checks:

```javascript
if (password.value !== cnfrmPassword.value) {
    showError("Passwords do not match.");
    return;
}
```

This is only a frontend check.

The backend still has to protect itself.

---

## Request

File:

```text
frontend/scripts/register.js
```

The frontend sends:

```javascript
const credentials = {
    university_email: email.value.trim(),
    password: password.value,
    first_name: firstname.value.trim(),
    last_name: lastname.value.trim(),
    registration_code: registrationCode.value.trim()
};
```

To:

```text
POST http://127.0.0.1:8000/register
```

Important:

```javascript
credentials: "include"
```

That tells the browser to accept and send cookies for this request.

Without that, the backend can set a session cookie but the frontend may not
keep it.

---

## Backend Route

File:

```text
backend/app/router/auth.py
```

Route:

```text
POST /register
```

If registration works:

```text
201 Created
```

If something is wrong:

```text
400 Bad Request
```

The route calls:

```python
register_user(credentials)
```

Then it sets the session cookie.

---

## Backend Checks

File:

```text
backend/app/service/auth.py
```

First the backend looks up the student:

```sql
SELECT
    id,
    first_name,
    last_name,
    university_email,
    registration_code_hash,
    claimed_at,
    is_active
FROM students
WHERE LOWER(university_email) = LOWER(%s)
FOR UPDATE;
```

`FOR UPDATE` locks the student row during registration.

That matters because two requests should not claim the same student at the
same time.

Then the backend checks:

```text
student exists
student is active
claimed_at is still NULL
no user already exists for this student
first name matches
last name matches
registration code matches
```

---

## Code Matching

The form sends the raw registration code.

The database has the hash.

So the backend normalizes and hashes the submitted code:

```text
remove dashes
strip spaces
uppercase

        |
        v

SHA-256
```

Then it compares:

```python
hmac.compare_digest(
    prompt_hash,
    stored_hash,
)
```

`compare_digest` is used because this is secret-ish data and should be
compared carefully.

---

## Creating The User

When all checks pass:

```text
hash password with Argon2

        |
        v

insert row into users

        |
        v

set students.claimed_at = NOW()

        |
        v

create session row

        |
        v

set browser cookie
```

The user row stores:

```text
student_id
first_name
last_name
university_email
password_hash
```

The raw password is not stored.

---

## One-Time Code

The registration code is one-time because after registration:

```text
claimed_at = NOW()
```

Then if someone tries to register again with the same university email:

```text
User already exists. Try logging in.
```

So the registration code does not need to be deleted.

The student record itself now says it has already been claimed.

---

## Response

The backend returns:

```text
user_id
first_name
last_name
university_email
message
```

Then the frontend redirects:

```text
/frontend/complete_profile.html
```

---

## Full Flow

```text
register.html

        |
        v

POST /register

        |
        v

find student by university email

        |
        v

check name + registration code

        |
        v

create users row

        |
        v

mark student claimed

        |
        v

create session

        |
        v

set cookie

        |
        v

complete profile page
```

---

## Things I learned

- Registration is not just inserting a user.
- The backend must verify the student belongs to the fake university records.
- `FOR UPDATE` helps protect a one-time claim.
- Passwords should be hashed with a password hasher, not plain SHA-256.
- Registration codes can be checked by hashing the prompt and comparing it to the stored hash.
- A session can start immediately after registration.
- `credentials: "include"` matters when cookies are involved.

---

[<- Back to Index](./README.md)
