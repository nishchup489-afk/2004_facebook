# Profile Creation Flow

Profile creation is what happens after registration.

Registration creates the account.

Profile creation fills the account with information other students can see.

The profile can include:

```text
username
profile picture
basic info
school/location info
contact info
personal info
interests
bio
```

---

## Latest main checked

The branch was updated from latest `origin/main`.

Important commit:

```text
2a5664c Feature added: profile creation:
```

Important files:

```text
frontend/complete_profile.html
frontend/scripts/complete_profile.js
frontend/profile.html
frontend/scripts/profile.js
backend/app/router/profile.py
backend/app/service/profile.py
backend/app/service/get_user_id.py
backend/app/schema/profile.py
```

---

## Profile Form

The user fills this page after registering.

![Profile creation form](./screenshots/profile-creation-form.png)

The form has a real file input:

```html
<input
    type="file"
    id="profile_pic"
    name="profile_pic"
    accept="image/*"
>
```

That means the browser can send an image file, not just text.

---

## Frontend Request

File:

```text
frontend/scripts/complete_profile.js
```

The frontend uses:

```javascript
const formData = new FormData();
```

Then it adds normal text fields:

```javascript
formData.append("username", username);
formData.append("gender", gender);
formData.append("status", status);
```

For list-like fields, it turns comma-separated text into arrays and then
stringifies them:

```javascript
formData.append(
    "interests",
    JSON.stringify(
        commaSeparatedToArray(interests)
    )
);
```

If a profile picture exists:

```javascript
formData.append(
    "profile_pic",
    profilePicture.files[0]
);
```

Then it sends:

```javascript
fetch(
    "http://127.0.0.1:8000/profile",
    {
        method: "POST",
        credentials: "include",
        body: formData
    }
);
```

There is no manual `Content-Type` header here.

That is correct for `FormData`.

The browser creates the multipart boundary itself.

---

## Backend Route

File:

```text
backend/app/router/profile.py
```

Route:

```text
POST /profile
```

The backend reads fields using:

```python
username: str = Form(...)
profile_pic: UploadFile | None = File(None)
```

So the request is:

```text
multipart/form-data
```

Not:

```text
application/json
```

---

## Get Current User

Before creating a profile, the backend needs to know which logged-in user is
making the request.

File:

```text
backend/app/service/get_user_id.py
```

Flow:

```text
browser cookie

        |
        v

raw session token

        |
        v

SHA-256 hash

        |
        v

sessions table

        |
        v

active user_id
```

The query checks:

```sql
SELECT s.user_id
FROM sessions s
JOIN users u
    ON u.id = s.user_id
WHERE s.token_hash = %s
  AND s.expires_at > NOW()
  AND u.is_active = TRUE;
```

So profile creation requires:

```text
valid session cookie
not expired session
active user
```

If there is no cookie:

```text
You are not logged in.
```

If the session is wrong or expired:

```text
Session is invalid or expired.
```

---

## Parsing Lists

The frontend sends list fields as JSON strings.

Example:

```text
["Programming", "basketball", "movies"]
```

The backend parses them with:

```python
json.loads(value)
```

Then it checks the result is actually a list.

If the data is not valid JSON:

```text
Invalid list data.
```

If the JSON is not a list:

```text
Expected a list.
```

This matters because fields like interests, websites, favorite music, and
favorite movies should be stored as arrays, not one big string.

---

## Image Upload

File:

```text
backend/app/service/profile.py
```

If the user selected a profile picture, the service first checks:

```python
profile_pic.content_type.startswith("image/")
```

If it is not an image:

```text
Profile picture must be an image.
```

If it is an image, the backend uploads it to Cloudinary:

```python
cloudinary.uploader.upload(
    profile_pic.file,
    folder="thefacebook/profile_pictures",
    public_id=f"user_{user_id}",
    overwrite=True,
    resource_type="image",
)
```

Important parts:

```text
folder      -> thefacebook/profile_pictures
public_id   -> user_{user_id}
overwrite   -> replace old profile picture
```

Then Cloudinary returns:

```text
secure_url
```

That URL becomes:

```text
profile_pic
```

in the database.

---

## Database Write

The profile data goes into the `profile` table.

The service uses:

```sql
INSERT INTO profile (...)
VALUES (...)
ON CONFLICT (user_id)
DO UPDATE SET ...
```

So the same endpoint can:

```text
create profile first time
update profile later
```

Important part:

```sql
profile_pic =
    COALESCE(
        EXCLUDED.profile_pic,
        profile.profile_pic
    )
```

This means:

```text
new picture uploaded
        -> replace old profile_pic

no new picture uploaded
        -> keep old profile_pic
```

That is useful because editing text fields should not delete the existing
profile picture.

---

## JSONB Storage

Some profile fields are lists.

In Python they are normal lists:

```python
profile.interests
profile.favorite_music
profile.favorite_movies
profile.websites
```

Before inserting them into PostgreSQL, the service wraps them:

```python
Jsonb(profile.interests)
```

So PostgreSQL stores them as JSONB.

Example:

```text
interests = ["Programming", "basketball", "movies"]
```

This is better than storing:

```text
Programming,basketball,movies
```

because the database still knows it is structured data.

---

## Profile Display

After profile creation succeeds, the frontend redirects to:

```text
/frontend/profile.html
```

The profile page is where the saved fields should show up.

![Created profile page](./screenshots/profile-created-page.png)

File:

```text
frontend/scripts/profile.js
```

It loads:

```text
GET /profile
```

with:

```javascript
credentials: "include"
```

Then it fills the page with the response.

For the picture:

```javascript
if (profile.profile_pic) {
    profilePicture.src =
        profile.profile_pic;
}
```

So the displayed image should eventually be the Cloudinary URL.

---

## Full Flow

```text
complete_profile.html

        |
        v

FormData

        |
        v

POST /profile

        |
        v

get user_id from session cookie

        |
        v

parse form fields

        |
        v

upload image to Cloudinary

        |
        v

store profile row

        |
        v

return ProfileResponse

        |
        v

redirect to profile.html
```

---

## Test I Ran

I added a small smoke test:

```text
backend/tests/test_profile_creation.py
```

Command:

```text
python -m pytest tests/test_profile_creation.py -v
```

Result:

```text
2 passed
```

The tests check:

```text
profile creation route imports
/profile is registered in the FastAPI app
```

---

## Bugs I Hit And Fixed

### Profile schema export

`backend/app/schema/profile.py` defines:

```text
ProfileCreate
ProfileResponse
```

But `backend/app/schema/__init__.py` did not export them.

So this line failed:

```python
from app.schema import (
    ProfileCreate,
    ProfileResponse,
)
```

Fix:

```python
from .profile import ProfileCreate, ProfileResponse
```

### Session helper import

`backend/app/service/get_user_id.py` imported auth from:

```python
from backend.app.service.auth import _hash_session_token
```

That path is wrong when the backend is running from the `backend` folder.

Fix:

```python
from app.service.auth import _hash_session_token
```

### Profile router registration

`backend/app/router/__init__.py` only exposed auth/university routing before.

So the profile route file existed, but `/profile` was not visible in the
FastAPI app.

Fix:

```python
routers = (
    university_router,
    auth_router,
    profile_router,
)
```

Then `main.py` includes each router:

```python
for router in routers:
    app.include_router(router)
```

---

## Things I learned

- Profile creation needs a logged-in user, so it starts from the session cookie.
- `FormData` is needed when text fields and files are sent together.
- The browser should set the multipart `Content-Type` by itself.
- `UploadFile` is how FastAPI receives files.
- Cloudinary returns a `secure_url`, and that is what should be stored.
- `ON CONFLICT (user_id)` lets profile creation also work as profile update.
- `COALESCE(EXCLUDED.profile_pic, profile.profile_pic)` keeps the old picture when no new picture is uploaded.
- JSONB is useful for list fields like interests, music, movies, and websites.
- A route file existing is not enough; imports and router wiring also have to work.

---

[<- Back to Index](./README.md)
