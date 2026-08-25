# Thefacebook 2004 — Codex Instructions

## Scope

Your job in this repository is limited to:

1. Writing and improving tests
2. Writing and improving documentation

Do NOT implement application features.

Do NOT refactor application code.

Do NOT modify backend or frontend production code unless the user explicitly asks you to.

The developer is building the actual project manually to learn engineering.

Codex is being used only to remove boring work around testing and documentation.

---

# Allowed work

You may freely modify:

- `backend/tests/`
- `docs/`
- `docs/index.md`
- documentation screenshots/references
- test configuration when necessary

You may inspect production code under:

- `backend/app/`
- `frontend/`

but normally DO NOT edit it.

Production code is the source you study in order to write tests and documentation.

---

# If you find a bug

Do NOT silently fix production code.

Instead:

1. Write or run the relevant test
2. Confirm the behavior
3. Report the bug clearly
4. Explain which production file appears responsible

Only fix production code if the user explicitly asks.

---

# Testing philosophy

Tests should verify meaningful behavior.

Do not chase coverage percentage for its own sake.

Prefer a small number of useful tests over dozens of pointless tests.

Focus especially on:

- authentication
- database state changes
- security-sensitive behavior
- validation
- important user flows

Use pytest for backend tests.

Prefer readable test names.

Example:

    test_valid_registration_creates_user
    test_invalid_registration_code_is_rejected
    test_claimed_student_cannot_register_again
    test_login_with_wrong_password_fails
    test_login_creates_session
    test_logout_removes_session

Tests should test behavior, not internal implementation details.

---

# Authentication testing

The project uses:

- Argon2 password hashing
- server-side sessions
- HttpOnly cookies
- SHA-256 session token hashes
- one-time university registration codes

Important behaviors worth testing include:

Registration:

    valid university student
        ↓
    valid registration code
        ↓
    users row created
        ↓
    students.claimed_at updated
        ↓
    session created

Failures:

- nonexistent student
- wrong registration code
- inactive student
- already claimed student
- duplicate Facebook account

Login:

- correct password succeeds
- wrong password fails
- nonexistent email fails
- successful login creates a session

Logout:

- current session is deleted
- logout remains safe when no session exists

Security:

- plaintext password is never stored
- raw session token is not stored in PostgreSQL
- registration code validation behaves correctly

---

# Test boundaries

Do NOT:

- rewrite production functions to make testing easier
- weaken validation just to make a test pass
- mock everything
- test trivial getters or syntax
- manufacture tests only for coverage
- alter database constraints

When a test fails because the application has a real bug, report it.

---

# Running tests

Backend tests normally run from:

    cd backend
    poetry run pytest

For authentication tests:

    poetry run pytest tests/test_auth.py -v

After writing tests:

1. Run them
2. Inspect failures
3. Report actual results
4. Never claim tests passed if they were not executed

---

# Documentation philosophy

Documentation should look like notes from the developer who built the project.

It should NOT read like a textbook.

Keep explanations:

- easy
- visual
- short
- practical
- based on this project

The developer prefers understanding the flow over reading theory.

---

# Documentation style

Prefer:

- screenshots
- small diagrams
- arrows
- short paragraphs
- small code snippets
- UI examples
- actual bugs encountered
- "things I learned"
- simple explanations

Avoid:

- long introductions
- huge walls of text
- corporate documentation
- unnecessary theory
- explaining obvious code line-by-line
- repeating the same point
- excessive jargon

Write naturally.

Example style:

    After login we don't want to send the password again every time.

    So we create a session.

    browser
        ↓
    raw session token
        ↓
    cookie

    database
        ↓
    SHA-256(token)
        ↓
    sessions.token_hash

This style is preferred over several paragraphs of formal session theory.

---

# Screenshots

Screenshots are an important part of the docs.

Store them in:

    docs/screenshots/

Prefer descriptive names:

    register-page.png
    session-cookie.png
    login-error.png
    student-database.png

Do NOT fabricate screenshots.

Do NOT expose:

- passwords
- raw session tokens
- `.env` values
- database passwords
- API secrets

If a screenshot contains sensitive information, crop or hide it.

---

# Documentation structure

Most documentation pages should roughly follow:

    [← Back to Index](./index.md)

    # Topic

    short explanation

    screenshot

    simple flow

    important code snippet

    explanation of what happened

    ## Things I learned

    short bullets

Not every document needs every section.

Do not force structure when it adds noise.

---

# Navigation

`docs/index.md` is the documentation homepage.

Whenever a new documentation file is added, update the index.

Example:

    # INDEX

    ## Backend

    1. [Frontend Backend Connection](./1_frontend_backend_connection.md)
    2. [University Student Flow](./2_university_student_flow.md)
    3. [Session Authentication](./3_session_authentication.md)

Every documentation page should have:

    [← Back to Index](./index.md)

Prefer simple numbered documentation filenames when they fit the existing structure.

---

# Documentation content

Document things that were actually learned or built.

Good topics:

- frontend/backend connection
- CORS
- PostgreSQL connection pool
- fake university identity system
- university → student → Facebook user flow
- password hashing
- session authentication
- HttpOnly cookies
- SameSite=Lax
- registration
- login
- logout
- database constraints
- bugs that taught something useful

Do NOT document every CSS adjustment or tiny variable rename.

---

# Git

Do not commit or push automatically unless explicitly requested.

When asked to prepare tests/docs for a commit:

1. run tests
2. inspect `git status`
3. inspect relevant diff
4. summarize what changed

Suggested commit messages:

    test: add authentication flow coverage

    docs: document session authentication

    test: cover registration failures

    docs: explain university registration flow

Keep docs and test commits focused when practical.

---

# Core rule

The developer writes the product.

You write the boring supporting layer:

    tests
      +
    docs

Do not take over the project.