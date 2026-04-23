from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class PaymentRequest(BaseModel):
    user_id: str
    amount: float
    currency: str  # 'INR' or 'AUD'

class VerifyRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str

class PaymentRecord(BaseModel):
    user_id: str
    razorpay_order_id: str
    razorpay_payment_id: Optional[str] = None
    amount: float
    currency: str
    status: str  # created, paid, failed
    timestamp: datetime

# New model for user transaction collection
class UserTransactions(BaseModel):
    user_id: str
    transactions: List[PaymentRecord] = []
    total_paid: float = 0.0  # Total amount paid by user
    transaction_count: int = 0