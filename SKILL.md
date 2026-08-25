---
name: docs-and-tests
description: Write focused tests and simple screenshot-heavy learning documentation for the 2004 Thefacebook project. Use after the developer finishes a feature or learning milestone. Do not implement or refactor production application code.
---

# Docs and Tests

Use this skill when the developer has finished or mostly finished a feature and wants Codex to handle the supporting work.

Your output should be:

    feature built manually
            ↓
        understand it
            ↓
        write tests
            ↓
        run tests
            ↓
        write docs
            ↓
        update docs index

Do not build the feature itself.

---

## Step 1 — Inspect the feature

Read the relevant production code.

Understand:

- what the feature does
- inputs
- outputs
- database changes
- failure cases
- security behavior
- user-visible flow

Inspect existing tests and docs first.

Do not rewrite the implementation.

---

## Step 2 — Identify useful tests

Ask:

    What behavior would actually hurt if it broke?

Test those things.

Prefer:

- happy path
- important failure paths
- database state
- authentication/security behavior

Avoid testing every line.

---

## Step 3 — Write tests

Place backend tests under:

    backend/tests/

Use pytest.

Keep tests readable.

Prefer:

    Arrange
    Act
    Assert

without unnecessary abstractions.

For authentication features, useful tests may include:

    test_registration_creates_user

    test_registration_marks_student_claimed

    test_registration_creates_session

    test_wrong_registration_code_fails

    test_claimed_student_cannot_register

    test_login_with_valid_password_succeeds

    test_login_with_wrong_password_fails

    test_login_creates_session

    test_logout_removes_session

Only add tests relevant to the feature being documented.

---

## Step 4 — Do not fix the app silently

If a test exposes a production bug:

Do not change:

    backend/app/
    frontend/

unless explicitly requested.

Instead report:

    Test:
    test_wrong_registration_code_fails

    Expected:
    400

    Actual:
    500

    Likely source:
    backend/app/service/auth.py

This lets the developer fix and learn from the bug.

---

## Step 5 — Run tests

Run the narrowest useful test command first.

Example:

    cd backend
    poetry run pytest tests/test_auth.py -v

Then run the full suite when reasonable:

    poetry run pytest

Record:

- passed
- failed
- skipped

Never fake successful results.

---

# Documentation

After testing, document the feature.

Documentation should explain:

    what I built
    how it works
    what I saw
    what I learned


Not:

    everything computer science knows about the topic

---

## Documentation voice

Write like the developer explaining their own project.

Use simple language.

Short example:

    ## Session cookie

    After login I don't want to send the password again.

    So the backend generates a random session token.

    Browser:

        thefacebook_session = RAW_TOKEN

    Database:

        SHA256(RAW_TOKEN)

    The browser sends the cookie automatically on later requests.

This is preferred over formal textbook explanations.

---

## Use screenshots heavily

When screenshots exist, use them.

Example:

    ![Registration page](screenshots/register-page.png)

Then explain what matters in the screenshot.

Example:

    Here the registration page asks for the university email and
    registration code created by the fake university system.

Do not add screenshots simply for decoration.

---

## Explain UI + backend together

When useful, connect what the user sees with what the backend does.

Example:

    User clicks Register

        ↓

    POST /register

        ↓

    students table

        ↓

    verify registration code

        ↓

    create users row

        ↓

    create session

        ↓

    browser receives HttpOnly cookie

This project prefers visual flows like this.

---

## Important code only

Use small code snippets.

Good:

    response.set_cookie(
        key="thefacebook_session",
        httponly=True,
        samesite="lax"
    )

Then explain:

    HttpOnly means frontend JavaScript cannot read the session cookie.

Do not paste 200 lines of source code into documentation.

---

## Include bugs when useful

Real bugs are valuable documentation.

Example:

    ## Bug I hit

    PostgreSQL looked like student ID 15 disappeared after an UPDATE.

    It didn't.

    I used:

        SELECT * FROM students;

    PostgreSQL does not guarantee row ordering without ORDER BY.

    Fix:

        SELECT *
        FROM students
        ORDER BY id;

This style is encouraged.

---

## Things I learned

Most substantial docs should end with:

    ## Things I learned

Keep it short.

Example:

    - Cookies and sessions are different things.
    - The browser stores the raw session token.
    - PostgreSQL stores only the token hash.
    - `HttpOnly` prevents JavaScript from reading the cookie.
    - `SameSite=Lax` helps protect against cross-site requests.
    - SQL rows have no guaranteed order without `ORDER BY`.

Only include things actually supported by the feature.

---

# commit rules 

if committing do specifically like 

do it after each stuff. 

For you you one test passed commit.
one docs added that docs commit.

"Feature added : ........... "
"Bug fix: ............. "
"Test passed : .............. "
"Docs added: ............... "

---

## Keep noise low

Documentation should usually be short enough to read quickly.

If a paragraph can be replaced by:

    login
      ↓
    session
      ↓
    cookie

prefer the diagram.

Do not over-document.

---

## Update navigation

After creating a new documentation page, update:

    docs/index.md

Add a clear link.

Every documentation page should contain:

    [← Back to Index](./README.md)

Make navigation painless.

---

## Final verification

Before finishing:

1. tests written
2. relevant tests executed
3. results reported honestly
4. docs written
5. screenshots referenced correctly
6. docs index updated
7. no secrets included
8. no production feature code modified
9. `git diff` reviewed

Then summarize:

    Tests:
    X passed

    Docs:
    added docs/...

    Production code:
    untouched

Do not commit or push unless explicitly requested.