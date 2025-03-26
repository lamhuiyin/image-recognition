import firebase_admin
from firebase_admin import credentials, firestore, storage

def initialize_firebase():
    """Initialize Firebase only if not already initialized"""
    if not firebase_admin._apps:
        cred = credentials.Certificate("/content/final-year-project-ceci1-firebase-adminsdk-592aj-ef68c17717.json")
        firebase_admin.initialize_app(cred, {
            'storageBucket': 'final-year-project-ceci1.appspot.com'
        })
    
    # Get Firestore and Storage clients
    db = firestore.client()
    bucket = storage.bucket()
    
    return db, bucket
