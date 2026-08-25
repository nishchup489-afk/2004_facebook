# University Admission Flow

Before someone can register for Thefacebook, they need a fake university
identity.

This is not the real Thefacebook account yet.

This is only the university side.

It creates:

```text
university email
registration number
registration code
```

Then the student uses those details to register for Thefacebook.

---

## Frontend Page

File:

```text
frontend/university.html
```

The form asks for:

```text
university
first_name
last_name
```

The university options are hardcoded in the page:

```text
Harvard University
Yale University
Massachusetts Institute of Technology
Columbia University
Stanford University
```

When the form submits, JavaScript sends the data to the backend.

File:

```text
frontend/scripts/university.js
```

```javascript
const credentials = {
    university: university.value,
    first_name: first_name.value.trim(),
    last_name: last_name.value.trim()
};
```

Then:

```text
POST http://127.0.0.1:8000/university
```

---

## Backend Route

File:

```text
backend/app/router/university.py
```

Route:

```text
POST /university
```

The route receives:

```python
UniversityAdmissionRequest
```

The schema checks:

```text
university is not empty
first_name is not empty
last_name is not empty
```

and strips extra whitespace.

---

## Bug I noticed

If `/university` does not show up in FastAPI, check:

```text
backend/app/router/__init__.py
```

Right now both route files export a variable named `router`.

So importing them with the same name can accidentally keep only the last one.

Expected idea:

```text
main router
    |
    | include university router
    |
    | include auth router
```

I am not fixing it here because this doc is only for explaining the flow.

---

## Service Flow

File:

```text
backend/app/service/university.py
```

The service first checks if the university exists:

```sql
SELECT
    id,
    name,
    email_domain
FROM universities
WHERE name = %s;
```

If the university does not exist:

```text
400 University does not exist
```

If it exists, the backend creates the student identity.

```text
first name + last name + university domain

        |
        v

university email

        |
        v

registration number

        |
        v

registration code

        |
        v

students row
```

---

## Generated Email

The email is generated from:

```text
first name
last name
random hex value
university email domain
```

Example:

```text
nish.chup.9f3a1b2c@harvard.edu
```

The random part matters because two people can have the same name.

---

## Registration Number

The registration number uses a university prefix.

Example:

```text
HARV-2026-A1B2C3D4E5
```

The prefixes are:

```text
Harvard University -> HARV
Yale University -> YALE
Massachusetts Institute of Technology -> MIT
Columbia University -> COLU
Stanford University -> STAN
```

This is not used for login.

It is more like a university record number.

---

## Registration Code

The registration code is the important part.

It looks like:

```text
XXXX-XXXX-XXXX-XXXX
```

The backend returns the raw code to the frontend once.

But the database stores only:

```text
registration_code_hash
```

So the flow is:

```text
raw code

        |
        v

remove dashes and uppercase

        |
        v

SHA-256 hash

        |
        v

store hash in students
```

---

## Student Card

After the backend returns success, the frontend stores the response in
`sessionStorage`.

```javascript
sessionStorage.setItem(
    "universityAdmission",
    JSON.stringify(data)
);
```

Then it redirects to:

```text
/frontend/university_portfolio.html?student_id=...
```

That page shows:

```text
student name
university
university email
registration number
registration code
student card URL
```

The student needs the email and registration code for Thefacebook
registration.

---

## Important Detail

The registration code is shown on the student card.

But it may not be recoverable after the browser session.

So the page gives copy, print, and download buttons.

That is why the page says to save it.

---

## Full Flow

```text
open university.html

        |
        v

select university

        |
        v

enter first and last name

        |
        v

POST /university

        |
        v

check universities table

        |
        v

create students row

        |
        v

return email + registration code

        |
        v

store in sessionStorage

        |
        v

show university portfolio page
```

---

## Things I learned

- Registration starts before the Thefacebook user exists.
- The university page creates a student record, not a user record.
- The raw registration code is only returned to the browser.
- The database stores the hashed registration code.
- `sessionStorage` is useful for temporary browser data.
- Random email suffixes prevent duplicate generated emails.

---

[<- Back to Index](./README.md)
