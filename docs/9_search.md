# Search Flow

Search is how a logged-in user finds people in the directory.

The page is:

```text
frontend/search.html
```

The route is:

```text
GET /search
```

Example:

```text
GET /search?q=alex&school=1&status=Student&looking_for=Networking&relationship_status=Single
```

---

## Latest main checked

This work started from current local `main`.

Important commit:

```text
101ba00 abort fix 2: added gitignore
```

Important files:

```text
frontend/search.html
frontend/scripts/search.js
backend/app/router/search.py
backend/app/service/search.py
backend/tests/test_search.py
```

---

## Search Page

The search form lets me filter by:

```text
name
school
profile status
looking for
relationship status
```

![Search page](./screenshots/search-page.png)

The new fields are useful because profile data is not only a name.

Someone might want to find:

```text
people looking for Networking
people marked Single
students at the same school
```

---

## Frontend Request

File:

```text
frontend/scripts/search.js
```

The frontend builds query params:

```javascript
params.set(
    "q",
    query
);
```

Then optional filters are added:

```text
school
status
looking_for
relationship_status
```

The API URL comes from:

```text
frontend/.env
```

Value:

```text
FRONTEND_API_URL=http://127.0.0.1:8000
```

So the request uses:

```javascript
`${API_URL}/search?${params.toString()}`
```

Not a repeated hard-coded backend URL.

---

## Login Required

Search is not public.

The route uses the session cookie:

```text
thefacebook_session
        |
        v
sessions table
        |
        v
current_user_id
```

That matters because the backend uses `current_user_id` to return friendship
state for each result.

---

## Backend Query

File:

```text
backend/app/service/search.py
```

Search reads from:

```text
users
students
universities
profile
friendships
```

Small version:

```sql
FROM users AS u

JOIN students AS s
    ON s.id = u.student_id

JOIN universities AS uni
    ON uni.id = s.university_id

LEFT JOIN profile AS p
    ON p.user_id = u.id

LEFT JOIN friendships AS f
    ON f.user_id_low = LEAST(%s, u.id)
   AND f.user_id_high = GREATEST(%s, u.id)
```

The friendship join lets the result say:

```text
self
none
pending_sent
pending_received
accepted
```

So the frontend can show:

```text
This is You
Add as Friend
Requested
Pending
Friends
```

---

## Response Shape

Each result returns:

```text
user_id
first_name
last_name
profile_pic
university_id
university_name
status
username
looking_for
relationship_status
friendship_status
```

That means the UI does not need to make a second request just to know whether
the add button should be visible.

---

## Test I Ran

Tests:

```text
backend/tests/test_search.py
```

Command:

```text
python -B -m pytest tests/test_courses.py tests/test_search.py tests/test_friendship_status.py tests/test_profile_creation.py -v -p no:cacheprovider
```

Result:

```text
15 passed
```

The search tests check:

```text
looking_for filter is added
relationship_status filter is added
friendship state is returned
empty search does not hit the database
```

---

## Things I learned

- Search needs the session cookie even though it is a GET request.
- The same person can look different in search depending on friendship state.
- Profile filters make search more useful than just first name / last name.
- `frontend/.env` keeps the API URL in one frontend place.

---

[<- Back to Index](./README.md)
