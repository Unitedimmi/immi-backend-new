
# from fastapi import APIRouter, Depends, HTTPException
# from typing import List, Dict
# from datetime import datetime
# import hmac
# import hashlib

# from app.utils.razorpay_config import client, RAZORPAY_KEY_SECRET
# from app.models.payment import PaymentRequest, VerifyRequest, PaymentRecord, UserTransactions
# from app.utils.auth import get_current_user
# from app.database import db  # Import your existing database connection

# router = APIRouter(prefix="/payment", tags=["Payment"])

# # Collections using your existing db connection
# payment_collection = db.payments  # All payments
# user_collection = db.user_transactions  # Users with their transactions  
# verified_collection = db.verified_transactions  # Verified transactions

# # Add payment record and update user collection
# async def add_payment_record(user_id, order_id, amount, currency, status):
#     # Create payment record
#     payment_data = {
#         "user_id": user_id,
#         "razorpay_order_id": order_id,
#         "razorpay_payment_id": None,
#         "amount": amount,
#         "currency": currency,
#         "status": status,
#         "timestamp": datetime.now()
#     }
    
#     # Add to main payment database
#     await payment_collection.insert_one(payment_data)
    
#     # Add to user collection
#     user_doc = await user_collection.find_one({"user_id": user_id})
    
#     if not user_doc:
#         # Create new user document
#         user_data = {
#             "user_id": user_id,
#             "total_paid": 0.0,
#             "transaction_count": 1,
#             "transactions": [payment_data]
#         }
#         await user_collection.insert_one(user_data)
#     else:
#         # Update existing user document
#         await user_collection.update_one(
#             {"user_id": user_id},
#             {
#                 "$push": {"transactions": payment_data},
#                 "$inc": {"transaction_count": 1}
#             }
#         )

# # Update payment status in both collections
# async def update_payment_status(order_id, payment_id, status):
#     # Update in main payment database
#     payment_doc = await payment_collection.find_one({"razorpay_order_id": order_id})
    
#     if payment_doc:
#         update_data = {
#             "razorpay_payment_id": payment_id,
#             "status": status
#         }
        
#         await payment_collection.update_one(
#             {"razorpay_order_id": order_id},
#             {"$set": update_data}
#         )
        
#         # If payment is verified, save to verified collection
#         if status == "paid":
#             verified_payment = {**payment_doc, **update_data}
#             await verified_collection.insert_one(verified_payment)
        
#         # Update in user collection
#         user_id = payment_doc["user_id"]
#         user_doc = await user_collection.find_one({"user_id": user_id})
        
#         if user_doc:
#             # Update the specific transaction in the user's transactions array
#             await user_collection.update_one(
#                 {"user_id": user_id, "transactions.razorpay_order_id": order_id},
#                 {
#                     "$set": {
#                         "transactions.$.razorpay_payment_id": payment_id,
#                         "transactions.$.status": status
#                     }
#                 }
#             )
            
#             # If payment is successful, add to total_paid
#             if status == "paid":
#                 await user_collection.update_one(
#                     {"user_id": user_id},
#                     {"$inc": {"total_paid": payment_doc["amount"]}}
#                 )

# # Get all payments (for testing/debug)
# async def get_all_payments():
#     payments = []
#     async for payment in payment_collection.find():
#         payments.append(payment)
#     return payments

# # Get user transactions
# async def get_user_transactions(user_id: str):
#     user_doc = await user_collection.find_one({"user_id": user_id})
#     if user_doc:
#         return user_doc
#     else:
#         return {
#             "user_id": user_id,
#             "total_paid": 0.0,
#             "transaction_count": 0,
#             "transactions": []
#         }

# # Get all users with their transaction data
# async def get_all_users():
#     users = {}
#     async for user in user_collection.find():
#         users[user["user_id"]] = user
#     return users

# @router.post("/pay")
# async def create_order(request: PaymentRequest):
#     try:
#         order = client.order.create({
#             "amount": int(request.amount * 100), 
#             "currency": request.currency,
#             "payment_capture": 1
#         })

#         await add_payment_record(
#             user_id=request.user_id,
#             order_id=order["id"],
#             amount=request.amount,
#             currency=request.currency,
#             status="created"
#         )

#         return {
#             "order_id": order["id"],
#             "currency": request.currency,
#             "amount": request.amount,
#             "status": "created"
#         }

#     except Exception as e:
#         raise HTTPException(status_code=400, detail=f"Payment order creation failed: {str(e)}")

# @router.post("/verify")
# async def verify_payment(data: VerifyRequest):
#     body = f"{data.razorpay_order_id}|{data.razorpay_payment_id}"

#     expected_signature = hmac.new(
#         key=bytes(RAZORPAY_KEY_SECRET, 'utf-8'),
#         msg=bytes(body, 'utf-8'),
#         digestmod=hashlib.sha256
#     ).hexdigest()

#     if expected_signature == data.razorpay_signature:
#         await update_payment_status(
#             order_id=data.razorpay_order_id,
#             payment_id=data.razorpay_payment_id,
#             status="paid"
#         )
#         return {"status": "Payment verified successfully."}
#     else:
#         await update_payment_status(
#             order_id=data.razorpay_order_id,
#             payment_id=data.razorpay_payment_id,
#             status="failed"
#         )
#         raise HTTPException(status_code=400, detail="Invalid payment signature.")

# # Get user transaction data
# @router.get("/user/{user_id}")
# def get_user_data(user_id: str):
#     """Get all transactions for a specific user"""
#     user_data = get_user_transactions(user_id)
#     return {
#         "user_id": user_data.user_id,
#         "total_paid": user_data.total_paid,
#         "transaction_count": user_data.transaction_count,
#         "transactions": user_data.transactions
#     }



from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from datetime import datetime, timezone
import hmac
import hashlib

from app.utils.razorpay_config import client, RAZORPAY_KEY_SECRET
from app.models.payment import PaymentRequest, VerifyRequest
from app.utils.auth import get_current_user
from app.database import db  

router = APIRouter(prefix="/payment", tags=["Payment"],dependencies=[Depends(get_current_user)]  )

# Collections using your existing db connection
payment_collection = db.payments  # All payments
user_collection = db.user_transactions  # Users with their transactions  
verified_collection = db.verified_transactions  # Verified transactions

# Add payment record and update user collection
async def add_payment_record(user_id, order_id, amount, currency, status):
    # Create payment record
    payment_data = {
        "user_id": user_id,
        "razorpay_order_id": order_id,
        "razorpay_payment_id": None,
        "amount": amount,
        "currency": currency,
        "status": status,
        "timestamp": datetime.now(timezone.utc)
    }
    
    # Add to main payment database
    await payment_collection.insert_one(payment_data)
    
    # Add to user collection
    user_doc = await user_collection.find_one({"user_id": user_id})
    
    if not user_doc:
        # Create new user document
        user_data = {
            "user_id": user_id,
            "total_paid": 0.0,
            "transaction_count": 1,
            "transactions": [payment_data]
        }
        await user_collection.insert_one(user_data)
    else:
        # Update existing user document
        await user_collection.update_one(
            {"user_id": user_id},
            {
                "$push": {"transactions": payment_data},
                "$inc": {"transaction_count": 1}
            }
        )

# Update payment status in both collections
async def update_payment_status(order_id, payment_id, status):
    # Update in main payment database
    payment_doc = await payment_collection.find_one({"razorpay_order_id": order_id})
    
    if payment_doc:
        update_data = {
            "razorpay_payment_id": payment_id,
            "status": status
        }
        
        await payment_collection.update_one(
            {"razorpay_order_id": order_id},
            {"$set": update_data}
        )
        
        # If payment is verified, save to verified collection
        if status == "paid":
            verified_payment = {**payment_doc, **update_data}
            await verified_collection.insert_one(verified_payment)
        
        # Update in user collection
        user_id = payment_doc["user_id"]
        user_doc = await user_collection.find_one({"user_id": user_id})
        
        if user_doc:
            # Update the specific transaction in the user's transactions array
            await user_collection.update_one(
                {"user_id": user_id, "transactions.razorpay_order_id": order_id},
                {
                    "$set": {
                        "transactions.$.razorpay_payment_id": payment_id,
                        "transactions.$.status": status
                    }
                }
            )
            
            # If payment is successful, add to total_paid
            if status == "paid":
                await user_collection.update_one(
                    {"user_id": user_id},
                    {"$inc": {"total_paid": payment_doc["amount"]}}
                )

# Get user transactions
async def get_user_transactions(user_id: str):
    user_doc = await user_collection.find_one({"user_id": user_id})
    if user_doc:
        # Convert ObjectId to string for JSON serialization
        user_doc["_id"] = str(user_doc["_id"])
        return user_doc
    else:
        return {
            "user_id": user_id,
            "total_paid": 0.0,
            "transaction_count": 0,
            "transactions": []
        }

@router.post("/pay")
async def create_order(request: PaymentRequest):
    try:
        order = client.order.create({
            "amount": int(request.amount * 100), 
            "currency": request.currency,
            "payment_capture": 1
        })

        await add_payment_record(
            user_id=request.user_id,
            order_id=order["id"],
            amount=request.amount,
            currency=request.currency,
            status="created"
        )

        return {
            "order_id": order["id"],
            "currency": request.currency,
            "amount": request.amount,
            "status": "created"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Payment order creation failed: {str(e)}")

@router.post("/verify")
async def verify_payment(data: VerifyRequest):
    body = f"{data.razorpay_order_id}|{data.razorpay_payment_id}"

    expected_signature = hmac.new(
        key=bytes(RAZORPAY_KEY_SECRET, 'utf-8'),
        msg=bytes(body, 'utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

    if expected_signature == data.razorpay_signature:
        await update_payment_status(
            order_id=data.razorpay_order_id,
            payment_id=data.razorpay_payment_id,
            status="paid"
        )
        return {"status": "Payment verified successfully."}
    else:
        await update_payment_status(
            order_id=data.razorpay_order_id,
            payment_id=data.razorpay_payment_id,
            status="failed"
        )
        raise HTTPException(status_code=400, detail="Invalid payment signature.")

@router.get("/user/{user_id}")
async def get_user_data(user_id: str):
    """Get all transactions for a specific user"""
    try:
        # Get all transactions for this user from verified_transactions collection
        transactions = []
        async for transaction in verified_collection.find({"user_id": user_id}):
            # Convert ObjectId to string for JSON serialization
            transaction["_id"] = str(transaction["_id"])
            transactions.append(transaction)
        
        # Calculate total paid amount
        total_paid = sum(t.get("amount", 0) for t in transactions if t.get("status") == "paid")
        
        # Return user data
        return {
            "user_id": user_id,
            "total_paid": total_paid,
            "transaction_count": len(transactions),
            "transactions": transactions
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching user data: {str(e)}")
