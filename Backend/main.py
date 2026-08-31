# Backend/main.py
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from database import get_db_cursor, init_db
import schemas
import security

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    init_db()
    yield

app = FastAPI(title="Bright Buy Retail Backend", lifespan=lifespan)

# Enable CORS for React Frontend (vite default: http://localhost:5173)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/register", status_code=status.HTTP_201_CREATED)
def register(user_data: schemas.UserRegisterRequest, cursor = Depends(get_db_cursor)):
    # 1. Check if user already exists
    cursor.execute("SELECT id FROM users WHERE email = %s", (user_data.email,))
    existing_user = cursor.fetchone()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists."
        )
    
    # 2. Hash the password
    hashed_pwd = security.hash_password(user_data.password)

    # 3. Create and save new user record
    cursor.execute(
        "INSERT INTO users (email, hashed_password, phonenum) VALUES (%s, %s, %s)",
        (user_data.email, hashed_pwd, user_data.phonenum)
    )
    user_id = cursor.lastrowid

    return {"message": "User registered successfully!", "user_id": user_id}


@app.post("/api/login", response_model=schemas.TokenResponse)
def login(login_data: schemas.UserLoginRequest, cursor = Depends(get_db_cursor)):
    # 1. Look up user by email
    cursor.execute(
        "SELECT id, email, hashed_password, phonenum FROM users WHERE email = %s",
        (login_data.email,)
    )
    user = cursor.fetchone()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    # 2. Verify password hash
    if not security.verify_password(login_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    # 3. Generate JWT access token
    access_token = security.create_access_token(data={"sub": user["email"], "id": user["id"]})

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "phonenum": user.get("phonenum")
        }
    }

@app.get("/")
def root():
    return {"message": "Bright Buy Retail API is running"}
