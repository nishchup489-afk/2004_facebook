
# Security Policy

Thank you for helping improve the security of **Thefacebook 2004**.

This project is an educational recreation of an early university social network built with FastAPI, PostgreSQL, raw SQL, plain HTML/CSS/JavaScript, and server-side sessions.

Security reports are especially useful when they involve authentication, authorization, session handling, SQL queries, user data exposure, or unsafe configuration.

---

## Supported Versions

Security fixes are applied to the latest version of the `main` branch.

| Version | Supported |
| --- | --- |
| Latest `main` | ✅ |
| Older commits / abandoned branches | ❌ |

This project does not currently maintain multiple release branches.

---

## Reporting a Vulnerability

Please **do not publish sensitive vulnerability details in a public GitHub issue**.

If GitHub private vulnerability reporting is enabled for this repository, use:

**Security → Report a vulnerability**

That is the preferred reporting method.

If private vulnerability reporting is unavailable, open a public issue with only a minimal message such as:

> I found a potential security issue and would like a private way to share the details.

Do not include:

- exploit code
- credentials
- session tokens
- database connection strings
- private user data
- detailed reproduction steps for a serious vulnerability

until a private communication channel is available.

---

## What to Include in a Report

A useful security report should include:

- a clear description of the vulnerability
- the affected endpoint, file, or feature
- steps to reproduce the issue
- expected behavior
- actual behavior
- potential impact
- whether authentication is required
- any suggested fix, if you have one

Screenshots, logs, and proof-of-concept code can be useful when shared privately.

Please remove unrelated personal data and secrets from logs or screenshots.

---

## Security Areas of Interest

### Authentication

The application uses server-side sessions.

Relevant issues include:

- authentication bypass
- accepting invalid or expired sessions
- session fixation
- insecure session token generation
- leaking raw session tokens
- incorrect logout behavior
- sessions remaining valid after they should be revoked

The authenticated user must always be resolved from the server-side session.

Frontend-supplied user IDs must never be trusted as authentication.

---

### Authorization

A logged-in user should not be able to perform actions as another user.

Examples include:

- editing another user's profile
- accepting a friend request on behalf of another user
- modifying another user's account
- deleting another user's content without permission
- accessing data that should not be available to them

Changing a URL parameter must not be enough to gain another user's permissions.

---

### SQL Injection

The backend intentionally uses raw SQL with Psycopg.

All untrusted values must use parameterized queries.

Good:

```python
cur.execute(
    "SELECT id FROM users WHERE id = %s",
    (user_id,),
)
````

Unsafe:

```python
cur.execute(
    f"SELECT id FROM users WHERE id = {user_id}"
)
```

Please report any endpoint where user input can alter SQL syntax.

---

### Session Cookies

Session cookies should use appropriate security settings in production.

Relevant properties include:

* `HttpOnly`
* `Secure`
* `SameSite`
* appropriate expiration
* appropriate path/domain scope

Production session cookies should not be transmitted over plain HTTP.

---

### CORS

The API may be deployed separately from the frontend.

CORS configuration should allow only intended frontend origins when credentials are enabled.

Avoid overly broad production configurations.

For example, credentialed requests should not rely on unrestricted origins.

---

### Password Security

Passwords should never be stored in plaintext.

The project uses password hashing rather than reversible encryption.

Please report:

* plaintext password storage
* password exposure in logs
* unsafe password comparison
* password disclosure in API responses
* hard-coded real credentials

---

### Secrets

The repository must not contain real:

* database passwords
* PostgreSQL connection strings with credentials
* Cloudinary API secrets
* session tokens
* API keys
* production credentials
* private environment variables

Files such as `.env` should remain untracked.

If a real secret is accidentally committed, deleting it from the latest commit is not enough. The credential should also be rotated.

---

### Friendships and Social Graph Authorization

Friendship operations must be authorized by the backend.

Examples of invalid behavior include:

* accepting your own outgoing friend request
* creating duplicate friendships
* creating both `(A, B)` and `(B, A)` relationships
* accepting a request that was never sent to you
* manipulating `requested_by`
* accessing another user's private relationship data without permission

Friendship pairs are normalized using:

```text
user_id_low  = min(user_a, user_b)
user_id_high = max(user_a, user_b)
```

Any security fix should preserve this invariant.

---

### Profile and User Data

User profile data should only expose fields intended by the API.

Please report:

* password hashes appearing in responses
* session data appearing in responses
* private internal IDs or secrets being exposed unnecessarily
* unauthorized profile modification
* mass assignment vulnerabilities
* sensitive database fields being returned accidentally

---

### File and Image Handling

Profile images may be uploaded to an external image provider.

Relevant issues include:

* accepting unsafe file types
* trusting client-supplied file metadata
* exposing image service secrets
* unsafe upload handling
* storing credentials in frontend code

The database should store the resulting image URL, not service credentials.

---

## Expected Security Behavior

The application should generally follow these rules:

```text
Authentication
→ server verifies session

Authorization
→ server verifies permission

Database access
→ parameterized SQL

Passwords
→ hashed

Sessions
→ random token + hashed database copy

Secrets
→ environment variables

Frontend
→ presentation only, never trusted for authorization
```

---

## Out of Scope

The following generally do not require a security report:

* UI bugs without a security impact
* historical inaccuracies
* broken styling
* missing accessibility labels
* performance issues without security impact
* dependency warnings with no practical exploit path
* issues requiring physical access to the developer's own machine

If you are unsure, reporting the issue is still welcome.

---

## Responsible Testing

Please test responsibly.

Do not:

* intentionally damage production data
* attempt denial-of-service attacks
* access data belonging to real users without permission
* publish credentials
* perform destructive testing against the live deployment
* use automated scanning that creates excessive traffic

Prefer reproducing vulnerabilities in a local development environment whenever possible.

---

## Disclosure

Please allow reasonable time for a vulnerability to be investigated and fixed before publishing detailed technical information.

After a fix is released, coordinated disclosure and technical write-ups are welcome.

---

## Security Is a Shared Responsibility

Security improvements are welcome through:

* vulnerability reports
* pull requests
* tests
* code review
* safer defaults
* documentation improvements

Thanks for helping keep **Thefacebook 2004** secure.

```
```
