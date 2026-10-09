# Event Planner

Event Planner is a full-stack web app for creating events, inviting registered users, collecting RSVPs, and searching the events you take part in. Organizers manage the guest list. Invitees answer **Going**, **Maybe**, or **Not Going**.

The stack is an Angular frontend, a FastAPI backend, and MongoDB.

## Features

- Sign up and log in with email and password. Passwords are hashed with bcrypt, and login returns a JWT that the frontend stores in `localStorage`.
- Create events with a title, description, date, time, and location. Each event gets a sequential integer id.
- See two lists on the events page: events you organize, and events you were invited to.
- Invite only people who already have an account. Only the organizer can send invitations.
- RSVP as an invitee. Organizers are treated as attending and cannot submit a response.
- View the attendee list and a response summary (Going, Maybe, Not Going, No Response). Only the organizer can open this page.
- Delete an event. Only the organizer can delete it.
- Search by keyword (title or description, case-insensitive), date, and role (`organizer` or `attendee`).

## Architecture

```text
Browser (Angular, :4200)
        |
        |  HTTP + Bearer JWT
        v
FastAPI (uvicorn, :8000)
        |
        v
MongoDB (event_planner, :27017)
```

| Layer | Technology | Role |
| --- | --- | --- |
| Frontend | Angular 20 | Pages for auth, events, invites, RSVPs, search, and attendees |
| Backend | FastAPI, Uvicorn, Pydantic | REST API, validation, and JWT checks |
| Database | MongoDB 7 | Users, events, and the event-id counter |
| Auth | python-jose (HS256), passlib (bcrypt) | Access tokens expire after 60 minutes |

The API allows requests from `http://localhost:4200` and `http://frontend:80`. Interactive docs are served by FastAPI at `/docs` (Swagger UI) and `/redoc`.

## Project structure

```text
EventPlanner/
├── main.py                      # FastAPI app, CORS, and routers
├── config.py                    # JWT settings loaded from the environment
├── database.py                  # MongoDB connection and collections
├── requirements.txt
├── Dockerfile                   # Backend image
├── docker-compose.yaml          # MongoDB, backend, and frontend
├── test_connection.py           # Standalone MongoDB connectivity check
├── models/
│   ├── auth_models/user.py      # Signup and login body
│   └── event_model/event_model.py
├── routes/
│   ├── auth_routes.py           # /auth
│   ├── event_routes.py          # create, list, invite, delete
│   ├── response_routes.py       # RSVP and attendee list
│   ├── search_routes.py         # /events/search
│   └── test_routes.py           # /test-db
├── utils/auth_utils.py          # Hashing and token creation
└── frontend/eventplanner-frontend/
    ├── Dockerfile               # Production Angular build served by nginx
    └── src/app/
        ├── home/                # Landing page
        ├── components/          # Login, signup, events, invite, search, attendees
        └── service/             # AuthService and EventService
```

## Prerequisites

For Docker:

- Docker and Docker Compose

For a local run:

- Python 3.11
- Node.js 20
- MongoDB 7 listening on port `27017`

## Configuration

Create a `.env` file in the project root. The backend refuses to start if `SECRET_KEY` is missing.

```env
SECRET_KEY=replace-with-a-long-random-string
MONGO_URL=mongodb://127.0.0.1:27017
```

| Variable | Required | Used by | Meaning |
| --- | --- | --- | --- |
| `SECRET_KEY` | Yes | `config.py`, `utils/auth_utils.py` | Secret used to sign JWTs (HS256) |
| `MONGO_URL` | No | `database.py` | MongoDB connection string. Defaults to `mongodb://127.0.0.1:27017` |

Keep `.env` out of version control. Docker Compose reads `SECRET_KEY` from the shell and falls back to `SECRETKEY123` when it is unset. Inside Compose, the backend connects with `MONGO_URL=mongodb://db:27017`.

The Angular services call the API at `http://127.0.0.1:8000`. That address works when the API is published on the host, including the Docker setup below.

## Run with Docker

From the project root:

```bash
docker compose up --build
```

| Service | URL |
| --- | --- |
| Frontend | http://localhost:4200 |
| API | http://127.0.0.1:8000 |
| Swagger UI | http://127.0.0.1:8000/docs |
| MongoDB | `localhost:27017` |

MongoDB data is stored in the `mongodata` volume. Stop the stack with `docker compose down`. Add `-v` only when you intend to delete that data.

## Run locally

### 1. Start MongoDB

Use a local MongoDB instance on port `27017`, or start only the database service:

```bash
docker compose up db
```

Optional connectivity check, after `.env` contains `MONGO_URL`:

```bash
python test_connection.py
```

### 2. Start the API

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

macOS and Linux:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Start the frontend

```bash
cd frontend/eventplanner-frontend
npm install
npm start
```

Open http://localhost:4200.

## Using the app

1. Open the home page and create an account.
2. Log in. The app stores the access token and opens the events page.
3. Create an event. It appears under **My Organized Events**.
4. Invite another registered user by email.
5. Log in as that user. The event appears under **Events I'm Invited To**, where they can respond.
6. As the organizer, open **View Attendees** to see each response and the summary counts.
7. Use **Search Events** to filter by keyword, a start date, and role.

## API

Protected routes expect:

```http
Authorization: Bearer <access_token>
```

Tokens expire after 60 minutes. A missing, malformed, or expired token returns `401`.

### Authentication

| Method | Path | Body | Success |
| --- | --- | --- | --- |
| `POST` | `/auth/signup` | `{ "email", "password" }` | `{ "message": "User registered successfully" }`. `400` if the email already exists |
| `POST` | `/auth/login` | `{ "email", "password" }` | `{ "access_token", "token_type": "bearer", "message" }`. `401` for bad credentials |

### Events

| Method | Path | Who | What it does |
| --- | --- | --- | --- |
| `POST` | `/events/create` | Any logged-in user | Creates an event. The caller is stored as organizer and as the first attendee |
| `GET` | `/events/my-events` | Any logged-in user | Events where you are the organizer |
| `GET` | `/events/invited` | Any logged-in user | Events where your attendee role is `attendee` |
| `GET` | `/events/me` | Any logged-in user | Events you organize or attend |
| `POST` | `/events/invite` | Organizer | Adds a registered user as an attendee |
| `DELETE` | `/events/{event_id}` | Organizer | Deletes the event |

Create body:

```json
{
  "title": "Team offsite",
  "description": "Planning session for the next release",
  "date": "2026-11-02",
  "time": "14:00",
  "location": "Room 4"
}
```

Invite body:

```json
{
  "event_id": "1",
  "email": "guest@example.com"
}
```

`event_id` must be a positive integer. Inviting an unknown email returns `404`. Inviting someone who is already on the list returns `400`. A non-organizer receives `403`.

### RSVPs and attendees

| Method | Path | Who | What it does |
| --- | --- | --- | --- |
| `POST` | `/events/{event_id}/respond` | Invitee | Sets `Going`, `Maybe`, or `Not Going` |
| `GET` | `/events/{event_id}/attendees` | Organizer | Returns attendees plus a response summary |

Respond body:

```json
{ "response": "Going" }
```

Organizers who call the respond endpoint receive `400`. Users who are not on the attendee list receive `403`.

### Search

`GET /events/search`

| Query | Format | Effect |
| --- | --- | --- |
| `keyword` | string, max 200 characters | Case-insensitive match on title or description |
| `start_date` | `YYYY-MM-DD` | Events on or after this date |
| `end_date` | `YYYY-MM-DD` | Events on or before this date |
| `role` | `organizer` or `attendee` | Limits results to events you organize, or events you attend but do not organize |

Dates are stored and compared as `YYYY-MM-DD` strings. `start_date` must be on or before `end_date`. The response includes `results`, `count`, and `filters_applied`.

The search page sends `keyword`, a single date as `start_date`, and `role`. The API also accepts `end_date` for a range.

With no `role`, keyword and date filters run across events in the database. With `role=organizer` or `role=attendee`, results are limited to your events.

### Development endpoint

`GET /test-db` inserts a document into the `users` collection to confirm the database is reachable. It is not part of the product flow.

## Data model

Database name: `event_planner`.

**users**

| Field | Notes |
| --- | --- |
| `email` | Unique in practice; signup rejects a duplicate |
| `password` | bcrypt hash |
| `created_at` | UTC timestamp |

**events**

| Field | Notes |
| --- | --- |
| `_id` | Integer from the `counters` collection, starting at 1 |
| `title`, `description`, `date`, `time`, `location` | Supplied at creation |
| `organizer` | Email of the creator |
| `attendees` | `{ email, role, response?, response_updated_at? }` |
| `created_at` | UTC timestamp |

The creator is inserted with role `organizer`. Invited users are inserted with role `attendee` and no response until they RSVP.

**counters**

A single document, `_id: "event_id"`, holds `sequence_value`. Creating an event increments it and uses the new value as the event id.

List and search responses add `id`, `user_role`, `is_organizer`, and `user_response` for the caller. They do not replace the stored document.

## Frontend routes

| Path | Page |
| --- | --- |
| `/` | Home, with links to sign up and log in |
| `/signup` | Create an account |
| `/login` | Log in and store the access token |
| `/events` | Create events, list organized and invited events, RSVP, delete |
| `/events/invite/:id` | Invite a registered user to that event |
| `/events/attendees/:id` | Organizer view of responses |
| `/events/search` | Keyword, date, and role filters |

## Typical request flow

```http
POST /auth/signup
{ "email": "ada@example.com", "password": "a-strong-password" }

POST /auth/login
{ "email": "ada@example.com", "password": "a-strong-password" }

POST /events/create
Authorization: Bearer <token>
{ "title": "Demo", "description": "First event", "date": "2026-12-01", "time": "18:00", "location": "Hall A" }
```

A successful create returns `{ "message": "Event created successfully", "event_id": 1 }`.
