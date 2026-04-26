import os
from pymongo import MongoClient

MONGO_URL = os.environ.get("MONGODB_URL", None)

if MONGO_URL:
    client = MongoClient(MONGO_URL)
    db = client["ResuMate_ai"]
    resumes_collection = db["resumes"]
else:
    client = None
    db = None
    resumes_collection = None