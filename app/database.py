import firebase_admin
from motor.motor_asyncio import AsyncIOMotorClient
from firebase_admin import credentials, firestore




# MongoDB connection details
MONGO_URL = "mongodb://localhost:27017"  # Adjust this based on your setup
DATABASE_NAME = "fastapilibrary"

# Create the MongoDB client
client = AsyncIOMotorClient(MONGO_URL)
db_mongo = client.fastapilibrary
# Access the database
db = client[DATABASE_NAME]
users_collection = db.users 

# Dependency to get the database
def get_db():
    return db




# # Path to Firebase Admin SDK private key
# FIREBASE_CREDENTIALS_PATH = "/home/bino-tech/Test/demo/library-management-syste-11e9a-firebase-adminsdk-xm2rs-7972e40a94.json"

# # Initialize Firebase Admin SDK
# cred = credentials.Certificate(FIREBASE_CREDENTIALS_PATH)
# firebase_admin.initialize_app(cred)

# # Firestore database client
# firestore_db = firestore.client()

# # Dependency to get the Firestore client
# def get_firestore_db():
#     return firestore_db

#Initialize Firebase Admin SDK
cred = credentials.Certificate("/home/bino-tech/Downloads/library-management-syste-11e9a-firebase-adminsdk-xm2rs-d039b2b2c3.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://library-management-syste-11e9a-default-rtdb.asia-southeast1.firebasedatabase.app'
})

