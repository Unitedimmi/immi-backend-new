from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = "mongodb+srv://admin:admin@cluster0.ifswddf.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = AsyncIOMotorClient(MONGO_URI)
db = client.immigration
