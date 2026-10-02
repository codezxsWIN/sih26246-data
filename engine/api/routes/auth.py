from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/auth", tags=["auth"])

class LoginRequest(BaseModel):
    email: str
    password: str
    role: str

class LoginResponse(BaseModel):
    token: str
    role: str
    user_id: int

@router.post("/login", response_model=LoginResponse)
def login(request: LoginRequest):
    # Mock auth for prototype
    valid_roles = ["policymaker", "seeker", "employer"]
    if request.role not in valid_roles:
        raise HTTPException(status_code=400, detail="Invalid role")
        
    return LoginResponse(
        token=f"mock-jwt-token-{request.role}-123",
        role=request.role,
        user_id=1
    )

@router.post("/register", response_model=LoginResponse)
def register(request: LoginRequest):
    return LoginResponse(
        token=f"mock-jwt-token-{request.role}-123",
        role=request.role,
        user_id=1
    )
