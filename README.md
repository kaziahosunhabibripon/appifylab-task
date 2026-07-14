# AppifyLab Backend Task

A FastAPI backend for the AppifyLab social feed task. It provides JWT authentication, protected feed access, PostgreSQL persistence, comments, replies, likes, post visibility, and optional Cloudinary-backed image uploads.

## Features

- User registration with first name, last name, email, and password
- JWT login and protected feed access
- Public/private post visibility
- Text posts, image posts, and text-with-image posts
- Cloudinary image upload with local upload fallback
- Newest-first feed ordering
- Like/unlike support for posts, comments, and replies
- Liked-by user lists
- Comments and nested replies
- REST API routes grouped under `/api/v1`

## Tech Stack

- FastAPI
- PostgreSQL
- SQLAlchemy
- Alembic
- Pydantic
- JWT bearer authentication
- Cloudinary

## Project Structure

```text
.
├── app/
│   ├── models/
│   ├── routers/
│   ├── schemas/
│   ├── services/
│   └── utils/
├── alembic/
├── .env.example
├── alembic.ini
├── requirements.txt
└── README.md
```

## Prerequisites

- Python 3.12+
- PostgreSQL
- Cloudinary account for hosted image uploads, optional

## Environment Setup

Create backend environment file:

```bash
cp .env.example .env.local
```

Update `.env.local`:

```env
DATABASE_URL=postgresql://postgres:password@localhost:5432/appifylab
SECRET_KEY=replace-with-a-secure-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

## Run Locally

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Backend runs at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

Quick health check:

```bash
curl http://localhost:8000/
```

Expected response:

```json
{
  "message": "Backend Running Successfully 🚀"
}
```

### Backend Notes

- Backend settings load from `.env.local` by default. Set `ENV_FILE` if another env file is needed.
- All protected endpoints require an `Authorization: Bearer <token>` header from `/api/v1/auth/login`.
- Run `alembic upgrade head` before starting the API so the users, posts, comments, and likes tables exist.
- Post creation accepts JSON with `content`, `visibility`, and optional `image_url`.
- Post creation also accepts `multipart/form-data` with `content`, `visibility`, and optional `image`; uploaded files are served from `/uploads` when Cloudinary credentials are not configured.

## Useful Commands

Backend syntax check:

```bash
venv/bin/python -m compileall app
```

## Deployment

This repository includes `render.yaml` for a Render Blueprint deployment.

1. Push the repository to GitHub.
2. Open Render and choose **New +** -> **Blueprint**.
3. Connect this repository.
4. Render will create:
   - `appifylab-social-api`
   - `appifylab-social-db`
5. Add the Cloudinary environment variables in the Render service:

```env
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

The backend start command runs database migrations before starting the API:

```bash
alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

After deployment, the API base URL will look like:

```text
https://your-render-service.onrender.com/api/v1
```

## API Overview

All backend routes are prefixed with `/api/v1`.

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | Login and receive a bearer token |
| `GET` | `/users/me` | Get authenticated user |
| `GET` | `/posts` | Get protected feed |
| `POST` | `/posts` | Create post with JSON or multipart form data |
| `GET` | `/posts/{post_id}` | Get one visible post |
| `PATCH` | `/posts/{post_id}` | Update own post |
| `DELETE` | `/posts/{post_id}` | Delete own post |
| `POST` | `/posts/{post_id}/comments` | Add comment |
| `POST` | `/comments/{comment_id}/replies` | Add reply |
| `POST` | `/likes/{target_type}/{target_id}/toggle` | Toggle like for post, comment, or reply |

## Data Model

- `users`: stores account profile and authentication data
- `posts`: stores content, image URL, visibility, owner, and timestamps
- `comments`: stores comments and replies using an adjacency-list parent relationship
- `likes`: stores one reusable like system for posts, comments, and replies

The feed query returns public posts from all users and private posts owned by the authenticated user.

## Implementation Notes

- Passwords are hashed before storage.
- Protected routes require a JWT bearer token.
- Post visibility supports `public` and `private`.
- Image upload supports Cloudinary when configured and falls back to local `/uploads`.
- Image-only posts are supported, while fully empty posts are rejected.
- JWT access tokens are returned from login and must be sent as bearer tokens for protected routes.

## Deliverables

- GitHub repository: `https://github.com/kaziahosunhabibripon/appifylab-task`
- Live deployment: add the Render URL here if deployed
