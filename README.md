<h1 align="center">[ thefacebook ]</h1>

<h3 align="center">What if you rebuilt a 2004 university social network to learn how the web actually works?</h3>

<p align="center">A full-stack, Facebook-inspired learning project built with plain HTML, CSS, JavaScript, FastAPI, PostgreSQL, and raw SQL.</p>

<!-- Add the LinkedIn, X, and blog URLs here when they are published. -->
<p align="center">
  <a href="https://2004-facebook.vercel.app"><strong>Live Preview</strong></a> ·
  <a href="https://lnkd.in/p/e3PxnCqb"><strong>LinkedIn Post</strong> </a>·
  <a href="https://x.com/Nishchup489/status/2093128692843069785?s=20"><strong>X Post</strong> </a>· ·
  <strong>Detailed Blog — coming soon</strong>
</p>

<p align="center">
  <a href="https://2004-facebook.vercel.app"><img alt="Frontend on Vercel" src="https://img.shields.io/badge/frontend-Vercel-000000?style=flat-square&amp;logo=vercel"></a>
  <img alt="FastAPI backend" src="https://img.shields.io/badge/backend-FastAPI-009688?style=flat-square&amp;logo=fastapi&amp;logoColor=white">
  <img alt="PostgreSQL database" src="https://img.shields.io/badge/database-PostgreSQL-4169E1?style=flat-square&amp;logo=postgresql&amp;logoColor=white">
  <img alt="Python 3.14" src="https://img.shields.io/badge/python-3.14-3776AB?style=flat-square&amp;logo=python&amp;logoColor=white">
  <img alt="MIT License" src="https://img.shields.io/badge/license-MIT-4267B2?style=flat-square">
</p>

> **30-second version:** this is a working university social network inspired by Thefacebook's early product idea. Students receive a fake university identity, register with a one-time code, create a profile, search their school, add friends, discover mutual connections, and join courses. The frontend uses no framework. The backend uses FastAPI, PostgreSQL, raw SQL, and server-side sessions.

![alt text](image.png)

## Why I built this

I saw a question on X:

> No documentation. No YouTube tutorials. No AI. How did people build products like Facebook in 2004?

That question stuck with me.

Modern frameworks are useful, but they can hide the system underneath. I wanted to slow down and understand the real pieces: browser requests, cookies, authentication, relational data, SQL joins, file uploads, CORS, deployment, and the edge cases connecting them.

This is not a historically exact Facebook clone. It recreates the **spirit of building an early university network with fewer abstractions**.

> Build slowly. Think deeply. Understand everything.

## What you can do

| Feature | What happens |
|---|---|
| University admission | Generate a fake university email and one-time registration code |
| Registration | Claim an eligible student record and create an account |
| Authentication | Log in through an HttpOnly cookie and server-side session |
| Profiles | Add personal, academic, contact, and profile-picture information |
| People search | Filter people by name, university, status, relationship, and interests |
| Friendships | Send, accept, reject, and remove friend connections |
| Discovery | See suggestions, mutual friends, and people from the same university |
| Courses | Find courses, enroll, leave, and discover classmates |

## The core journey

```text
university admission
        ↓
email + one-time registration code
        ↓
create account
        ↓
HttpOnly session cookie
        ↓
build a profile
        ↓
search people → add friends → join courses
```

Registration is tied to university data instead of being a plain “insert a user” form:

```text
POST /register
      ↓
verify student + registration code
      ↓
hash password with Argon2
      ↓
create user + mark student claimed
      ↓
store SHA-256(session token) in PostgreSQL
      ↓
send raw token only as an HttpOnly cookie
```

## Product tour

### Join the university network

The project starts with a fake university admission flow. It creates the identity and registration code needed to join the network.

![Thefacebook registration page](docs/screenshots/register-university-email-box.png)

### Create a real profile

Profiles include school information, contact details, interests, relationship fields, and a Cloudinary-hosted profile picture.

![Thefacebook profile creation form](docs/screenshots/profile-creation-form.png)

### Search the directory

Search is not limited to names. Results can be filtered using the structured profile data stored in PostgreSQL.

![Thefacebook people search](docs/screenshots/search-page.png)

### Build a social graph

Friend requests move through pending, accepted, rejected, and removed states. Suggestions can use university, profile compatibility, and mutual friends.

![Thefacebook friends page](docs/screenshots/friends-page.png)

### Find classmates

Students can search the course catalog, enroll in courses, and see who shares their classes.

![Thefacebook courses page](docs/screenshots/courses-page.png)

## Architecture

```mermaid
flowchart LR
    B[Browser<br/>HTML + CSS + JavaScript]
    A[FastAPI<br/>routers + schemas]
    S[Service layer<br/>business logic + raw SQL]
    D[(PostgreSQL<br/>Neon)]
    C[Cloudinary<br/>profile images]

    B -->|JSON + session cookie| A
    A --> S
    S --> D
    S --> C
```

The backend stays intentionally small:

```text
request
   ↓
router        HTTP, validation, response status
   ↓
service       application rules and SQL
   ↓
PostgreSQL    durable relational state
```

The database models the network directly:

```text
universities → students → users → profiles
                         ↘ sessions
                         ↘ friendships
                         ↘ enrollments → courses
                         ↘ wall_posts
```

## Stack

| Layer | Technology | Why it is here |
|---|---|---|
| UI | HTML + CSS | Learn layout and browser fundamentals without a component framework |
| Client logic | Vanilla JavaScript | Work directly with forms, DOM state, Fetch, and browser storage |
| API | FastAPI + Pydantic | Typed request/response boundaries with a small Python backend |
| Data access | Psycopg + raw SQL | Understand queries, joins, transactions, and constraints directly |
| Database | PostgreSQL on Neon | Relational storage for identity, sessions, friendships, and courses |
| Passwords | Argon2 | Store slow, salted password hashes instead of plaintext passwords |
| Sessions | HttpOnly cookies | Keep raw session tokens out of frontend JavaScript |
| Media | Cloudinary | Store and deliver uploaded profile pictures |
| Hosting | Vercel + Render | Static frontend on Vercel; FastAPI backend on Render |
| Tests | Pytest | Verify important behavior around auth, profiles, search, friends, and courses |

## Security decisions

- Passwords are hashed with **Argon2**.
- Authentication uses **server-side sessions**, not passwords sent on every request.
- The browser receives the raw session token in an **HttpOnly** cookie.
- PostgreSQL stores only a **SHA-256 hash** of that token.
- Registration codes are one-time credentials tied to eligible student records.
- Protected routes resolve the authenticated user from the current session.
- Production requests use HTTPS and cross-origin credentials.

This is an educational project, not a production identity provider. See the implementation docs for the exact decisions and tradeoffs.

## Run it locally

### Prerequisites

- Python 3.14+
- [Poetry](https://python-poetry.org/)
- PostgreSQL
- A Cloudinary account

### 1. Clone the project

```bash
git clone https://github.com/nishchup489-afk/2004_facebook.git
cd 2004_facebook
```

### 2. Configure the backend

Create `backend/.env`:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST/DATABASE
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
COOKIE_NAME=thefacebook_session
COOKIE_MAX_AGE=604800
```

Never commit this file. The database URL and Cloudinary values are secrets.

### 3. Create the database

From `backend/`:

```bash
psql "$DATABASE_URL" -f database/query/schema.sql
psql "$DATABASE_URL" -f database/query/seed.sql
```

### 4. Start FastAPI

```bash
cd backend
poetry install
poetry run python -m uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`. FastAPI's interactive API docs are at `http://127.0.0.1:8000/docs`.

### 5. Start the frontend

In a second terminal, from the project root:

```bash
python3 -m http.server 3000
```

Open `http://127.0.0.1:3000/frontend/index.html`.

## Tests

```bash
cd backend
poetry run pytest
```

The suite covers the behavior that would hurt most if it broke: registration, login, sessions, profile creation, search, friendships, courses, and Cloudinary integration boundaries.

## Project map

```text
2004_facebook/
├── frontend/
│   ├── scripts/          browser behavior and API calls
│   ├── styles/           page-specific styling
│   └── *.html            the application pages
├── backend/
│   ├── app/
│   │   ├── router/       HTTP endpoints
│   │   ├── schema/       Pydantic request/response models
│   │   └── service/      business logic and SQL
│   ├── database/query/   schema and seed data
│   └── tests/            pytest suite
├── docs/                 visual, feature-by-feature build notes
└── design/               historical UI references
```

## Deep-dive documentation

The docs follow the project in the order it was built:

1. [Database design](docs/0_database_docs.md)
2. [Frontend ↔ backend connection](docs/1_frontend_backend_connection.md)
3. [University admission](docs/2_university_admission_flow.md)
4. [Registration](docs/3_registration_flow.md)
5. [Login](docs/4_login_flow.md)
6. [Sessions](docs/5_session_flow.md)
7. [Cloudinary setup](docs/6_cloudinary_setup.md)
8. [Profile creation](docs/7_profile.md)
9. [Profile retrieval](docs/8_get_profile.md)
10. [Search](docs/9_search.md)
11. [Friends](docs/10_friends.md)
12. [Courses](docs/11_courses.md)

Or start from the [documentation index](docs/README.md).

## What I learned

- Authentication is a flow across the browser, API, cookie, hashing, and database—not one login function.
- Social features become much clearer when friendship states are modeled explicitly.
- Raw SQL makes data relationships and performance tradeoffs impossible to ignore.
- Simple frontend code can still support a substantial product when responsibilities stay clear.
- Deployment is part of the system: CORS, HTTPS cookies, environment values, and service URLs must agree.

## Contributing

Small, focused contributions are welcome—especially tests, documentation, accessibility, SQL improvements, security fixes, and historically appropriate UI polish.

Read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request.

## Disclaimer

This independent educational project is inspired by the early university-network concept of Thefacebook. It is not affiliated with, endorsed by, or connected to Meta Platforms, Inc. or Facebook.

## License

Released under the [MIT License](LICENSE).

<p align="center"><strong>Built to understand the stack—not to hide it.</strong></p>
