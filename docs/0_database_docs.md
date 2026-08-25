# Database Docs

The database is the real memory of this project.

Frontend can forget things.

Backend can restart.

But PostgreSQL keeps the students, users, profiles, friendships, courses,
enrollments, and sessions.

---

## Files

```text
backend/database/query/schema.sql
backend/database/query/seed.sql
backend/app/config/config.py
backend/app/config/settings.py
```

`schema.sql` creates the shape of the database.

`seed.sql` adds fake development data.

`settings.py` creates the PostgreSQL connection pool that the services use.

---

## Setup Flow

First I create the database.

![Create database](../backend/database/image.png)

Then I load the schema.

![Load schema](../backend/database/image-2.png)

Then I load the seed data.

![Load seed data](../backend/database/image-3.png)

Then I check if the data is really there.

![Check database](../backend/database/image-4.png)

![Check rows](../backend/database/image-5.png)

The basic flow is:

```text
start PostgreSQL

        |
        v

create database thefacebook

        |
        v

run schema.sql

        |
        v

run seed.sql

        |
        v

query tables to check
```

---

## Tables

```text
universities
students
users
profile
friendships
courses
enrollments
sessions
```

The important idea is that a university student can exist before the
student creates a Thefacebook account.

So the flow is:

```text
universities
    |
    v
students
    |
    v
users
    |
    v
profile
```

The `students` table is like the fake university system.

The `users` table is the Thefacebook account.

---

## Universities

`universities` stores the schools that are allowed in the app.

Important columns:

```text
name
email_domain
location
```

Example:

```text
Harvard University
harvard.edu
Cambridge, Massachusetts
```

When a student applies through the fake university page, the backend uses
the university email domain to create an email.

---

## Students

`students` stores university identity records.

Important columns:

```text
university_id
first_name
last_name
university_email
registration_number
registration_code_hash
claimed_at
```

The raw registration code is not stored.

The backend stores:

```text
SHA256(registration_code)
```

This matters because the code is used once to create a Thefacebook account.

Before registration:

```text
claimed_at = NULL
```

After registration:

```text
claimed_at = NOW()
```

So the same student record cannot keep creating new accounts.

---

## Users

`users` stores real Thefacebook accounts.

Important columns:

```text
student_id
first_name
last_name
university_email
password_hash
```

`student_id` is unique.

That means:

```text
one student -> one user
```

Not:

```text
one student -> many users
```

The password is stored as a hash, not the raw password.

---

## Profile

`profile` stores the public profile information.

It uses:

```text
user_id PRIMARY KEY
```

So one user gets one profile row.

This is a one-to-one relationship.

---

## Courses and Enrollments

Courses belong to universities.

Students belong to courses through `enrollments`.

```text
students
    |
    v
enrollments
    |
    v
courses
```

`enrollments` has a composite primary key:

```text
(student_id, course_id)
```

So the same student cannot be added to the same course twice.

---

## Friendships

Friendship is a user connecting to another user.

But both sides are still from the same table.

```text
users <-> friendships <-> users
```

The table stores:

```text
user_id_low
user_id_high
requested_by
status
```

The check constraint requires:

```text
user_id_low < user_id_high
```

So this:

```text
4 friend with 7
```

is only stored one way:

```text
user_id_low  = 4
user_id_high = 7
```

This prevents duplicate friendships like `4, 7` and `7, 4`.

---

## Sessions

`sessions` stores login sessions.

After register or login:

```text
generate raw token

        |
        v

hash token with SHA-256

        |
        v

store hash in sessions table

        |
        v

send raw token to browser cookie
```

The browser has the raw token.

PostgreSQL has the hash.

That is better than storing the raw token in the database.

---

## Connection Pool

The backend reads:

```python
DATABASE_URL = os.getenv("DATABASE_URL")
```

Then creates:

```python
pool = ConnectionPool(
    conninfo=DATABASE_URL,
    min_size=1,
    max_size=10,
)
```

So services can do:

```python
with pool.connection() as conn:
    with conn.cursor() as cursor:
        cursor.execute(...)
```

I like this because every feature does not create its own random database
connection logic.

---

## Things I learned

- The database should match the real flow of the app.
- A student can exist before a Thefacebook user exists.
- Registration codes should be hashed.
- Passwords should be hashed.
- A unique `student_id` in `users` prevents duplicate accounts.
- A junction table is needed for course enrollments.
- A self-referencing friendship needs rules so the same friendship is not stored twice.
- Sessions connect a browser cookie to a backend user.

---

[<- Back to Index](./README.md)
