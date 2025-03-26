import numpy as np
from tensorflow.keras.applications import ResNet50
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing import image

# Load model (outside function to load only once)
model = ResNet50(weights='imagenet', include_top=False, pooling='avg')

def extract_features(img_path):
    """Extract features from image using ResNet50 with error handling"""
    try:
        img = image.load_img(img_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        features = model.predict(x)
        return features.flatten()
    except Exception as e:
        print(f"Error processing image {img_path}: {str(e)}")
        return None
