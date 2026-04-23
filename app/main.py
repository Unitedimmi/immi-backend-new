from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import warnings
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")

from app.routes import auth, upload, user_info,admin, visa_user_details , email
from app.routes import payment

app = FastAPI(
    title="Immigration Backend API",
    description="API for immigration services",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(upload.router)
app.include_router(user_info.router)
app.include_router(payment.router)
app.include_router(admin.router)  
app.include_router(visa_user_details.router)
app.include_router(email.router)


@app.get("/")
async def root():
    return {"message": "Immigration Backend API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Service is running"}
