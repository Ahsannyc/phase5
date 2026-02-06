# Quickstart Guide: FastAPI Backend Implementation

## Overview
This guide provides step-by-step instructions to set up, develop, and deploy the FastAPI + SQLModel + Neon PostgreSQL backend application. Follow these instructions to get the application running locally and understand the development workflow.

## Prerequisites

Before starting, ensure you have the following installed:

- Python 3.9 or higher
- pip (Python package manager)
- Git
- A code editor (VS Code recommended)
- Access to a Neon PostgreSQL database

## Initial Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd todo-phase2/backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the backend directory with the following variables:

```env
DATABASE_URL=postgresql://username:password@host:port/database_name
BETTER_AUTH_SECRET=your-secret-key-here
BETTER_AUTH_URL=http://localhost:3000
```

## Development

### 1. Running the Development Server
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

### 2. Database Migrations
```bash
# Create a new migration
alembic revision --autogenerate -m "description of changes"

# Apply migrations
alembic upgrade head

# Downgrade migrations
alembic downgrade -1
```

### 3. Development Commands

- `uvicorn app.main:app --reload` - Start development server with hot reloading
- `pytest` - Run unit tests
- `black .` - Format Python code
- `flake8 .` - Lint Python code
- `mypy .` - Type check Python code
- `alembic upgrade head` - Apply all pending migrations

### 4. Folder Structure for Development

Understanding the key folders and files:

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py             # Database session and user dependencies
│   │   ├── auth.py             # Authentication routes
│   │   └── tasks.py            # Task management routes
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Settings and configuration
│   │   └── security.py         # JWT and authentication logic
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py             # User SQLModel definition
│   │   └── task.py             # Task SQLModel definition
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py             # User Pydantic schemas
│   │   └── task.py             # Task Pydantic schemas
│   ├── crud/
│   │   ├── __init__.py
│   │   ├── user.py             # User CRUD operations
│   │   └── task.py             # Task CRUD operations
│   └── database.py             # Database engine and session setup
├── alembic/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/               # Migration files
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_auth.py
│   └── test_tasks.py
└── requirements.txt
```

## Key Development Concepts

### 1. Async Programming
- All database operations should be async
- Use `async def` for route handlers
- Use `await` when calling database operations

### 2. Dependency Injection
- Use FastAPI's `Depends()` for injecting dependencies
- Common dependencies: database session, current user
- Dependencies help with authentication and resource management

### 3. SQLModel Usage
- Define models that inherit from `SQLModel` and `table=True`
- Use Pydantic validation with field types
- Combine SQLAlchemy functionality with Pydantic serialization

### 4. JWT Authentication
- Tokens are created and verified using PyJWT
- Middleware extracts user info from tokens
- All protected routes validate tokens and user ownership

## Building for Production

### 1. Install Production Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Production Server
```bash
uvicorn app.main:app --workers 4 --host 0.0.0.0 --port 8000
```

## Environment Variables

Required environment variables for different environments:

### Development
```env
DATABASE_URL=postgresql://localhost:5432/todo_dev
BETTER_AUTH_SECRET=dev-secret-key-change-before-production
BETTER_AUTH_URL=http://localhost:3000
```

### Production
```env
DATABASE_URL=postgresql://production-neon-db-url
BETTER_AUTH_SECRET=production-secret-key
BETTER_AUTH_URL=https://your-frontend-domain.com
```

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Verify that your DATABASE_URL is correctly formatted
   - Check that Neon PostgreSQL is accessible from your environment
   - Ensure required database drivers are installed (asyncpg)

2. **JWT Authentication Failing**
   - Verify that BETTER_AUTH_SECRET matches between frontend and backend
   - Check that token format is correct in requests
   - Ensure tokens are not expired

3. **Migration Issues**
   - Run `alembic upgrade head` to ensure all migrations are applied
   - Check that your database models match your migration files

4. **Dependency Installation Issues**
   - Ensure you're using the correct Python version (3.9+)
   - Use virtual environment to avoid conflicts
   - Verify internet access for package downloads

### Development Tips

- Use the VS Code Python extension for debugging
- Enable linting and type checking during development
- Test authentication flows with tools like Postman or curl
- Check server logs for detailed error information

## API Testing

### Testing Authentication
```bash
# Sign up a new user
curl -X POST "http://localhost:8000/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123", "name": "Test User"}'

# Sign in to get a token
curl -X POST "http://localhost:8000/api/auth/signin" \
  -H "Content-Type: application/json" \
  -d '{"email": "test@example.com", "password": "password123"}'
```

### Testing Task Operations
```bash
# Create a task (using token from signin)
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"title": "My First Task", "description": "A sample task"}'
```

## Next Steps

After completing the setup:

1. Run database migrations: `alembic upgrade head`
2. Start the development server: `uvicorn app.main:app --reload`
3. Test authentication endpoints
4. Create a test user account
5. Test task management features
6. Review and modify the models as needed
7. Add additional validation or business logic as required