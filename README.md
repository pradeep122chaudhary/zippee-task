# Task Manager REST API (Django REST Framework - APIView Only)

Production-ready Task Manager API built with Django REST Framework using `APIView

## Project Overview

This project provides secure JWT-based authentication and task management endpoints with role-based access control, pagination, filtering, search, OpenAPI schema generation, and unit tests.

## Features

- `APIView`-only implementation for all custom endpoints
- URI-based API versioning under `/api/v1/`
- JWT authentication using `djangorestframework-simplejwt`
- User registration and login endpoints
- Role-based access control (`IsOwnerOrAdmin`)
- Task CRUD with ownership enforcement
- Pagination (`PageNumberPagination`, page size `10`)
- Filtering by `completed` and search by `title`
- OpenAPI/Swagger documentation via `drf-spectacular`
- Comprehensive APITestCase suite
- PostgreSQL-ready configuration (SQLite fallback for development)

## Tech Stack

- Python 3.10+
- Django 4+ (tested with Django 5.x)
- Django REST Framework
- SimpleJWT
- drf-spectacular
- django-filter
- PostgreSQL (optional), SQLite (default development)

## Project Structure

```text
task_manager/
├── apps/
│   ├── tasks/
│   │   ├── filters.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── permissions.py
│   │   ├── serializers.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   └── users/
│       ├── migrations/
│       ├── models.py
│       ├── serializers.py
│       ├── tests.py
│       ├── urls.py
│       └── views.py
├── config/
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── manage.py
├── requirements.txt
└── README.md
```

## Installation

1. Clone and move into the project directory:

```bash
cd task_manager
```

2. Create a virtual environment:

```bash
python -m venv .venv
```

3. Activate the virtual environment:

- Windows (PowerShell):

```powershell
.venv\Scripts\Activate.ps1
```

- Linux/macOS:

```bash
source .venv/bin/activate
```

4. Install dependencies:

```bash
pip install -r requirements.txt
```

## Environment Variables

Optional variables for production-like setup:

- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG` (`True`/`False`)
- `DJANGO_ALLOWED_HOSTS` (comma-separated)
- `POSTGRES_DB`
- `POSTGRES_USER`
- `POSTGRES_PASSWORD`
- `POSTGRES_HOST`
- `POSTGRES_PORT`
- `JWT_ACCESS_MINUTES`
- `JWT_REFRESH_DAYS`

If PostgreSQL variables are not set, SQLite is used automatically.

## Database Setup

Run migrations:

```bash
python manage.py migrate
```

Create a superuser (optional):

```bash
python manage.py createsuperuser
```

## Run the Server

```bash
python manage.py runserver
```

Server starts at `http://127.0.0.1:8000/`.

## Authentication Endpoints

- `POST /api/v1/auth/register/`
- `POST /api/v1/auth/login/` (email + password)
- `GET /api/v1/auth/users/` (regular user: own data, admin/super admin: all users)
- `POST /api/v1/token/`
- `POST /api/v1/token/refresh/`

## Task Endpoints

- `GET /api/v1/tasks/`
- `POST /api/v1/tasks/`
- `GET /api/v1/tasks/{id}/`
- `PUT /api/v1/tasks/{id}/`
- `DELETE /api/v1/tasks/{id}/`

## JWT Usage Example

After login, include access token in headers:

```http
Authorization: Bearer <access_token>
```

## Swagger / OpenAPI

- Schema: `http://127.0.0.1:8000/api/v1/schema/`
- Swagger UI: `http://127.0.0.1:8000/api/v1/docs/`

## Example cURL Requests

Register:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"john@example.com\",\"first_name\":\"John\",\"last_name\":\"Doe\",\"password\":\"StrongPass123!\",\"password_confirm\":\"StrongPass123!\"}"
```

Login:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"john@example.com\",\"password\":\"StrongPass123!\"}"
```

Create task:

```bash
curl -X POST http://127.0.0.1:8000/api/v1/tasks/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <access_token>" \
  -d "{\"title\":\"Finish assignment\",\"description\":\"Complete by Friday\",\"completed\":false}"
```

Filter tasks:

```bash
curl "http://127.0.0.1:8000/api/v1/tasks/?completed=true" \
  -H "Authorization: Bearer <access_token>"
```

Search tasks:

```bash
curl "http://127.0.0.1:8000/api/v1/tasks/?search=finish" \
  -H "Authorization: Bearer <access_token>"
```

## Running Tests

```bash
python manage.py test
```

## Permission Model

- Regular users can view and manage only their own tasks.
- `admin` and `super_admin` user types can access and manage all tasks and user data.
- `admin` and `super_admin` can get, update, and delete any user's task.

## HTTP Status Codes Used

- `200 OK`
- `201 Created`
- `204 No Content`
- `400 Bad Request`
- `401 Unauthorized`
- `403 Forbidden`
- `404 Not Found`
