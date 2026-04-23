from fastapi import APIRouter, HTTPException
from app.models.user import SignupModel, LoginModel
from app.utils.auth import hash_password, verify_password, create_id_token
from app.database import db
import uuid

router = APIRouter()

@router.post("/signup")
async def signup(user: SignupModel):
    try:
        # Check if user already exists
        existing_user = await db.users.find_one({"email": user.email})
        if existing_user:
            # Explicitly raise and handle known condition
            raise HTTPException(status_code=400, detail="Email already registered")

        # Prepare user dict
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        user_dict = user.model_dump()
        user_dict["user_id"] = user_id
        user_dict["password"] = hash_password(user.password)

        await db.users.insert_one(user_dict)

        return {
            "message": "User registered successfully",
            "user_id": user_id,
            "name": user.name,
            "email": user.email,
            "phone_number": user.phone_number
        }

    except HTTPException as http_ex:
        # Re-raise known handled errors like 400
        raise http_ex

    except Exception as e:
        print(f"Unhandled signup error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login")
async def login(user: LoginModel):
    try:
        # Use await with Motor's async find_one
        db_user = await db.users.find_one({"email": user.email})
        if not db_user or not verify_password(user.password, db_user["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        id_token = create_id_token(data={"sub": user.email})

        return {
            "idToken": id_token,
            "user_id": db_user.get("user_id"),
            "name": db_user.get("name"),
            "email": db_user.get("email"),
            "phone_number": db_user.get("phone_number")
        }
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# Optional: Add connection testing
@router.get("/health")
async def health_check():
    try:
        # Test database connection
        await db.command("ping")
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        print(f"Database connection error: {e}")
        raise HTTPException(status_code=503, detail="Database unavailable")