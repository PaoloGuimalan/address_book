# Address Book API

A FastAPI backend for a personal address book. Users register, log in to receive a JWT, and manage their own addresses. GPS coordinates are filled in automatically through OpenStreetMap Nominatim when an address is created or its location changes, and can be set by hand on update. A public endpoint finds stored addresses within a radius of any point.

- **Framework:** FastAPI, Pydantic v2, SQLAlchemy 2
- **Database:** SQLite by default. PostgreSQL and MySQL are supported through the same settings.
- **Auth:** bcrypt password hashes, HS256 JWT bearer tokens
- **Geocoding:** `geopy` + Nominatim (needs outbound internet access)

> **Interactive API docs (Swagger UI):** once the server is running, open **http://127.0.0.1:8000/docs** to browse every endpoint, see its fields and responses, and call it from the browser, including with your login token. A read-only ReDoc view is at **http://127.0.0.1:8000/redoc**. See [Try it in Swagger UI](#5-try-it-in-swagger-ui) for a walkthrough.

---

## How to execute

### Prerequisites

- Python **3.10 or newer** (developed on 3.11)
- Internet access, because creating or relocating an address calls Nominatim

Run every command below from the **project root** (the folder containing `requirements.txt`).

### 1. Create and activate a virtual environment

```bash
python -m venv .venv
```

Activate it:

| Shell | Command |
| --- | --- |
| Windows PowerShell | `.venv\Scripts\Activate.ps1` |
| Windows cmd | `.venv\Scripts\activate.bat` |
| macOS / Linux / Git Bash | `source .venv/bin/activate` |

### 2. Install the requirements

```bash
pip install -r requirements.txt
```

### 3. Provide the `.env` file

Copy the template and edit it:

```bash
cp .env.example .env              # macOS / Linux / Git Bash
Copy-Item .env.example .env       # Windows PowerShell
```

**`SECRET_KEY` must be set to a non-empty value.** The template leaves it blank, and with a blank key every login fails with `500 Internal Server Error` (`HMAC key must not be empty`). Generate one with:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Example `.env` for local development:

```dotenv
APP_ENV=dev
PROJECT_NAME="Address Book"
DB_TYPE=sqlite
DB_NAME=address_book
DB_USER=
DB_PASSWORD=
DB_HOST=
DB_PORT=
SECRET_KEY=paste-the-generated-value-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

| Variable | Required | Default in code | Description |
| --- | --- | --- | --- |
| `SECRET_KEY` | **Yes** | insecure placeholder | Key used to sign JWTs. Use a long random string. |
| `ALGORITHM` | No | `HS256` | JWT signing algorithm. |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | No | `60` | Token lifetime in minutes. |
| `PROJECT_NAME` | No | `FastAPI Factory Architecture` | Title shown in Swagger/ReDoc and in the `GET /` welcome message. |
| `DB_TYPE` | No | `sqlite` | `sqlite`, `postgres` / `postgresql`, or `mysql`. |
| `DB_NAME` | No | `address_book` | Database name. With SQLite this is the file `./<DB_NAME>.db`, created in the directory you start the server from. |
| `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` | Only for PostgreSQL / MySQL | empty | Connection details for network databases. Ignored by SQLite. |
| `APP_ENV` | No | `development` | Environment label. Loaded into settings but not used by any code path yet. |
| `LOG_LEVEL`, `LOG_FILE_PATH` | No | n/a | Listed in `.env.example` but not read. Logging is fixed at `INFO`, written to stdout and to `logs/<module>.log`. |

#### SQLite (default): nothing extra to install

With `DB_TYPE=sqlite`, the database sets itself up. SQLite ships with Python, so you don't need a separate driver, server, or install step. On first start the app creates the database file `./<DB_NAME>.db` (by default `address_book.db` in the project root) and builds all of its tables. Leave `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT` empty.

To start over with an empty database, stop the server, delete the `.db` file, and start the server again.

#### Using PostgreSQL or MySQL (optional)

Neither database driver is in `requirements.txt`, so install the one you need:

```bash
pip install psycopg2-binary   # DB_TYPE=postgres
pip install pymysql           # DB_TYPE=mysql
```

Then set `DB_TYPE`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, and `DB_PORT`. The database itself must already exist. The app creates the tables but not the database.

### 4. Run the development server

```bash
fastapi dev app/main.py
```

- The API is served at **http://127.0.0.1:8000** with auto-reload on.
- **Swagger UI: http://127.0.0.1:8000/docs**, the easiest way to explore and test the API (see step 5). ReDoc is at **http://127.0.0.1:8000/redoc**, and the raw OpenAPI schema is at `/openapi.json`.
- On startup the app creates any missing tables (`user_accounts`, `user_addresses`). There are no migrations to run.
- Logs go to the console and to one file per module in `logs/`. The folder is created automatically on first start.
- Start the server from the project root. The source uses top-level imports (`from utils...`, `from api...`), and the FastAPI CLI puts `app/` on the import path for that. `.env`, the SQLite file, and `logs/`, however, are resolved relative to the current directory.

Useful variations:

```bash
fastapi dev app/main.py --port 8080           # different port
fastapi dev app/main.py --host 0.0.0.0        # reachable from other devices on the network
fastapi run app/main.py                       # production mode: no reload, binds 0.0.0.0:8000
```

Quick smoke test:

```bash
curl http://127.0.0.1:8000/health
# {"status":"healthy","database":{"engine":"sqlite","connected":true}}
```

### 5. Try it in Swagger UI

Open **http://127.0.0.1:8000/docs**. Endpoints are grouped into **Checks**, **Auth**, **Users**, and **Address**. Expand any endpoint and click **Try it out**, fill in the fields, then click **Execute** to see the real response.

1. **Register:** under **Auth**, run `POST /api/v1/auth/register` with a JSON body such as
   `{"username": "jdoe", "email": "jdoe@example.com", "name": "John Doe", "password": "supersecret1"}`. Expect `201`.
2. **Log in:** run `POST /api/v1/auth/login` with `{"username_or_email": "jdoe", "password": "supersecret1"}` and copy the `access_token` value from the response.
3. **Authorize:** click the **Authorize** button (padlock, top right), paste **only the token** (no `Bearer ` prefix), click **Authorize**, then **Close**. The padlocks on protected endpoints close, and Swagger sends the token with every request from now on. Tokens expire after `ACCESS_TOKEN_EXPIRE_MINUTES` (default 60). After that, log in again and re-authorize.
4. **Create an address:** run `POST /api/v1/address/`. It shows form fields for the address text only. Coordinates aren't asked for, because they're looked up automatically.
5. **See it:** run `GET /api/v1/address/my-list`. The new address appears with `latitude` and `longitude` filled in.
6. **Edit it:**
   - `PUT /api/v1/address/{address_id}` is a form with every field. Leave `latitude`/`longitude` empty to have them looked up again, or fill in both to set them by hand.
   - `PATCH /api/v1/address/{address_id}` takes JSON. **Swagger pre-fills every field** (`"string"`, `0`), so delete the lines for fields you don't want to change before clicking Execute. Otherwise the address is overwritten with those placeholder values and moved to coordinates 0, 0.
7. **Search nearby:** `GET /api/v1/nearby/` needs no login. Enter `latitude`, `longitude`, and optionally `radius_km`/`limit`.

---

## What endpoints it consists of

| Method | Path | Auth | Description |
| --- | --- | --- | --- |
| `GET` | `/health` | Public | Liveness check that also runs `SELECT 1` against the database |
| `GET` | `/ready` | Public | Readiness probe |
| `POST` | `/api/v1/auth/register` | Public | Create an account |
| `POST` | `/api/v1/auth/login` | Public | Exchange credentials for a JWT access token |
| `GET` | `/api/v1/user/list` | Bearer | Paginated list of all accounts |
| `GET` | `/api/v1/user/{username}` | Bearer | Account details by username **or** email |
| `GET` | `/api/v1/address/my-list` | Bearer | Paginated list of the caller's addresses |
| `GET` | `/api/v1/address/{address_id}` | Bearer, owner only | Get one address |
| `POST` | `/api/v1/address/` | Bearer | Create an address. Coordinates are looked up automatically, so don't send them. |
| `PUT` | `/api/v1/address/{address_id}` | Bearer, owner only | Replace every field of an address. Coordinates can be set by hand, or left blank to be looked up. |
| `PATCH` | `/api/v1/address/{address_id}` | Bearer, owner only | Update only the fields sent. Coordinates can be set by hand, or are looked up again when the location changes. |
| `DELETE` | `/api/v1/address/{address_id}` | Bearer, owner only | Delete an address |
| `GET` | `/api/v1/nearby/` | Public | Addresses from all accounts within a radius of a point |

Non-API routes: `GET /` (returns `"Welcome to <PROJECT_NAME>"`, hidden from the docs), `/docs`, `/redoc`, and `/openapi.json`.

---

## Endpoint documentation

### Conventions

**Base URL:** `http://127.0.0.1:8000`. The `curl` examples use bash syntax. On Windows, run them in Git Bash, or skip curl and use the [Swagger UI](#5-try-it-in-swagger-ui) at `/docs`, which accepts the same fields.

**Authentication.** Endpoints marked *Bearer* need the token returned by `POST /api/v1/auth/login`:

```
Authorization: Bearer <access_token>
```

In Swagger UI, click **Authorize** and paste only the token, without the `Bearer ` prefix. Tokens are HS256 JWTs whose `sub` claim is the account ID, and they expire after `ACCESS_TOKEN_EXPIRE_MINUTES`.

Every Bearer endpoint can return these two errors, so they are not repeated in each endpoint's table below:

| Status | Body | When |
| --- | --- | --- |
| `401` | `{"detail": "Not authenticated"}` | The `Authorization` header is missing |
| `401` | `{"detail": "Could not validate authorization signatures."}` | The token is malformed, has a bad signature, is expired, or belongs to an account that no longer exists or is inactive. Sent with a `WWW-Authenticate: Bearer` header. |

**Request content types.** Endpoints differ in the body format they accept. Sending the wrong one returns `422`.

| Endpoint | Body format |
| --- | --- |
| `POST /auth/register`, `POST /auth/login`, `PATCH /address/{id}` | `application/json` |
| `POST /address/`, `PUT /address/{id}` | Form data: `application/x-www-form-urlencoded` or `multipart/form-data` |

**Trailing slashes.** `POST /api/v1/address/` and `GET /api/v1/nearby/` are defined with a trailing slash. Without the slash the server answers `307 Temporary Redirect` to the slashed URL.

**Error bodies.** Errors raised by the app look like `{"detail": "<message>"}`. Validation failures return `422 Unprocessable Content` in FastAPI's standard format, with one entry per invalid field:

```json
{
  "detail": [
    {
      "type": "string_too_short",
      "loc": ["body", "username"],
      "msg": "String should have at least 3 characters",
      "input": "jd",
      "ctx": { "min_length": 3 }
    }
  ]
}
```

**Pagination.** List endpoints take `page` (1-based, default `1`) and `limit` (1–100, default `20`) as query parameters and return:

| Field | Type | Description |
| --- | --- | --- |
| `total_records` | int | Number of items **in this page**, not the overall total |
| `current_page` | int | The `page` that was requested |
| `limit` | int | The `limit` that was requested |
| `data` | array | The items in this page |

### Shared response objects

#### Address

Returned by every address endpoint except create and delete.

| Field | Type | Description |
| --- | --- | --- |
| `id` | int | Address ID |
| `account_id` | int | ID of the owning account |
| `title` | string | Label such as `Home` or `Office` (1–100 chars) |
| `street_address` | string | Street and building number (1–255 chars) |
| `city` | string | City (1–100 chars) |
| `state` | string | State, province, or region (1–100 chars) |
| `postal_code` | string | ZIP or postal code (1–20 chars) |
| `country` | string | Country (1–100 chars) |
| `latitude` | float | -90 to 90 |
| `longitude` | float | -180 to 180 |
| `created_at` | datetime | ISO 8601 creation timestamp |
| `updated_at` | datetime | ISO 8601 timestamp of the last change |

```json
{
  "title": "Home",
  "street_address": "1 Rizal Ave",
  "city": "Manila",
  "state": "Metro Manila",
  "postal_code": "1000",
  "country": "Philippines",
  "latitude": 14.5995,
  "longitude": 120.9842,
  "id": 1,
  "account_id": 1,
  "created_at": "2026-10-02T13:45:39",
  "updated_at": "2026-10-02T13:45:39"
}
```

#### Account (summary)

Used in `GET /api/v1/user/list`.

| Field | Type | Description |
| --- | --- | --- |
| `username` | string | Unique username |
| `name` | string | Display name |

#### Account (details)

Returned by `GET /api/v1/user/{username}`. The password hash is never returned.

| Field | Type | Description |
| --- | --- | --- |
| `id` | int | Account ID |
| `username` | string | Unique username (3–50 chars) |
| `email` | string | Unique email address |
| `name` | string | Display name (1–255 chars) |
| `is_active` | bool | Whether the account may log in |
| `is_superuser` | bool | Admin flag. Stored, but no endpoint uses it yet. |
| `created_at` | datetime | ISO 8601 creation timestamp |
| `updated_at` | datetime | ISO 8601 timestamp of the last change |

---

### Checks

#### `GET /health`

Checks that the app is running and that the database answers `SELECT 1`.

**Auth:** public. **Parameters:** none.

| Status | When | Body |
| --- | --- | --- |
| `200 OK` | The database query succeeded | `{"status": "healthy", "database": {"engine": "sqlite", "connected": true}}` |
| `503 Service Unavailable` | The database query failed | See below |

```json
{
  "detail": {
    "status": "unhealthy",
    "database": {
      "engine": "sqlite",
      "connected": false,
      "error": "Unable to communicate with the database container or file."
    }
  }
}
```

#### `GET /ready`

Readiness probe. Does not touch the database.

**Auth:** public. **Parameters:** none.

| Status | Body |
| --- | --- |
| `200 OK` | `{"status": "OK", "message": "ready"}` |

---

### Auth

#### `POST /api/v1/auth/register`

Creates an account. It returns no token, so call login afterward.

**Auth:** public. **Body:** `application/json`

| Field | Type | Required | Constraints |
| --- | --- | --- | --- |
| `username` | string | Yes | 3–50 chars, unique |
| `email` | string | Yes | Valid email address, unique |
| `name` | string | Yes | 1–255 chars |
| `password` | string | Yes | At least 8 chars. Stored as a bcrypt hash. |

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "jdoe", "email": "jdoe@example.com", "name": "John Doe", "password": "supersecret1"}'
```

| Status | When | Body |
| --- | --- | --- |
| `201 Created` | Account created | `{"message": "Account created successfully"}` |
| `400 Bad Request` | The username or email is already taken | `{"detail": "Username or Email address is already registered."}` |
| `422 Unprocessable Content` | A field is missing or breaks a constraint | Validation error list |

#### `POST /api/v1/auth/login`

Checks credentials and returns a bearer token.

**Auth:** public. **Body:** `application/json`

| Field | Type | Required | Constraints |
| --- | --- | --- | --- |
| `username_or_email` | string | Yes | The account's username **or** email, at least 1 char |
| `password` | string | Yes | At least 1 char |

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username_or_email": "jdoe@example.com", "password": "supersecret1"}'
```

| Status | When | Body |
| --- | --- | --- |
| `200 OK` | Credentials are valid | `{"access_token": "<jwt>", "token_type": "bearer"}` |
| `401 Unauthorized` | Unknown user or wrong password | `{"detail": "Invalid username/email or password credentials."}` |
| `403 Forbidden` | The account's `is_active` flag is false (only settable directly in the database) | `{"detail": "This account has been deactivated by an administrator."}` |
| `422 Unprocessable Content` | A field is missing or empty | Validation error list |

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzkwOTUyMzM5fQ.EphgxF0m...",
  "token_type": "bearer"
}
```

---

### Users

#### `GET /api/v1/user/list`

Paginated list of every account, active or not, showing only username and display name.

**Auth:** Bearer.

| Query param | Type | Default | Constraints |
| --- | --- | --- | --- |
| `page` | int | `1` | ≥ 1 |
| `limit` | int | `20` | 1–100 |

```bash
curl "http://127.0.0.1:8000/api/v1/user/list?page=1&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

| Status | When | Body |
| --- | --- | --- |
| `200 OK` | Success | Paginated list of Account summaries |
| `422 Unprocessable Content` | `page` or `limit` is out of range or not an integer | Validation error list |

```json
{
  "total_records": 2,
  "current_page": 1,
  "limit": 20,
  "data": [
    { "username": "jdoe", "name": "John Doe" },
    { "username": "asmith", "name": "Ann Smith" }
  ]
}
```

#### `GET /api/v1/user/{username}`

Full details of one account. The path value can be either the username or the email address. Any logged-in user can look up any account.

**Auth:** Bearer.

| Path param | Type | Description |
| --- | --- | --- |
| `username` | string | Username or email of the account |

```bash
curl http://127.0.0.1:8000/api/v1/user/jdoe \
  -H "Authorization: Bearer $TOKEN"
```

| Status | When | Body |
| --- | --- | --- |
| `200 OK` | Account found | Account details |
| `404 Not Found` | No account has that username or email | `{"detail": "Account not found"}` |

```json
{
  "username": "jdoe",
  "email": "jdoe@example.com",
  "name": "John Doe",
  "id": 1,
  "is_active": true,
  "is_superuser": false,
  "created_at": "2026-10-02T13:45:38",
  "updated_at": "2026-10-02T13:45:38"
}
```

---

### Address

All addresses belong to the account that created them. Every endpoint that takes `{address_id}` first returns `404` if the address doesn't exist, then `403` if it belongs to another account.

**Coordinates are filled in automatically.** You never need to supply `latitude` or `longitude`. The API looks them up from the address text, and you can still set them by hand when editing:

| Endpoint | Coordinates |
| --- | --- |
| `POST /address/` (create) | Always looked up automatically. Don't send them; they aren't accepted here. |
| `PUT /address/{id}` (replace) | Send **both** `latitude` and `longitude` to set them by hand. Leave either one blank or out, and both are looked up again from the new address text. |
| `PATCH /address/{id}` (partial update) | Send `latitude` and/or `longitude` to set them by hand. If you only change location text (`street_address`, `city`, `state`, `postal_code`, `country`), they're looked up again. If you only change `title`, they stay as they are. |

**Geocoding.** Coordinates come from Nominatim, using the query `"{street_address}, {city}, {state}, {postal_code}, {country}"` with a 5-second timeout. Any endpoint that triggers a lookup can also return:

| Status | Body | When |
| --- | --- | --- |
| `400 Bad Request` | `{"detail": "The provided address could not be resolved to valid GPS coordinates."}` | Nominatim found no match |
| `502 Bad Gateway` | `{"detail": "External Geolocation mapping server is temporarily unavailable or timed out."}` | Nominatim was unreachable, errored, or timed out |

Nominatim's public service allows about one request per second, so avoid bulk-creating addresses in tight loops.

#### `GET /api/v1/address/my-list`

Paginated list of the caller's addresses.

**Auth:** Bearer.

| Query param | Type | Default | Constraints |
| --- | --- | --- | --- |
| `page` | int | `1` | ≥ 1 |
| `limit` | int | `20` | 1–100 |

```bash
curl "http://127.0.0.1:8000/api/v1/address/my-list?page=1&limit=20" \
  -H "Authorization: Bearer $TOKEN"
```

| Status | When | Body |
| --- | --- | --- |
| `200 OK` | Success. Returns an empty `data` array if the caller has no addresses. | Paginated list of Address objects |
| `422 Unprocessable Content` | `page` or `limit` is out of range or not an integer | Validation error list |

```json
{
  "total_records": 2,
  "current_page": 1,
  "limit": 20,
  "data": [
    {
      "title": "Home", "street_address": "1 Rizal Ave", "city": "Manila", "state": "Metro Manila",
      "postal_code": "1000", "country": "Philippines", "latitude": 14.5995, "longitude": 120.9842,
      "id": 1, "account_id": 1, "created_at": "2026-10-02T13:45:39", "updated_at": "2026-10-02T13:45:39"
    },
    {
      "title": "Office", "street_address": "5 EDSA", "city": "Quezon City", "state": "Metro Manila",
      "postal_code": "1100", "country": "Philippines", "latitude": 14.676, "longitude": 121.0437,
      "id": 2, "account_id": 1, "created_at": "2026-10-02T13:45:39", "updated_at": "2026-10-02T13:45:39"
    }
  ]
}
```

#### `GET /api/v1/address/{address_id}`

Returns a single address owned by the caller.

**Auth:** Bearer, owner only.

| Path param | Type | Description |
| --- | --- | --- |
| `address_id` | int | ID of the address |

```bash
curl http://127.0.0.1:8000/api/v1/address/1 \
  -H "Authorization: Bearer $TOKEN"
```

| Status | When | Body |
| --- | --- | --- |
| `200 OK` | Found and owned by the caller | Address |
| `403 Forbidden` | Owned by another account | `{"detail": "You are not authorized to view this address entry profile record."}` |
| `404 Not Found` | No address with that ID | `{"detail": "Address entry with ID 999 was not found."}` |
| `422 Unprocessable Content` | `address_id` is not an integer | Validation error list |

#### `POST /api/v1/address/`

Creates an address for the caller. Latitude and longitude are always geocoded from the text fields and cannot be supplied here. Use `PUT` or `PATCH` afterward to override them. The response does not include the new ID. Fetch it from `GET /address/my-list`.

**Auth:** Bearer. **Body:** form data (`application/x-www-form-urlencoded` or `multipart/form-data`). JSON is rejected with `422`.

| Field | Type | Required | Constraints |
| --- | --- | --- | --- |
| `title` | string | No | 1–100 chars, default `Home` |
| `street_address` | string | Yes | 1–255 chars |
| `city` | string | Yes | 1–100 chars |
| `state` | string | Yes | 1–100 chars |
| `postal_code` | string | Yes | 1–20 chars |
| `country` | string | Yes | 1–100 chars |

```bash
curl -X POST http://127.0.0.1:8000/api/v1/address/ \
  -H "Authorization: Bearer $TOKEN" \
  -d "title=Home" -d "street_address=1 Rizal Ave" -d "city=Manila" \
  -d "state=Metro Manila" -d "postal_code=1000" -d "country=Philippines"
```

| Status | When | Body |
| --- | --- | --- |
| `201 Created` | Address geocoded and saved | `{"message": "Address created successfully"}` |
| `400 Bad Request` | The address could not be geocoded | See *Geocoding* above |
| `502 Bad Gateway` | Nominatim was unavailable | See *Geocoding* above |
| `422 Unprocessable Content` | A required field is missing or too long, or the body is JSON | Validation error list |

#### `PUT /api/v1/address/{address_id}`

Replaces every field of an address owned by the caller.

**Auth:** Bearer, owner only. **Body:** form data (`application/x-www-form-urlencoded` or `multipart/form-data`).

| Path param | Type | Description |
| --- | --- | --- |
| `address_id` | int | ID of the address |

| Field | Type | Required | Constraints |
| --- | --- | --- | --- |
| `title` | string | Yes | 1–100 chars |
| `street_address` | string | Yes | 1–255 chars |
| `city` | string | Yes | 1–100 chars |
| `state` | string | Yes | 1–100 chars |
| `postal_code` | string | Yes | 1–20 chars |
| `country` | string | Yes | 1–100 chars |
| `latitude` | float | No | -90 to 90. Leave blank to geocode. |
| `longitude` | float | No | -180 to 180. Leave blank to geocode. |

How coordinates are set: if **both** `latitude` and `longitude` are sent, they are stored as given. If **either** is blank or omitted, both are geocoded from the text fields, and a lone latitude or longitude is discarded.

```bash
curl -X PUT http://127.0.0.1:8000/api/v1/address/1 \
  -H "Authorization: Bearer $TOKEN" \
  -d "title=Home" -d "street_address=2 Rizal Ave" -d "city=Manila" \
  -d "state=Metro Manila" -d "postal_code=1000" -d "country=Philippines" \
  -d "latitude=14.6" -d "longitude=120.99"
```

| Status | When | Body |
| --- | --- | --- |
| `200 OK` | Updated | The updated Address |
| `400 Bad Request` | Geocoding was needed and found no match | See *Geocoding* above |
| `403 Forbidden` | Owned by another account | `{"detail": "You are not authorized to update this address entry."}` |
| `404 Not Found` | No address with that ID | `{"detail": "Address entry not found."}` |
| `422 Unprocessable Content` | A required field is missing, blank, or too long, a coordinate is out of range or not a number, or the body is JSON. Nothing is saved. | Validation error list |
| `502 Bad Gateway` | Geocoding was needed and Nominatim was unavailable | See *Geocoding* above |

#### `PATCH /api/v1/address/{address_id}`

Updates only the fields included in the body.

**Auth:** Bearer, owner only. **Body:** `application/json`. Form data is rejected with `422`.

| Path param | Type | Description |
| --- | --- | --- |
| `address_id` | int | ID of the address |

Every field is optional. A field sent as `null` or `""` counts as not sent, and its current value is kept. Every column is required, so a PATCH can't clear one.

> In Swagger UI the example body lists every field with placeholder values (`"string"`, `0`). Remove the fields you aren't changing before you click **Execute**.

| Field | Type | Constraints |
| --- | --- | --- |
| `title` | string | 1–100 chars |
| `street_address` | string | 1–255 chars |
| `city` | string | 1–100 chars |
| `state` | string | 1–100 chars |
| `postal_code` | string | 1–20 chars |
| `country` | string | 1–100 chars |
| `latitude` | float | -90 to 90 |
| `longitude` | float | -180 to 180 |

How coordinates are set:

1. If the body contains `latitude` and/or `longitude`, those values are stored. A coordinate that isn't sent keeps its current value, and no geocoding happens even if location text also changed.
2. Otherwise, if any of `street_address`, `city`, `state`, `postal_code`, or `country` is sent, the coordinates are geocoded from the merged (new and existing) location fields.
3. Otherwise, for example when only `title` is sent, the coordinates are unchanged.

```bash
curl -X PATCH http://127.0.0.1:8000/api/v1/address/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"city": "Quezon City"}'
```

| Status | When | Body |
| --- | --- | --- |
| `200 OK` | Updated | The updated Address |
| `400 Bad Request` | Geocoding was needed and found no match | See *Geocoding* above |
| `403 Forbidden` | Owned by another account | `{"detail": "You are not authorized to update this address entry."}` |
| `404 Not Found` | No address with that ID | `{"detail": "Address entry with ID 1 was not found."}` |
| `422 Unprocessable Content` | A value breaks a constraint (e.g. `latitude: 200`), or the body is not JSON | Validation error list |
| `502 Bad Gateway` | Geocoding was needed and Nominatim was unavailable | See *Geocoding* above |

#### `DELETE /api/v1/address/{address_id}`

Permanently deletes an address owned by the caller.

**Auth:** Bearer, owner only.

| Path param | Type | Description |
| --- | --- | --- |
| `address_id` | int | ID of the address |

```bash
curl -X DELETE http://127.0.0.1:8000/api/v1/address/2 \
  -H "Authorization: Bearer $TOKEN"
```

| Status | When | Body |
| --- | --- | --- |
| `200 OK` | Deleted | `{"status": "success", "message": "Address entry with ID 2 has been completely deleted."}` |
| `403 Forbidden` | Owned by another account | `{"detail": "You are not authorized to delete this address entry."}` |
| `404 Not Found` | No address with that ID, or it was already deleted | `{"detail": "Address entry with ID 2 was not found."}` |
| `422 Unprocessable Content` | `address_id` is not an integer | Validation error list |

#### `GET /api/v1/nearby/`

Public search across **all accounts'** addresses. Returns the ones within `radius_km` of a point, nearest first, up to `limit` results. Distance is the geodesic distance. It decides the filtering and order but is not included in the response.

**Auth:** public.

| Query param | Type | Required | Default | Constraints |
| --- | --- | --- | --- | --- |
| `latitude` | float | Yes | n/a | -90 to 90 |
| `longitude` | float | Yes | n/a | -180 to 180 |
| `radius_km` | float | No | `5.0` | > 0 |
| `limit` | int | No | `20` | 1–100 |

```bash
curl "http://127.0.0.1:8000/api/v1/nearby/?latitude=14.6&longitude=121.0&radius_km=20&limit=20"
```

| Status | When | Body |
| --- | --- | --- |
| `200 OK` | Success. Returns `[]` when nothing is in range. | Array of Address objects |
| `422 Unprocessable Content` | `latitude` or `longitude` is missing, or a parameter is out of range | Validation error list |

```json
[
  {
    "title": "Office", "street_address": "5 EDSA", "city": "Quezon City", "state": "Metro Manila",
    "postal_code": "1100", "country": "Philippines", "latitude": 14.676, "longitude": 121.0437,
    "id": 2, "account_id": 1, "created_at": "2026-10-02T13:45:39", "updated_at": "2026-10-02T13:45:39"
  }
]
```
