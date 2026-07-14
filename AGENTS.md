# AppifyLab Backend Notes

## Requirement Summary

- Build backend support for the provided Login, Register, and Feed UI.
- Use secure JWT authentication for register/login and protected feed access.
- Registration fields: first name, last name, email, password.
- Feed is protected and shows public posts from everyone plus the current user's private posts.
- Posts must support text, optional image, newest-first ordering, and public/private visibility.
- Implement comments, replies, like/unlike state, and show who liked posts, comments, and replies.

## Backend Implementation

- FastAPI with PostgreSQL, SQLAlchemy, Alembic, and JWT bearer auth.
- Core routes are under `/api/v1`.
- `POST /api/v1/auth/register` creates users.
- `POST /api/v1/auth/login` returns a bearer token.
- `GET /api/v1/users/me` returns the current authenticated user.
- `GET /api/v1/posts` returns the protected feed, newest first.
- `POST /api/v1/posts` creates a post from JSON or multipart form data.
- `GET /api/v1/posts/{post_id}` returns one visible post.
- `PATCH /api/v1/posts/{post_id}` updates only the author's post.
- `DELETE /api/v1/posts/{post_id}` deletes only the author's post.
- `POST /api/v1/posts/{post_id}/comments` adds a comment.
- `POST /api/v1/comments/{comment_id}/replies` adds a reply.
- `POST /api/v1/likes/{target_type}/{target_id}/toggle` toggles likes for `post`, `comment`, or `reply`.

## Data Model Notes

- `users` stores auth profile data.
- `posts` stores content, optional `image_url`, author, visibility, and timestamps.
- `comments` is an adjacency-list table; top-level comments have `parent_id = NULL`, replies have a parent.
- `likes` uses `target_type` plus `target_id` so posts, comments, and replies share one like system.
- Important lookup indexes were added for feed reads, comment loading, and like-state queries.
