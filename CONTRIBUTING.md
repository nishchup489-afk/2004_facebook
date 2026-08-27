# Contributing to Thefacebook 2004

Thanks for your interest in contributing to **Thefacebook 2004**.

This project is an educational recreation of an early university social network, built to practice and demonstrate:

- backend engineering
- relational database design
- raw SQL
- authentication
- authorization
- search
- social graph concepts
- frontend fundamentals

The project intentionally keeps the stack small:

- HTML
- CSS
- JavaScript
- FastAPI
- PostgreSQL
- Psycopg
- server-side sessions

The goal is **not** to turn this into a modern Facebook clone.

---

## What Contributions Are Welcome?

Good contributions include:

- bug fixes
- tests
- documentation improvements
- accessibility improvements
- PostgreSQL query improvements
- indexing and performance improvements
- security fixes
- historically appropriate UI improvements
- frontend/backend integration fixes
- developer experience improvements
- better error handling

Small contributions are welcome.

If you are new to open source, look for issues labeled:

```text
good first issue
```

---

## What Is Out of Scope?

Please avoid features that significantly change the intended scope of the project.

Examples:

- AI recommendation systems
- reels
- stories
- modern algorithmic news feeds
- recommendation ML
- unnecessary microservices
- Kafka without a demonstrated need
- Redis without a demonstrated need
- React or another frontend framework
- third-party authentication replacing the existing session system
- modern Facebook product features unrelated to the original university-network concept

The constrained architecture is part of the project.

---

# Development Setup

Clone the repository:

```bash
git clone https://github.com/nishchup489-afk/2004_facebook.git
cd 2004_facebook
```

## Backend

Move into the backend directory:

```bash
cd backend
```

Install dependencies:

```bash
poetry install
```

Run FastAPI:

```bash
poetry run python -m uvicorn app.main:app --reload
```

The API should run at:

```text
http://127.0.0.1:8000
```

---

## Frontend

The frontend uses plain HTML, CSS, and JavaScript.

From the project root, run:

```bash
python -m http.server 3000
```

Then open:

```text
http://127.0.0.1:3000/frontend/index.html
```

---

# Environment Variables

Configure the required environment variables locally.

Do not commit secrets.

Sensitive values include:

- PostgreSQL connection strings
- database passwords
- Cloudinary credentials
- API secrets
- production credentials
- session tokens

Never commit:

```text
.env
```

---

# Branch Naming

Create a branch before making changes.

Feature:

```bash
git switch -c feat/short-description
```

Bug fix:

```bash
git switch -c fix/short-description
```

Documentation:

```bash
git switch -c docs/short-description
```

Tests:

```bash
git switch -c test/short-description
```

Examples:

```text
feat/mutual-friend-display
fix/duplicate-friend-request
docs/session-authentication
test/search-service
```

---

# Keep Pull Requests Focused

A pull request should solve one clear problem.

Good:

```text
fix: prevent duplicate friend requests
```

Avoid combining unrelated changes such as:

```text
rewrite friendship system
redesign profile page
replace authentication
reorganize backend
change database schema
```

in one pull request.

Focused changes are easier to review, test, and merge.

---

# Backend Architecture

The backend generally follows:

```text
router
   ↓
service
   ↓
PostgreSQL
```

## Routers

Routers should primarily handle HTTP concerns:

- request parameters
- authentication dependencies
- response models
- status codes
- translating service errors into HTTP errors

Avoid putting large SQL queries directly inside routers.

## Services

Services contain application and database logic.

Examples:

- creating profiles
- searching users
- sending friend requests
- accepting friend requests
- finding mutual friends
- retrieving courses

## Schemas

Pydantic schemas define API request and response structures.

Reuse existing schemas where practical instead of creating duplicate response formats.

---

# Authentication Rules

The project uses **server-side sessions**.

The authenticated user must always be resolved from the session cookie.

Do not trust a frontend-provided user ID as the authenticated identity.

Conceptually:

```text
browser cookie
      ↓
session token
      ↓
sessions table
      ↓
authenticated user_id
```

A URL parameter may identify another user.

Example:

```text
/profile/15
```

Here:

```text
15 = target user
```

The current authenticated user still comes from the session.

Do not implement authentication using:

- JWT
- Clerk
- Firebase Auth
- Auth0
- another managed authentication provider

unless there is a clear project-wide decision to change the architecture.

---

# Database Changes

Database changes should be deliberate.

Before modifying the schema, consider whether the problem can be solved using the existing design.

When changing the database:

- preserve referential integrity
- use foreign keys appropriately
- consider uniqueness constraints
- consider indexes
- avoid destructive changes unless necessary
- explain important schema decisions
- preserve existing data when possible

If your contribution adds or modifies an index, explain which query it is intended to improve.

---

# SQL Guidelines

This project intentionally uses raw SQL.

Always use parameterized queries.

Good:

```python
cur.execute(
    """
    SELECT id, first_name, last_name
    FROM users
    WHERE id = %s;
    """,
    (user_id,),
)
```

Do not do:

```python
cur.execute(
    f"SELECT * FROM users WHERE id = {user_id}"
)
```

Never interpolate untrusted user input directly into SQL.

## Query Design

Prefer understandable SQL over unnecessarily clever SQL.

Use:

- JOINs
- CTEs
- indexes
- constraints
- PostgreSQL features

when they solve a real problem.

Avoid adding an external system when PostgreSQL already handles the use case well.

For example, basic people search should not require Elasticsearch unless the project eventually reaches a point where PostgreSQL is clearly insufficient.

---

# Friendship Model

Friendships are stored as normalized unordered pairs.

For users `15` and `8`:

```text
user_id_low  = 8
user_id_high = 15
```

Use:

```python
user_id_low = min(user_a, user_b)
user_id_high = max(user_a, user_b)
```

The `requested_by` column records who initiated the request.

The relationship status can represent states such as:

```text
pending
accepted
rejected
```

Do not create separate relationship rows for:

```text
(8, 15)
```

and:

```text
(15, 8)
```

They represent the same pair of users.

Any friendship-related contribution should preserve this invariant.

---

# Frontend Guidelines

The frontend intentionally uses plain:

```text
HTML
CSS
JavaScript
```

Do not introduce a frontend framework without prior discussion.

Keep visual changes consistent with the early Thefacebook aesthetic.

That generally means:

- simple bordered sections
- compact layouts
- blue navigation and headers
- directory-style pages
- minimal decoration
- simple buttons
- limited animation
- no modern card-heavy UI

Avoid redesigning the application into a modern social media interface.

---

# API Requests

Authenticated frontend requests should include credentials where required.

Example:

```javascript
fetch(`${API_URL}/me`, {
    method: "GET",
    credentials: "include"
});
```

Do not move authorization logic into the frontend.

The frontend may hide or disable buttons based on relationship state, but the backend must always enforce permissions independently.

---

# Profile Images

Profile images may be hosted externally.

The database stores the resulting image URL rather than the image bytes themselves.

Frontend code should handle missing profile images gracefully using the project's default profile image.

Do not commit large user-uploaded image files directly into the repository.

---

# Error Handling

Backend failures should return appropriate HTTP status codes.

Examples:

```text
400 Bad Request
401 Unauthorized
404 Not Found
409 Conflict
422 Unprocessable Entity
```

Do not allow expected application errors to become generic `500 Internal Server Error` responses.

For example, an invalid or expired session should result in:

```text
401 Unauthorized
```

not:

```text
500 Internal Server Error
```

---

# Tests

When fixing a bug, add a regression test when practical.

When adding backend behavior, test important edge cases.

Examples:

```text
cannot friend yourself
duplicate friend requests are rejected
expired session returns 401
pending friendships are not returned as friends
mutual friends only count accepted relationships
missing users return 404
inactive users are handled correctly
```

Tests should not depend on production services unnecessarily.

For example, friendship tests should not upload images to Cloudinary.

Keep test data isolated and predictable.

---

# Generated Files

Do not commit generated Python files.

These should remain ignored:

```text
__pycache__/
*.pyc
*.pyo
*.pyd
```

Also do not commit:

```text
.env
```

or other local secret/configuration files containing credentials.

---

# Code Style

Follow the style already used in the surrounding code.

Prefer:

- clear names
- small focused functions
- readable SQL
- consistent formatting
- straightforward control flow

Avoid introducing large abstractions for simple problems.

A contribution should make the system easier to understand, not harder.

---

# Commit Messages

Use short, descriptive commit messages.

Examples:

```text
feat: add mutual friend endpoint
fix: prevent duplicate friend requests
test: cover expired session handling
docs: document friendship model
refactor: simplify search result mapping
```

Avoid vague commit messages such as:

```text
update
changes
stuff
fixed
final
```

---

# Pull Requests

A good pull request should explain:

## What changed?

Describe what you implemented.

## Why?

Explain the problem being solved.

## How was it tested?

Include:

- tests run
- manual testing steps
- important edge cases

## UI changes

For frontend changes, include screenshots when possible.

## Database changes

Clearly mention:

- schema changes
- new constraints
- indexes
- query changes

---

# Pull Request Checklist

Before opening a pull request, check that:

- [ ] the change solves one focused problem
- [ ] the application still runs locally
- [ ] relevant tests pass
- [ ] new backend behavior has tests where practical
- [ ] no secrets were committed
- [ ] no `__pycache__` or `.pyc` files were committed
- [ ] SQL remains parameterized
- [ ] authentication still comes from the session
- [ ] frontend changes match the existing visual style
- [ ] documentation was updated if behavior changed

---

# Security

Do not publish:

- passwords
- database credentials
- API secrets
- Cloudinary secrets
- session tokens
- private user information
- production environment variables

If you discover a serious security vulnerability, avoid publishing detailed exploit instructions publicly before the issue can be reviewed.

For ordinary bugs, opening a GitHub issue is fine.

---

# Performance Contributions

Performance work is welcome when it is measurable.

Useful examples include:

- improving SQL indexes
- removing N+1 queries
- reducing unnecessary database round trips
- improving search queries
- optimizing large result sets
- adding pagination

When proposing a performance change, explain the problem being solved.

If possible, include evidence such as:

```sql
EXPLAIN ANALYZE
```

results before and after the change.

Do not add caching or infrastructure solely because it is considered "scalable."

---

# Historical Scope

This project is inspired by the early university-network era of Thefacebook.

Historical accuracy is not absolute, and the backend uses modern technologies.

However, new product features should generally respect the project's intended era and simplicity.

Examples of appropriate concepts include:

- university profiles
- people search
- friendships
- courses
- walls
- early directory-style social features

When unsure whether a feature belongs, open an issue before spending significant time implementing it.

---

# Accessibility

Accessibility improvements are welcome.

Examples include:

- labels for form controls
- useful alt text
- keyboard navigation
- reasonable semantic HTML
- improved focus behavior
- clearer error messages

Accessibility improvements should preserve the project's visual character where possible.

---

# Documentation

Documentation contributions are welcome.

Useful topics include:

- local setup
- database schema
- authentication
- friendship modeling
- search architecture
- deployment
- API behavior
- testing

Prefer concise documentation that explains **why** something works the way it does, not only what the code contains.

---

# Opening an Issue

Before implementing a large feature, consider opening an issue first.

A useful issue should include:

- the problem
- expected behavior
- current behavior
- reproduction steps if relevant
- screenshots or logs where useful

For feature ideas, explain why the feature fits the project's scope.

---

# Code Review

Changes may be requested when a contribution:

- introduces unnecessary complexity
- breaks existing behavior
- weakens security
- duplicates existing architecture
- significantly expands project scope
- introduces an unnecessary dependency
- lacks tests for important behavior
- does not follow the existing data model

Feedback should remain technical and respectful.

---

# License

By contributing to this repository, you agree that your contributions will be licensed under the project's **MIT License**.

---

# Trademark and Historical Material

This project is an independent educational project.

It is not affiliated with, endorsed by, or sponsored by Meta Platforms, Inc. or Facebook.

The project's software license does not grant rights to third-party trademarks, logos, screenshots, images, or other third-party assets.

Contributors should avoid adding copyrighted or trademarked assets unless their use is legally appropriate for the project.

---

# Thank You

Whether you:

- fix a typo
- improve a SQL query
- report a bug
- add a test
- improve accessibility
- improve documentation
- optimize a query
- contribute frontend polish

your contribution is appreciated.

Thanks for helping improve **Thefacebook 2004**.
