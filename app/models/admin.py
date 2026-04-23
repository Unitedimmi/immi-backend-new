from pydantic import BaseModel, EmailStr

class AdminSignupModel(BaseModel):
    email: EmailStr
    password: str

class AdminLoginModel(BaseModel):
    email: EmailStr
    password: str
