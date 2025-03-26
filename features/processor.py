import time
from tqdm import tqdm
import os
from firebase.config import initialize_firebase
from firebase.utils import download_image
from features.extractor import extract_features

def process_images_in_batches(batch_size=20, max_docs=None):
    """Process clothing images in manageable batches with comprehensive error handling"""
    db, bucket = initialize_firebase()
    clothes_ref = db.collection('clothes')
    total_count = len(list(clothes_ref.limit(max_docs).get())) if max_docs else len(list(clothes_ref.get()))
    
    processed_count = 0
    skipped_count = 0
    error_count = 0
    
    # Get initial batch
    docs = clothes_ref.limit(batch_size).stream()
    
    with tqdm(total=total_count, desc="Processing images") as pbar:
        while True:
            batch = db.batch()
            batch_count = 0
            
            for doc in docs:
                data = doc.to_dict()
                if 'clotheImageUrlsArray' in data and len(data['clotheImageUrlsArray']) > 0:
                    img_url = data['clotheImageUrlsArray'][0]
                    img_path = download_image(img_url, bucket)
                    
                    if img_path:
                        features = extract_features(img_path)
                        if features is not None:
                            try:
                                batch.update(doc.reference, {'featureVector': features.tolist()})
                                batch_count += 1
                                processed_count += 1
                            except Exception as e:
                                print(f"Error updating document {doc.id}: {str(e)}")
                                error_count += 1
                        else:
                            error_count += 1
                        # Clean up temporary file
                        try:
                            os.unlink(img_path)
                        except:
                            pass
                    else:
                        skipped_count += 1
                else:
                    skipped_count += 1
                
                pbar.update(1)
                
                if max_docs and processed_count + skipped_count + error_count >= max_docs:
                    break
            
            # Commit the batch if it has any updates
            if batch_count > 0:
                try:
                    batch.commit()
                    print(f"\nCommitted batch of {batch_count} updates")
                except Exception as e:
                    print(f"\nError committing batch: {str(e)}")
                    error_count += batch_count
            
            # Break conditions
            if batch_count == 0 or (max_docs and processed_count + skipped_count + error_count >= max_docs):
                break
            
            # Get next batch using pagination
            try:
                last_doc = list(clothes_ref.limit(processed_count + skipped_count + error_count).get())[-1]
                docs = clothes_ref.start_after(last_doc).limit(batch_size).stream()
            except Exception as e:
                print(f"Error getting next batch: {str(e)}")
                break
            
            # Add delay to avoid quota limits
            time.sleep(1)
    
    print(f"\nProcessing complete:")
    print(f"- Successfully processed: {processed_count}")
    print(f"- Skipped (no image): {skipped_count}")
    print(f"- Errors: {error_count}")
