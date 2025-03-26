import numpy as np
from firebase.config import initialize_firebase
from features.extractor import extract_features

def search_similar_images(query_image_path, top_k=5):
    """Search for similar clothing items based on an image"""
    # Extract features from query image
    query_features = extract_features(query_image_path)
    if query_features is None:
        return []
    
    db, _ = initialize_firebase()
    # Get all clothes with feature vectors
    clothes_ref = db.collection('clothes')
    docs = clothes_ref.where('featureVector', '!=', None).stream()
    
    # Calculate similarities
    similarities = []
    for doc in docs:
        data = doc.to_dict()
        db_features = np.array(data['featureVector'])
        # Cosine similarity
        similarity = np.dot(query_features, db_features) / (
            np.linalg.norm(query_features) * np.linalg.norm(db_features))
        similarities.append({
            'id': doc.id,
            'similarity': similarity,
            #'data': data
        })
    
    # Sort by similarity and return top results
    return sorted(similarities, key=lambda x: x['similarity'], reverse=True)[:top_k]

def get_similar_items(item_id, top_k=5):
    """Find similar items to a specific clothing item"""
    db, _ = initialize_firebase()
    # Get the target item's features
    doc_ref = db.collection('clothes').document(item_id)
    doc = doc_ref.get()
    if not doc.exists or 'featureVector' not in doc.to_dict():
        return []
    
    target_features = np.array(doc.to_dict()['featureVector'])
    
    # Search for similar items (excluding self)
    clothes_ref = db.collection('clothes')
    docs = clothes_ref.where('featureVector', '!=', None).stream()
    
    similarities = []
    for d in docs:
        if d.id == item_id:
            continue
        data = d.to_dict()
        db_features = np.array(data['featureVector'])
        similarity = np.dot(target_features, db_features) / (
            np.linalg.norm(target_features) * np.linalg.norm(db_features))
        similarities.append({
            'id': d.id,
            'similarity': similarity,
            #'data': data
        })
    
    return sorted(similarities, key=lambda x: x['similarity'], reverse=True)[:top_k]
