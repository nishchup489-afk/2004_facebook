# Friends Flow

Friends are the social graph part of Thefacebook.

The page is:

```text
frontend/friends.html
```

![Friends page](./screenshots/friends-page.png)

The routes start at:

```text
/friends
```

---

## Latest main checked

This branch includes the local friendship feature from:

```text
0a1efb9 feat: add friendship system
```

Important files:

```text
frontend/friends.html
frontend/scripts/friends.js
backend/app/router/friends.py
backend/app/service/friends.py
backend/app/schema/friends.py
backend/tests/test_friendship_status.py
```

---

## Friend States

The database stores one row for a pair of users.

The table is:

```text
friendships
```

Important columns:

```text
user_id_low
user_id_high
requested_by
status
```

The database status can be:

```text
pending
accepted
rejected
```

But the frontend needs more detail.

So the service converts it into:

```text
pending_sent
pending_received
accepted
none
```

Example:

```text
requested_by == current_user_id
        |
        v
pending_sent
```

That means the UI should say:

```text
Requested
```

If the other person sent it:

```text
pending_received
        |
        v
Pending + Accept / Reject
```

---

## Send Request

Route:

```text
POST /friends/{target_user_id}
```

Flow:

```text
click Add as Friend
        |
        v
POST /friends/{id}
        |
        v
normalize pair
        |
        v
insert friendships row
        |
        v
status = pending
```

The pair is normalized so this:

```text
7 -> 12
```

and this:

```text
12 -> 7
```

still point to one friendship row.

---

## Suggestions

Route:

```text
GET /friends/suggestions
```

Suggestions are from the same university.

They can also explain why someone appears:

```text
Same university
Also looking for Networking
1 mutual friend
Request pending
Sent you a request
```

Important behavior:

```text
pending requests do not disappear
```

If I send a request, that person can still stay in suggestions with:

```text
Requested
```

That is better than the row vanishing and making the user wonder what happened.

---

## Homepage

The homepage also shows:

```text
People You May Know
```

It uses the same suggestions route:

```text
GET /friends/suggestions
```

So the homepage and friends page agree about:

```text
Requested
Pending
Friends
```

---

## Test I Ran

Tests:

```text
backend/tests/test_friendship_status.py
backend/tests/test_profile_creation.py
```

Command:

```text
python -B -m pytest tests/test_courses.py tests/test_search.py tests/test_friendship_status.py tests/test_profile_creation.py -v -p no:cacheprovider
```

Result:

```text
15 passed
```

The friendship tests check:

```text
pending request sent by me becomes pending_sent
pending request sent to me becomes pending_received
accepted friendship stays accepted
pending suggestions stay visible
suggestion reason says Request pending
```

---

## Things I learned

- A friendship row is shared by two users, so pair normalization matters.
- `pending` is not enough for the UI by itself.
- The UI needs to know who requested the friendship.
- Suggestions should keep pending rows visible, not hide them.
- Homepage, search, profile, friends, and courses should all use the same labels.

---

[<- Back to Index](./README.md)
