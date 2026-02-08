# Quickstart Guide: Todo AI Chatbot

## Overview
This guide provides step-by-step instructions for setting up and running the Todo AI Chatbot application locally.

## Prerequisites

- Python 3.12 or higher
- Node.js 18 or higher
- PostgreSQL (or access to Neon PostgreSQL account)
- Cohere API key
- OpenAI API key (for Agents SDK)

## Environment Setup

### Backend Environment Variables

Create a `.env` file in the `backend/` directory:

```env
DATABASE_URL="postgresql://username:password@localhost:5432/todo_db"
COHERE_API_KEY="your-cohere-api-key"
OPENAI_API_KEY="your-openai-api-key"
BETTER_AUTH_SECRET="your-secret-key-for-jwt"
BETTER_AUTH_URL="http://localhost:3000"
NEON_DATABASE_URL="your-neon-database-url"
```

### Frontend Environment Variables

Create a `.env.local` file in the `frontend/` directory:

```env
NEXT_PUBLIC_BACKEND_URL="http://localhost:8000"
NEXT_PUBLIC_COHERE_API_KEY="your-cohere-api-key"
NEXT_PUBLIC_OPENAI_DOMAIN_KEY="your-nextjs-domain-for-chatkit"
```

## Installation Steps

### 1. Clone and Navigate to Project

```bash
git clone <your-repository-url>
cd phase3
```

### 2. Backend Setup

Navigate to the backend directory:

```bash
cd backend
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### 3. Database Setup

Set up your PostgreSQL database (local or Neon):

```bash
# Run database migrations
alembic upgrade head
```

### 4. Frontend Setup

Navigate to the frontend directory:

```bash
cd ../frontend
```

Install Node.js dependencies:

```bash
npm install
```

## Running the Application

### 1. Start the Backend

From the `backend/` directory:

```bash
# Start the FastAPI server
uvicorn app.main:app --reload --port 8000
```

### 2. Start the MCP Server

From the `backend/` directory in a separate terminal:

```bash
# Start the MCP server
python -m mcp.server
```

### 3. Start the Frontend

From the `frontend/` directory in a separate terminal:

```bash
# Start the Next.js development server
npm run dev
```

The application will be accessible at `http://localhost:3000`

## API Usage Examples

### Using the Chat Endpoint

```bash
curl -X POST http://localhost:8000/api/1/chat \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your-jwt-token>" \
  -d '{
    "message": "Add a task to buy groceries"
  }'
```

### Using the Conversations Endpoint

```bash
curl -X GET http://localhost:8000/api/1/conversations \
  -H "Authorization: Bearer <your-jwt-token>"
```

## Testing the AI Chatbot

1. Navigate to the application at `http://localhost:3000`
2. Sign in with your credentials
3. Look for the floating chat icon (cyan glow) in the bottom-right corner
4. Click the chat icon to open the chat interface
5. Try these sample commands:
   - "Add a task to call mom"
   - "Show my tasks"
   - "Mark task 1 as complete"
   - "Delete task 2"

## Troubleshooting

### Common Issues

**Issue**: Database connection errors
**Solution**: Verify your DATABASE_URL is correct and the database is running

**Issue**: Authentication failures
**Solution**: Ensure your JWT token is valid and the secret matches between frontend and backend

**Issue**: AI responses are slow or failing
**Solution**: Check that your Cohere API key is valid and has sufficient quota

**Issue**: Chat interface not appearing
**Solution**: Verify that the chat feature is enabled and properly configured in the frontend

## Development Commands

### Backend Development
```bash
# Run tests
pytest

# Format code
black .

# Check types
mypy .
```

### Frontend Development
```bash
# Run tests
npm test

# Format code
npm run format

# Lint code
npm run lint
```

## Deployment

For production deployment, ensure:

1. Environment variables are properly set
2. SSL certificates are configured for HTTPS
3. Database connections are optimized
4. API keys are securely managed
5. Proper load balancing is in place