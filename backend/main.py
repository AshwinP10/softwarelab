from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import json
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import uuid

app = FastAPI(title="HaaS API", description="Hardware-as-a-Service API", version="1.0.0")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Data models
class User(BaseModel):
    id: str
    email: str
    hashed_password: str
    created_at: str

class UserCreate(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class Project(BaseModel):
    id: str
    name: str
    description: str
    user_id: str
    created_at: str

class ProjectCreate(BaseModel):
    name: str
    description: str

class HardwareSet(BaseModel):
    id: str
    name: str
    total_capacity: int
    available_capacity: int

class CheckoutRequest(BaseModel):
    hardware_set_id: str
    project_id: str
    quantity: int

class CheckinRequest(BaseModel):
    hardware_set_id: str
    project_id: str
    quantity: int

class Token(BaseModel):
    access_token: str
    token_type: str

# Database functions (JSON file-based)
def load_data(filename: str):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return []

def save_data(filename: str, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

def get_users():
    return load_data('users.json')

def save_users(users):
    save_data('users.json', users)

def get_projects():
    return load_data('projects.json')

def save_projects(projects):
    save_data('projects.json', projects)

def get_hardware():
    return load_data('hardware.json')

def save_hardware(hardware):
    save_data('hardware.json', hardware)

def get_checkouts():
    return load_data('checkouts.json')

def save_checkouts(checkouts):
    save_data('checkouts.json', checkouts)

# Initialize hardware sets if not exists
def init_hardware():
    hardware = get_hardware()
    if not hardware:
        hardware = [
            {
                "id": "hwset1",
                "name": "HWSet1",
                "total_capacity": 10,
                "available_capacity": 10
            },
            {
                "id": "hwset2", 
                "name": "HWSet2",
                "total_capacity": 20,
                "available_capacity": 20
            }
        ]
        save_hardware(hardware)

# Auth functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    users = get_users()
    user = next((u for u in users if u["email"] == email), None)
    if user is None:
        raise credentials_exception
    return user

# API Routes
@app.on_event("startup")
async def startup_event():
    init_hardware()

@app.get("/")
async def root():
    return {"message": "HaaS API is running"}

@app.post("/auth/signup", response_model=Token)
async def signup(user: UserCreate):
    users = get_users()
    
    # Check if user exists
    if any(u["email"] == user.email for u in users):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    new_user = {
        "id": str(uuid.uuid4()),
        "email": user.email,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow().isoformat()
    }
    
    users.append(new_user)
    save_users(users)
    
    # Create token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/auth/login", response_model=Token)
async def login(user: UserLogin):
    users = get_users()
    db_user = next((u for u in users if u["email"] == user.email), None)
    
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/projects", response_model=List[Project])
async def get_user_projects(current_user: dict = Depends(get_current_user)):
    projects = get_projects()
    user_projects = [p for p in projects if p["user_id"] == current_user["id"]]
    return user_projects

@app.post("/projects", response_model=Project)
async def create_project(project: ProjectCreate, current_user: dict = Depends(get_current_user)):
    projects = get_projects()
    
    new_project = {
        "id": str(uuid.uuid4()),
        "name": project.name,
        "description": project.description,
        "user_id": current_user["id"],
        "created_at": datetime.utcnow().isoformat()
    }
    
    projects.append(new_project)
    save_projects(projects)
    return new_project

@app.get("/hardware", response_model=List[HardwareSet])
async def get_hardware_sets(current_user: dict = Depends(get_current_user)):
    return get_hardware()

@app.post("/hardware/checkout")
async def checkout_hardware(request: CheckoutRequest, current_user: dict = Depends(get_current_user)):
    hardware = get_hardware()
    projects = get_projects()
    checkouts = get_checkouts()
    
    # Verify project belongs to user
    project = next((p for p in projects if p["id"] == request.project_id and p["user_id"] == current_user["id"]), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Find hardware set
    hw_set = next((h for h in hardware if h["id"] == request.hardware_set_id), None)
    if not hw_set:
        raise HTTPException(status_code=404, detail="Hardware set not found")
    
    # Check availability
    if hw_set["available_capacity"] < request.quantity:
        raise HTTPException(status_code=400, detail="Not enough hardware available")
    
    # Update hardware capacity
    hw_set["available_capacity"] -= request.quantity
    save_hardware(hardware)
    
    # Record checkout
    checkout = {
        "id": str(uuid.uuid4()),
        "hardware_set_id": request.hardware_set_id,
        "project_id": request.project_id,
        "user_id": current_user["id"],
        "quantity": request.quantity,
        "checked_out_at": datetime.utcnow().isoformat(),
        "checked_in_at": None
    }
    checkouts.append(checkout)
    save_checkouts(checkouts)
    
    return {"message": f"Checked out {request.quantity} units of {hw_set['name']}"}

@app.post("/hardware/checkin")
async def checkin_hardware(request: CheckinRequest, current_user: dict = Depends(get_current_user)):
    hardware = get_hardware()
    projects = get_projects()
    checkouts = get_checkouts()
    
    # Verify project belongs to user
    project = next((p for p in projects if p["id"] == request.project_id and p["user_id"] == current_user["id"]), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Find hardware set
    hw_set = next((h for h in hardware if h["id"] == request.hardware_set_id), None)
    if not hw_set:
        raise HTTPException(status_code=404, detail="Hardware set not found")
    
    # Find active checkouts for this project and hardware
    active_checkouts = [c for c in checkouts if 
                       c["hardware_set_id"] == request.hardware_set_id and 
                       c["project_id"] == request.project_id and 
                       c["checked_in_at"] is None]
    
    total_checked_out = sum(c["quantity"] for c in active_checkouts)
    
    if total_checked_out < request.quantity:
        raise HTTPException(status_code=400, detail="Cannot check in more than checked out")
    
    # Update hardware capacity
    hw_set["available_capacity"] += request.quantity
    save_hardware(hardware)
    
    # Mark checkouts as returned (simplified - mark oldest first)
    remaining_to_checkin = request.quantity
    for checkout in active_checkouts:
        if remaining_to_checkin <= 0:
            break
        
        if checkout["quantity"] <= remaining_to_checkin:
            checkout["checked_in_at"] = datetime.utcnow().isoformat()
            remaining_to_checkin -= checkout["quantity"]
        else:
            # Partial checkin - split the checkout record
            new_checkout = checkout.copy()
            new_checkout["id"] = str(uuid.uuid4())
            new_checkout["quantity"] = checkout["quantity"] - remaining_to_checkin
            checkouts.append(new_checkout)
            
            checkout["quantity"] = remaining_to_checkin
            checkout["checked_in_at"] = datetime.utcnow().isoformat()
            remaining_to_checkin = 0
    
    save_checkouts(checkouts)
    
    return {"message": f"Checked in {request.quantity} units of {hw_set['name']}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
