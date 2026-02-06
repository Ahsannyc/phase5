#!/bin/bash

# Monorepo Bootstrap Script
# Creates the basic folder structure and initializes frontend/backend projects

set -e  # Exit on any error

echo "Bootstrapping Todo App Monorepo..."

# Create directory structure
mkdir -p {frontend,backend}
cd frontend
npm create next-app@latest . --typescript --tailwind --eslint --app --no-src-dir --import-alias "@/*"
cd ../backend
pip install fastapi uvicorn sqlmodel python-multipart python-dotenv

# Create basic .env.example
cat > .env.example << EOF
DATABASE_URL=postgresql://username:password@localhost:5432/todo_db
BETTER_AUTH_SECRET=your-secret-key-here
JWT_SECRET=your-jwt-secret-here
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
EOF

# Create basic backend structure
mkdir -p {models,services,api,routes}
touch backend/__init__.py
touch backend/models/__init__.py
touch backend/services/__init__.py
touch backend/api/__init__.py
touch backend/routes/__init__.py

# Create basic main.py for FastAPI
cat > backend/main.py << EOF
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
EOF

echo "Monorepo bootstrapped successfully!"
echo "Frontend created in ./frontend"
echo "Backend created in ./backend"
echo "Environment variables defined in .env.example"