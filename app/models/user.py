from pydantic import BaseModel, EmailStr, Field

class SignupModel(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone_number: str = Field(..., min_length=10, max_length=15)

class LoginModel(BaseModel):
    email: EmailStr
    password: str

class UserInDB(BaseModel):
    name: str
    email: EmailStr
    password: str  # hashed
