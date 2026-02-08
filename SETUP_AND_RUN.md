# Setup and Run Guide - Todo AI Chatbot

## Prerequisites
- Python 3.12+
- Node.js 18+
- PostgreSQL (Neon)

## Step 1: Setup Backend

### 1.1 Install Python Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 1.2 Set Environment Variables
Create/update `backend/.env`:
```
DATABASE_URL=postgresql://neondb_owner:npg_GtQsRu0KT3eE@ep-holy-mouse-aj1nsvqk-pooler.c-3.us-east-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
BETTER_AUTH_SECRET=CX7yA3GgjBJkdy5M5WR9nt4SvdCEUOA0
BETTER_AUTH_URL=http://localhost:3000
COHERE_API_KEY=your-cohere-api-key-here
OPENAI_API_KEY=your-openai-api-key-here (optional)
MCP_SERVER_PORT=8001
```

### 1.3 Run Database Migrations
```bash
cd backend
alembic upgrade head
```

### 1.4 Start Backend Server
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`

## Step 2: Setup Frontend

### 2.1 Install Frontend Dependencies
```bash
cd frontend
npm install
```

### 2.2 Set Environment Variables
Update `frontend/.env`:
```
BETTER_AUTH_SECRET=cpa1WXHeZgrAidWXxiSQxiuK53MmSeaT
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000
```

### 2.3 Start Frontend Server
```bash
cd frontend
npm run dev
```

Frontend will be available at: `http://localhost:3000`

## Step 3: Test the Chat Functionality

### Via Frontend
1. Go to http://localhost:3000
2. Sign in with your credentials
3. Look for the floating chat button 💬 in the bottom right
4. Click to open and try these commands:
   - "Add task buy groceries"
   - "Show my tasks"
   - "Mark task 1 done"
   - "List all tasks"

### Via API (curl)
```bash
# First, get a JWT token by signing in
# Then use it in your requests:

curl -X POST http://localhost:8000/api/chat/send \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Add task buy milk",
    "conversation_id": null
  }'
```

## Troubleshooting

### Issue: COHERE_API_KEY not set
**Solution**: Get an API key from https://cohere.com/api and add it to `.env`

### Issue: Database connection failed
**Solution**: Verify DATABASE_URL in `.env` and ensure Neon is accessible

### Issue: Chat not responding
**Solution**: Check backend logs, ensure migrations ran successfully

### Issue: Frontend can't reach backend
**Solution**: Verify NEXT_PUBLIC_BACKEND_URL is set correctly in frontend/.env

## Supported Chat Commands

| Command | Example | What It Does |
|---------|---------|--------------|
| Add Task | "Add task buy groceries" | Creates a new task |
| List Tasks | "Show my tasks" | Lists all your tasks |
| Mark Done | "Mark task 1 done" | Marks task as complete |
| Update Task | "Update task 2 to buy milk" | Changes task title |
| Delete Task | "Delete task 3" | Removes a task |

## API Endpoints

- `POST /api/chat/send` - Send message and get AI response
- `GET /api/chat/conversations` - List all conversations
- `GET /api/chat/conversations/{id}/messages` - Get messages in a conversation

All endpoints require JWT authentication via `Authorization: Bearer` header.

## Architecture

**Backend**:
- FastAPI with SQLModel
- Async database operations
- MCP tools for task management
- Cohere LLM for NLP
- Conversation/Message persistence

**Frontend**:
- Next.js 16+ with TypeScript
- OpenAI ChatKit UI component
- Glassmorphism + neon styling
- Session-based authentication

**Database**:
- Neon PostgreSQL
- Conversations and Messages tables
- User isolation via user_id

