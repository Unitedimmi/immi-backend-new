from fastapi import APIRouter, HTTPException
from app.models.admin import AdminSignupModel, AdminLoginModel
from app.utils.auth import hash_password, verify_password, create_id_token
from app.database import db  

router = APIRouter(prefix="/admin", tags=["Admin Auth"])

@router.post("/signup")
async def admin_signup(admin: AdminSignupModel):
    try:
        # Check if email already exists in the admin collection
        existing_admin = await db.admin.find_one({"email": admin.email})
        if existing_admin:
            raise HTTPException(status_code=400, detail="Email already registered")

        admin_dict = {
            "email": admin.email,
            "password": hash_password(admin.password),
            "role": "admin"
        }

        await db.admin.insert_one(admin_dict)  # inserting into admin collection

        return {
            "message": "Admin registered successfully",
            "email": admin.email,
            "role": "admin"
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Unhandled admin signup error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/login")
async def admin_login(admin: AdminLoginModel):
    try:
        # Find admin in the admin collection
        db_admin = await db.admin.find_one({"email": admin.email})
        if not db_admin or not verify_password(admin.password, db_admin["password"]):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_id_token(data={"sub": admin.email, "role": "admin"})

        return {
            "idToken": token,
            "email": db_admin["email"],
            "role": db_admin["role"]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Admin login error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
