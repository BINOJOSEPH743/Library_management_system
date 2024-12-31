import firebase_admin
from motor.motor_asyncio import AsyncIOMotorClient
from firebase_admin import credentials, db as firebase_db,messaging

# MongoDB Connection Details
MONGO_URL = "mongodb://localhost:27017"
DATABASE_NAME = "fastapilibrary"

# Create the MongoDB Client
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client[DATABASE_NAME]  # Access the MongoDB database
users_collection = db.users  # Access the users collection

# Dependency to get the MongoDB database
def get_db():
    return db


# Firebase Admin SDK Configuration
FIREBASE_CREDENTIALS_PATH = "/home/bino-tech/Downloads/library-management-syste-11e9a-firebase-adminsdk-xm2rs-bfe3fbbf10.json"

# Initialize Firebase Admin SDK
cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://library-management-syste-11e9a-default-rtdb.asia-southeast1.firebasedatabase.app'
})

# Firebase Realtime Database Reference
firebase_ref = firebase_db.reference('/messages')
