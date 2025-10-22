# ArchMesh TDD Implementation Guide

## Quick Start Guide

### 1. Setting Up TDD Environment

#### Backend Setup
```bash
# Activate virtual environment
cd archmesh-poc/backend
source venv/bin/activate

# Install development dependencies
pip install -e ".[dev]"

# Run tests with coverage
pytest --cov=app --cov-report=html --cov-fail-under=90
```

#### Frontend Setup
```bash
# Install dependencies
cd archmesh-poc/frontend
npm install

# Run tests
npm test

# Run tests with coverage
npm run test:coverage
```

### 2. Using the TDD Runner

#### Basic TDD Cycle
```bash
# Run complete TDD cycle for a new feature
python scripts/tdd-runner.py unit --tdd-cycle --feature "user-authentication"

# Run specific test type
python scripts/tdd-runner.py integration --verbose

# Run all tests
python scripts/tdd-runner.py all
```

#### Create Test Templates
```bash
# Create backend unit test template
python scripts/create-test-template.py create \
  --template backend_unit \
  --output tests/unit/test_user_service.py \
  --class-name UserService \
  --method-name create_user

# Create frontend component test template
python scripts/create-test-template.py create \
  --template frontend_unit \
  --output __tests__/components/UserProfile.test.tsx \
  --component-name UserProfile
```

## Practical TDD Examples

### Example 1: Adding User Authentication

#### Step 1: RED - Write Failing Test
```python
# tests/unit/test_auth_service.py
import pytest
from app.services.auth_service import AuthService
from app.models.user import User

class TestAuthService:
    def test_authenticate_user_success(self):
        """Test successful user authentication"""
        auth_service = AuthService()
        user_data = {
            "email": "test@example.com",
            "password": "secure_password"
        }
        
        result = auth_service.authenticate_user(user_data)
        
        assert result["success"] is True
        assert "access_token" in result["data"]
        assert "refresh_token" in result["data"]
        assert result["data"]["user"]["email"] == user_data["email"]
    
    def test_authenticate_user_invalid_credentials(self):
        """Test authentication with invalid credentials"""
        auth_service = AuthService()
        user_data = {
            "email": "test@example.com",
            "password": "wrong_password"
        }
        
        result = auth_service.authenticate_user(user_data)
        
        assert result["success"] is False
        assert "error" in result
        assert "Invalid credentials" in result["error"]
```

#### Step 2: GREEN - Implement Minimal Code
```python
# app/services/auth_service.py
from typing import Dict, Any

class AuthService:
    def authenticate_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        # Minimal implementation to make tests pass
        if user_data["password"] == "secure_password":
            return {
                "success": True,
                "data": {
                    "access_token": "mock_access_token",
                    "refresh_token": "mock_refresh_token",
                    "user": {
                        "email": user_data["email"],
                        "id": "mock_user_id"
                    }
                }
            }
        else:
            return {
                "success": False,
                "error": "Invalid credentials"
            }
```

#### Step 3: REFACTOR - Improve Implementation
```python
# app/services/auth_service.py
import bcrypt
import jwt
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.core.database import get_db
from app.models.user import User

class AuthService:
    def __init__(self):
        self.secret_key = "your-secret-key"
        self.algorithm = "HS256"
    
    async def authenticate_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate user with email and password"""
        try:
            async with get_db() as db:
                user = await self._get_user_by_email(db, user_data["email"])
                
                if not user or not self._verify_password(user_data["password"], user.hashed_password):
                    return {
                        "success": False,
                        "error": "Invalid credentials"
                    }
                
                tokens = self._generate_tokens(user)
                
                return {
                    "success": True,
                    "data": {
                        "access_token": tokens["access_token"],
                        "refresh_token": tokens["refresh_token"],
                        "user": {
                            "id": str(user.id),
                            "email": user.email,
                            "is_active": user.is_active
                        }
                    }
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Authentication failed: {str(e)}"
            }
    
    async def _get_user_by_email(self, db, email: str) -> Optional[User]:
        """Get user by email from database"""
        # Implementation here
        pass
    
    def _verify_password(self, password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    def _generate_tokens(self, user: User) -> Dict[str, str]:
        """Generate access and refresh tokens"""
        payload = {
            "user_id": str(user.id),
            "email": user.email,
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        
        access_token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        refresh_payload = {
            "user_id": str(user.id),
            "exp": datetime.utcnow() + timedelta(days=7)
        }
        
        refresh_token = jwt.encode(refresh_payload, self.secret_key, algorithm=self.algorithm)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }
```

### Example 2: Adding Frontend Component

#### Step 1: RED - Write Failing Test
```typescript
// __tests__/components/LoginForm.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginForm } from '@/components/LoginForm';

describe('LoginForm', () => {
  const defaultProps = {
    onLogin: jest.fn(),
    onRegister: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders login form with email and password fields', () => {
    render(<LoginForm {...defaultProps} />);
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('calls onLogin with form data when submitted', async () => {
    render(<LoginForm {...defaultProps} />);
    
    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);
    const submitButton = screen.getByRole('button', { name: /login/i });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(defaultProps.onLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123'
      });
    });
  });

  it('shows validation errors for empty fields', async () => {
    render(<LoginForm {...defaultProps} />);
    
    const submitButton = screen.getByRole('button', { name: /login/i });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText(/email is required/i)).toBeInTheDocument();
      expect(screen.getByText(/password is required/i)).toBeInTheDocument();
    });
  });
});
```

#### Step 2: GREEN - Implement Minimal Component
```typescript
// components/LoginForm.tsx
import React, { useState } from 'react';

interface LoginFormProps {
  onLogin: (data: { email: string; password: string }) => void;
  onRegister: () => void;
}

export function LoginForm({ onLogin, onRegister }: LoginFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const newErrors: { email?: string; password?: string } = {};
    
    if (!email) newErrors.email = 'Email is required';
    if (!password) newErrors.password = 'Password is required';
    
    setErrors(newErrors);
    
    if (Object.keys(newErrors).length === 0) {
      onLogin({ email, password });
    }
  };

  return (
    <form onSubmit={handleSubmit} data-testid="login-form">
      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          aria-label="Email"
        />
        {errors.email && <span>{errors.email}</span>}
      </div>
      
      <div>
        <label htmlFor="password">Password</label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          aria-label="Password"
        />
        {errors.password && <span>{errors.password}</span>}
      </div>
      
      <button type="submit">Login</button>
      <button type="button" onClick={onRegister}>Register</button>
    </form>
  );
}
```

#### Step 3: REFACTOR - Improve Component
```typescript
// components/LoginForm.tsx
import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Loader2 } from 'lucide-react';

interface LoginFormProps {
  onLogin: (data: { email: string; password: string }) => Promise<void>;
  onRegister: () => void;
  isLoading?: boolean;
  error?: string;
}

export function LoginForm({ onLogin, onRegister, isLoading = false, error }: LoginFormProps) {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});

  const validateForm = () => {
    const newErrors: { email?: string; password?: string } = {};
    
    if (!email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!password) {
      newErrors.password = 'Password is required';
    } else if (password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    try {
      await onLogin({ email, password });
    } catch (err) {
      // Error handling is done by parent component
    }
  };

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Login to ArchMesh</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} data-testid="login-form">
          {error && (
            <Alert variant="destructive" className="mb-4">
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}
          
          <div className="space-y-4">
            <div>
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                aria-label="Email"
                disabled={isLoading}
                className={errors.email ? 'border-red-500' : ''}
              />
              {errors.email && (
                <p className="text-sm text-red-500 mt-1">{errors.email}</p>
              )}
            </div>
            
            <div>
              <Label htmlFor="password">Password</Label>
              <Input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                aria-label="Password"
                disabled={isLoading}
                className={errors.password ? 'border-red-500' : ''}
              />
              {errors.password && (
                <p className="text-sm text-red-500 mt-1">{errors.password}</p>
              )}
            </div>
            
            <div className="space-y-2">
              <Button 
                type="submit" 
                className="w-full" 
                disabled={isLoading}
              >
                {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Login
              </Button>
              
              <Button 
                type="button" 
                variant="outline" 
                className="w-full"
                onClick={onRegister}
                disabled={isLoading}
              >
                Create Account
              </Button>
            </div>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
```

### Example 3: Adding API Endpoint

#### Step 1: RED - Write Failing Test
```python
# tests/unit/test_auth_api.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

class TestAuthAPI:
    def test_login_endpoint_success(self, client: TestClient):
        """Test successful login via API"""
        login_data = {
            "email": "test@example.com",
            "password": "secure_password"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "access_token" in data["data"]
        assert "user" in data["data"]
    
    def test_login_endpoint_invalid_credentials(self, client: TestClient):
        """Test login with invalid credentials"""
        login_data = {
            "email": "test@example.com",
            "password": "wrong_password"
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert data["success"] is False
        assert "Invalid credentials" in data["error"]
    
    def test_login_endpoint_missing_fields(self, client: TestClient):
        """Test login with missing required fields"""
        login_data = {
            "email": "test@example.com"
            # Missing password
        }
        
        response = client.post("/api/v1/auth/login", json=login_data)
        
        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
```

#### Step 2: GREEN - Implement Minimal Endpoint
```python
# app/api/v1/auth.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

router = APIRouter()

class LoginRequest(BaseModel):
    email: str
    password: str

class LoginResponse(BaseModel):
    success: bool
    data: Dict[str, Any] = None
    error: str = None

@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Login endpoint"""
    # Minimal implementation
    if request.password == "secure_password":
        return LoginResponse(
            success=True,
            data={
                "access_token": "mock_token",
                "user": {"email": request.email}
            }
        )
    else:
        raise HTTPException(
            status_code=401,
            detail="Invalid credentials"
        )
```

#### Step 3: REFACTOR - Improve Endpoint
```python
# app/api/v1/auth.py
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, EmailStr
from typing import Dict, Any, Optional
from app.services.auth_service import AuthService
from app.core.database import get_db
from app.models.user import User

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class LoginResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/login", response_model=LoginResponse)
async def login(
    request: LoginRequest,
    db = Depends(get_db)
):
    """Authenticate user and return tokens"""
    try:
        auth_service = AuthService()
        result = await auth_service.authenticate_user({
            "email": request.email,
            "password": request.password
        })
        
        if result["success"]:
            return LoginResponse(
                success=True,
                data=result["data"]
            )
        else:
            raise HTTPException(
                status_code=401,
                detail=result["error"]
            )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Authentication failed: {str(e)}"
        )
```

## TDD Best Practices for ArchMesh

### 1. Test Organization
```
tests/
├── unit/                    # Fast, isolated tests
│   ├── agents/             # AI agent tests
│   ├── services/           # Service layer tests
│   ├── core/               # Core utility tests
│   └── api/                # API endpoint tests
├── integration/            # Component interaction tests
│   ├── workflows/          # Workflow integration tests
│   └── services/           # Service integration tests
├── e2e/                    # End-to-end workflow tests
├── performance/            # Performance and load tests
├── security/               # Security vulnerability tests
└── fixtures/               # Test data and fixtures
```

### 2. Naming Conventions
```python
# Test file naming
test_<module_name>.py

# Test class naming
class Test<ClassName>:

# Test method naming
def test_<method_name>_<scenario>_<expected_result>():
    """Test <method_name> with <scenario> returns <expected_result>"""
```

### 3. Test Data Management
```python
# Use fixtures for test data
@pytest.fixture
def sample_user_data():
    return {
        "email": "test@example.com",
        "password": "secure_password",
        "name": "Test User"
    }

@pytest.fixture
def sample_project_data():
    return {
        "name": "Test Project",
        "description": "Test Description",
        "domain": "cloud-native"
    }
```

### 4. Mocking Strategy
```python
# Mock external dependencies
@pytest.fixture
def mock_llm_client():
    with patch('app.core.llm_strategy.LLMStrategy.get_llm') as mock:
        mock.return_value.invoke.return_value = "Mocked response"
        yield mock

# Mock database operations
@pytest.fixture
def mock_db_session():
    with patch('app.core.database.get_db') as mock:
        mock_session = AsyncMock()
        mock.return_value = mock_session
        yield mock_session
```

## Running TDD Workflow

### Daily TDD Workflow
1. **Start with failing test** (RED)
2. **Write minimal code** to pass (GREEN)
3. **Refactor and improve** (REFACTOR)
4. **Run full test suite** to ensure no regressions
5. **Commit with descriptive message**

### CI/CD Integration
```yaml
# .github/workflows/tdd-pipeline.yml
name: TDD Pipeline
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: |
          cd backend && pytest --cov=app --cov-fail-under=90
          cd frontend && npm test -- --coverage --watchAll=false
```

This implementation guide provides practical examples and patterns specifically tailored for ArchMesh's architecture and requirements.

