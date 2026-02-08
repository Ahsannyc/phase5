# Contributing to Todo App

Welcome! We're excited that you're interested in contributing. This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Give credit where credit is due
- Report issues responsibly
- Follow project guidelines

## Getting Started

### 1. Fork & Clone

```bash
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/your-username/todo-app.git
cd todo-app
```

### 2. Set Up Development Environment

```bash
# Create feature branch
git checkout -b feature/your-feature-name

# Setup (see LOCAL_DEVELOPMENT.md for details)
make setup
```

### 3. Make Changes

```bash
# Create or modify files
# Follow code style guidelines (see below)

# Run tests to ensure nothing breaks
make test

# Format code
make format

# Lint code
make lint
```

## Development Workflow

### Branch Naming Conventions

```
feature/feature-name          # New features
bugfix/bug-description        # Bug fixes
docs/documentation-update     # Documentation
refactor/refactoring-task     # Refactoring
test/test-case-name           # Tests
chore/maintenance-task        # Maintenance
```

### Commit Message Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types**:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `style`: Code style changes
- `chore`: Build/dependency changes

**Example**:
```
feat(chat): add natural language intent parsing

Implement intent parsing for chat messages to automatically
determine if user wants to add, list, or complete a task.

Closes #42
```

### Commit Checklist

- [ ] Code follows project style guide
- [ ] Tests pass: `make test`
- [ ] No linting errors: `make lint`
- [ ] Code is formatted: `make format`
- [ ] Changes documented in docstrings
- [ ] No console.log/print statements left in code
- [ ] Security checks pass: `make security-check`

## Code Style Guide

### Python (Backend)

```python
# Follow PEP 8 + Black formatter
# Type hints required for public functions

from typing import Optional
from sqlmodel import Session

def create_task(
    db: Session,
    user_id: int,
    title: str,
    description: Optional[str] = None
) -> Task:
    """Create a new task for user.

    Args:
        db: Database session
        user_id: User ID
        title: Task title
        description: Optional description

    Returns:
        Created Task object

    Raises:
        ValueError: If title is empty
    """
    if not title.strip():
        raise ValueError("Title cannot be empty")

    task = Task(
        user_id=user_id,
        title=title.strip(),
        description=description
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task
```

**Rules**:
- Use `black` for formatting: `black app/`
- Use `isort` for imports: `isort app/`
- Type hints for all public functions
- Docstrings for classes and public methods
- Max line length: 88 characters
- Use async/await for I/O operations

### JavaScript/TypeScript (Frontend)

```typescript
// Use Prettier for formatting
// Type hints required

interface Task {
  id: number;
  title: string;
  description?: string;
  completed: boolean;
}

export function TaskList({ tasks }: { tasks: Task[] }): JSX.Element {
  return (
    <ul>
      {tasks.map((task) => (
        <li key={task.id} className="task-item">
          <input type="checkbox" checked={task.completed} />
          <span>{task.title}</span>
        </li>
      ))}
    </ul>
  );
}
```

**Rules**:
- Use Prettier for formatting: `pnpm format`
- Use ESLint: `pnpm lint`
- Type all component props
- Export interfaces for prop types
- Max line length: 80 characters
- Use functional components + hooks
- Avoid prop drilling (use Context API)

## Testing Requirements

### Backend Tests

```python
# pytest

def test_create_task(db: Session, user: User):
    """Test task creation."""
    title = "Buy groceries"
    task = create_task(db, user.id, title)

    assert task.id is not None
    assert task.title == title
    assert task.completed == False
    assert task.user_id == user.id
```

**Requirements**:
- All new features must have tests
- Minimum 80% code coverage
- Tests in `tests/` directory parallel to `app/`
- Run tests: `make test`
- Run with coverage: `pytest --cov=app`

### Frontend Tests

```typescript
// Jest + React Testing Library

describe('TaskList', () => {
  it('renders tasks', () => {
    const tasks: Task[] = [
      { id: 1, title: 'Task 1', completed: false }
    ];

    const { getByText } = render(<TaskList tasks={tasks} />);
    expect(getByText('Task 1')).toBeInTheDocument();
  });
});
```

**Requirements**:
- Unit tests for utilities and hooks
- Component tests for UI components
- Run tests: `pnpm test`
- Coverage target: 70%+

## Pull Request Process

### Before Creating PR

1. Update your branch with latest main:
   ```bash
   git fetch origin
   git rebase origin/main
   ```

2. Run tests locally:
   ```bash
   make ci-local
   ```

3. Create a clear commit history:
   ```bash
   git log origin/main..HEAD
   ```

### Create Pull Request

1. Push your branch:
   ```bash
   git push origin feature/your-feature
   ```

2. Open PR on GitHub with:
   - Clear title: `feat: add chat intent parsing`
   - Description of changes
   - Closes #issue-number (if applicable)
   - Screenshots/videos for UI changes

3. Link related issues:
   ```markdown
   ## Description
   This PR adds natural language intent parsing to the chat interface.

   ## Changes
   - Added `parse_intent()` function
   - Added tests for intent parsing
   - Updated API documentation

   ## Testing
   - All tests pass
   - Coverage: 92%

   ## Closes #42
   ```

### PR Review Process

- At least 1 approval required
- All CI checks must pass
- Code review comments addressed
- Optional: Author responds to feedback

## Documentation

### Docstrings

```python
def create_task(db: Session, user_id: int, title: str) -> Task:
    """Create a new task for a user.

    This function creates a task and stores it in the database
    after validating the input.

    Args:
        db: Database session for persistence
        user_id: ID of the user creating the task
        title: Task title (required, must be non-empty)

    Returns:
        The created Task object with generated ID

    Raises:
        ValueError: If title is empty or whitespace only
        sqlalchemy.exc.IntegrityError: If user_id doesn't exist

    Example:
        >>> task = create_task(db, user_id=1, title="Buy milk")
        >>> print(task.id)
        1
    """
```

### README Updates

If your change affects usage:
1. Update README.md with clear examples
2. Add section to API_DOCUMENTATION.md if adding endpoints
3. Update LOCAL_DEVELOPMENT.md if changing setup process

### Architecture Changes

For significant architectural changes:
1. Propose design in GitHub Discussion first
2. Update ARCHITECTURE.md with diagrams
3. Document decision in comment and commit message

## Security & Best Practices

### Never Commit

❌ Secrets, API keys, passwords
❌ Environment files (.env)
❌ Credentials or tokens
❌ Sensitive data

### Always

✅ Use `.env.example` for configuration
✅ Validate user input
✅ Sanitize data before storing/displaying
✅ Use parameterized queries (SQLModel handles this)
✅ HTTPS for external API calls
✅ Proper error handling (no stack traces to users)

## Performance

- Don't block main thread with long-running tasks
- Use async/await for I/O operations
- Optimize database queries (use indexes)
- Cache when appropriate
- Profile before optimizing

## Accessibility

- Add alt text to images
- Use semantic HTML
- Ensure keyboard navigation
- Test with screen readers
- Follow WCAG 2.1 guidelines

## Local Testing Before PR

```bash
# Run full CI pipeline
make ci-local

# Or individually:
make lint          # Code style
make test          # Tests
make build         # Build artifacts
```

## Common Tasks

### Add New API Endpoint

1. Create route in `backend/app/api/`
2. Add schema in `backend/app/schemas/`
3. Add CRUD in `backend/app/crud/`
4. Write tests in `backend/tests/`
5. Update API_DOCUMENTATION.md

### Add New Frontend Component

1. Create component in `frontend/app/components/`
2. Write tests in `frontend/__tests__/`
3. Add stories in `.stories.tsx` for Storybook
4. Update documentation

### Add Database Table

1. Create model in `backend/app/models/`
2. Create alembic migration
3. Add CRUD operations
4. Add tests
5. Update schema

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue with reproduction steps
- **Ideas**: Start a GitHub Discussion

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Thanked in release notes
- Credited in commit history

---

## Legal

By contributing, you agree that:
- Your contributions are your own work
- You grant the project a license to use your work
- Your work doesn't violate anyone else's rights

---

Thank you for contributing! 🎉

