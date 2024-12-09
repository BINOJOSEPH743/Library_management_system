from motor.motor_asyncio import AsyncIOMotorClient


# MongoDB connection details
MONGO_URL = "mongodb://localhost:27017"  # Adjust this based on your setup
DATABASE_NAME = "fastapilibrary"

# Create the MongoDB client
client = AsyncIOMotorClient(MONGO_URL)

# Access the database
db = client[DATABASE_NAME]

# Dependency to get the database
def get_db():
    return db

