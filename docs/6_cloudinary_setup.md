# Cloudinary Setup

Cloudinary is for storing uploaded profile pictures.

The app should not store image files directly inside the frontend folder.

Instead the flow should become:

```text
user chooses profile picture

        |
        v

backend receives image

        |
        v

backend uploads image to Cloudinary

        |
        v

Cloudinary returns secure_url

        |
        v

database stores profile_pic URL
```

Right now the latest main commit added the Cloudinary setup.

It did not fully connect profile picture upload to the `/profile` backend
flow yet.

---

## Latest commit checked

```text
da62fd3 Feature added: cloudinary setup
```

Important files:

```text
backend/app/config/config.py
backend/app/config/media.py
backend/tests/test_cloudinary.py
backend/tests/test.webp
frontend/complete_profile.html
frontend/profile.html
frontend/scripts/complete_profile.js
```

---

## Profile Picture In The UI

The complete profile page now has a file input.

![Complete profile picture input](./screenshots/cloudinary-complete-profile.png)

The HTML part:

```html
<input
    type="file"
    id="profile_pic"
    name="profile_pic"
    accept="image/*"
>
```

This means the browser lets the user choose an image file.

But choosing a file is only the frontend part.

The backend still needs to receive it and upload it.

---

## Profile Page

The profile page has a picture area.

![Profile page picture area](./screenshots/cloudinary-profile-page.png)

Right now it points to:

```html
src="/frontend/assets/default-profile.png"
```

Later this should come from the database:

```text
profile.profile_pic
```

That value should be the Cloudinary `secure_url`.

---

## Environment Variables

File:

```text
backend/app/config/config.py
```

Cloudinary needs three secrets:

```text
CLOUDINARY_CLOUD_NAME
CLOUDINARY_API_KEY
CLOUDINARY_API_SECRET
```

The config file reads them from `.env`:

```python
CLOUDINARY_CLOUD_NAME = os.getenv(
    "CLOUDINARY_CLOUD_NAME"
)

CLOUDINARY_API_KEY = os.getenv(
    "CLOUDINARY_API_KEY"
)

CLOUDINARY_API_SECRET = os.getenv(
    "CLOUDINARY_API_SECRET"
)
```

Then it checks that all of them exist:

```python
if not all([
    CLOUDINARY_CLOUD_NAME,
    CLOUDINARY_API_KEY,
    CLOUDINARY_API_SECRET,
]):
    raise RuntimeError(
        "Cloudinary environment variables are not configured"
    )
```

This is good because the app should fail early if media upload cannot work.

No real secret values should be committed.

---

## Media Config

File:

```text
backend/app/config/media.py
```

This file configures the Cloudinary SDK.

```python
cloudinary.config(
    cloud_name=CLOUDINARY_CLOUD_NAME,
    api_key=CLOUDINARY_API_KEY,
    api_secret=CLOUDINARY_API_SECRET,
    secure=True,
)
```

`secure=True` matters.

It makes Cloudinary return HTTPS URLs.

So image URLs should look like:

```text
https://res.cloudinary.com/...
```

Not:

```text
http://res.cloudinary.com/...
```

---

## Test Upload

File:

```text
backend/tests/test_cloudinary.py
```

The test upload does:

```python
result = cloudinary.uploader.upload(
    "tests/test.webp",
    folder="thefacebook/test",
)
```

Then it prints:

```python
print(result["secure_url"])
```

So the basic check is:

```text
local test.webp

        |
        v

upload to Cloudinary folder thefacebook/test

        |
        v

Cloudinary returns secure_url
```

That proves the credentials and SDK config are working.

---

## Important Test Note

`test_cloudinary.py` talks to the real Cloudinary account.

So it is not like a normal fast unit test.

It needs:

```text
real env vars
internet access
real Cloudinary upload
```

Also, the upload runs at the top level of the file.

So if pytest imports this file, the upload can happen during collection.

For now it works as a manual smoke test.

Later it may be cleaner to make it explicit:

```text
manual cloudinary smoke test
```

or mark it so it does not run every time.

---

## Current Gap In Main

The frontend form has:

```text
profile_pic file input
```

But in commit `da62fd3`, `frontend/scripts/complete_profile.js` builds a
JSON object.

```javascript
const profile = {
    username: username,
    gender: gender || null,
    status: status || null,
    ...
};
```

Then it sends:

```javascript
headers: {
    "Content-Type": "application/json"
}
```

That means in the latest main commit, the image file is not being sent yet.

For file upload, this will probably need:

```text
FormData
multipart/form-data
FastAPI UploadFile
Cloudinary upload
profile_pic secure_url saved in database
```

---

## Future Profile Picture Flow

The full version should look like this:

```text
complete_profile.html

        |
        v

user selects image

        |
        v

FormData sends text fields + image

        |
        v

POST /profile

        |
        v

FastAPI reads UploadFile

        |
        v

Cloudinary upload

        |
        v

secure_url

        |
        v

profile.profile_pic

        |
        v

profile.html displays image
```

---

## Things I learned

- Cloudinary stores the actual image file outside my app.
- The app should store the Cloudinary URL, not the image bytes.
- `secure=True` makes Cloudinary return HTTPS URLs.
- Cloudinary credentials belong in environment variables.
- A file input alone does not upload a file.
- JSON requests are not enough for image upload.
- Profile image upload will need `FormData` on the frontend and `UploadFile` on the backend.
- A test that uploads to Cloudinary is a real integration smoke test, not a normal unit test.

---

[<- Back to Index](./README.md)
