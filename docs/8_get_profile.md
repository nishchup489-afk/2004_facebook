# GET Profile Flow

This is the read side of the profile feature.

Profile creation saves the data.

GET profile loads it back onto the profile page.

The route is:

```text
GET /profile/{user_id}
```

Example:

```text
GET /profile/7
```

---

## Latest main checked

The branch was updated from latest `origin/main`.

Important commit:

```text
02bf861 Feature added: GET profile
```

Important files:

```text
frontend/profile.html
frontend/scripts/profile.js
backend/app/router/profile.py
backend/app/service/profile.py
backend/app/schema/profile.py
backend/tests/test_profile_creation.py
```

---

## Profile Page

The frontend opens a profile with a query string:

```text
frontend/profile.html?user_id=7
```

That `user_id` tells the page which profile to load.

![Profile page loaded from backend](./screenshots/profile-created-page.png)

The page is not hard-coded.

It waits for the backend response, then fills in:

```text
name
school
member since
last updated
profile picture
basic info
contact info
personal info
```

---

## Frontend Request

File:

```text
frontend/scripts/profile.js
```

The script reads the id from the URL:

```javascript
const params = new URLSearchParams(
    window.location.search
);

const userId = params.get("user_id");
```

Then it sends:

```javascript
fetch(
    `${API_URL}/profile/${userId}`,
    {
        method: "GET",
        credentials: "include"
    }
);
```

Important part:

```text
credentials: "include"
```

The browser sends the login cookie with the request.

Without the cookie, the backend does not know who is viewing the profile.

---

## Backend Route

File:

```text
backend/app/router/profile.py
```

Route:

```python
@router.get(
    "/{user_id}",
    response_model=ProfileViewResponse,
)
```

The URL user id means:

```text
target_user_id
```

The session cookie means:

```text
current_user_id
```

So the backend knows both things:

```text
who is viewing
        |
        v
current_user_id

whose profile is being viewed
        |
        v
target_user_id
```

That is why the response can include:

```text
is_self
```

---

## Login Required

The route first calls:

```python
viewer_user_id = current_user_id(
    request
)
```

That checks the session cookie.

Flow:

```text
thefacebook_session cookie
        |
        v
hash raw token
        |
        v
sessions table
        |
        v
active user
```

If the cookie is missing, expired, or invalid:

```text
401 Unauthorized
```

The frontend handles that by sending the user back to login:

```javascript
if (response.status === 401) {
    window.location.href =
        "/frontend/index.html";
}
```

---

## Database Read

File:

```text
backend/app/service/profile.py
```

The service reads from four tables:

```text
users
students
universities
profile
```

The query joins them so one response can show account info and profile info
together.

Small version:

```sql
FROM users u

JOIN students s
    ON s.id = u.student_id

JOIN universities uni
    ON uni.id = s.university_id

JOIN profile p
    ON p.user_id = u.id

WHERE u.id = %s
  AND u.is_active = TRUE;
```

So the backend only returns:

```text
active user
profile row exists
matching user_id
```

If there is no matching row:

```text
404 Profile not found.
```

---

## Response Shape

Schema:

```text
ProfileViewResponse
```

The response has account fields:

```text
user_id
first_name
last_name
university_email
university_name
created_at
```

It also has profile fields:

```text
profile_pic
username
gender
status
residence
birth_date
home_town
high_school
mobile
websites
looking_for
interested_in
relationship_status
political_views
interests
favorite_music
favorite_movies
bio
updated_at
```

And it has this UI helper:

```text
is_self
```

`is_self` is true when:

```text
current_user_id == target_user_id
```

That lets the frontend hide the friend button on your own profile.

---

## Profile Picture

If the saved profile has a Cloudinary URL, the frontend puts it into the image:

```javascript
if (
    profilePicture &&
    profile.profile_pic
) {
    profilePicture.src =
        profile.profile_pic;
}
```

![Profile page with uploaded picture](./screenshots/cloudinary-profile-page.png)

So the GET route does not upload anything.

It only returns the stored URL.

---

## Full Flow

```text
profile.html?user_id=7

        |
        v

frontend reads user_id

        |
        v

GET /profile/7

        |
        v

browser sends session cookie

        |
        v

backend finds current user

        |
        v

backend loads target profile

        |
        v

return ProfileViewResponse

        |
        v

frontend fills profile.html
```

---

## Test I Ran

I added GET profile coverage in:

```text
backend/tests/test_profile_creation.py
```

Command:

```text
python -m pytest tests/test_profile_creation.py -v -p no:cacheprovider
```

Result:

```text
6 passed
```

The tests check:

```text
POST profile route still imports
POST /profile is registered
GET /profile/{user_id} is registered
GET profile maps the database row into ProfileViewResponse
GET profile marks your own profile with is_self = true
GET profile marks another user with is_self = false
missing profile raises Profile not found
```

---

## Things I learned

- The profile page needs both the URL `user_id` and the session cookie.
- `target_user_id` is the profile being viewed.
- `current_user_id` is the logged-in viewer.
- `is_self` is a backend value that makes frontend UI decisions easier.
- GET profile joins account, university, and profile data together.
- GET profile returns the stored Cloudinary URL, not a new upload.
- A missing profile should become a clean 404.

---

[<- Back to Index](./README.md)
