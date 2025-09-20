import os
import numpy as np
import tensorflow as tf
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
from io import BytesIO
import base64
from keras.applications.xception import preprocess_input

app = Flask(__name__)
# Enable CORS for all routes and all origins
CORS(app, resources={r"/*": {"origins": "*"}})

# Load model and class names once when the server starts
model = None
class_names = []

def load_model_and_classes():
    global model, class_names
    
    # IMPORTANT: Update these paths to your actual model and training data locations
    model_path = '/Volumes/PSSD T7/yj_dev/learn js/flask-api/h62_Xc_model.keras'  # <-- Update this
    #training_dir = 'path/to/your/dermnet/train'      # <-- Update this
    
    print(f"Loading model from: {model_path}")
    #print(f"Loading class names from: {training_dir}")
    
    try:
        # Get class names from directory structure
        if True:
            class_names = sorted([
                    'Acne and Rosacea Photos',
                    'Warts Molluscum and other Viral Infections',
                    'Light Diseases and Disorders of Pigmentation',
                    'Cellulitis Impetigo and other Bacterial Infections',
                    'Psoriasis pictures Lichen Planus and related diseases',
                    'Atopic Dermatitis Photos',
                    'Poison Ivy Photos and other Contact Dermatitis',
                    'Lupus and other Connective Tissue diseases',
                    'Hair Loss Photos Alopecia and other Hair Diseases',
                    'Tinea Ringworm Candidiasis and other Fungal Infections',
                    'Eczema Photos',
                    'Vascular Tumors',
                    'Actinic Keratosis Basal Cell Carcinoma and other Malignant Lesions',
                    'Vasculitis Photos',
                    'Melanoma Skin Cancer Nevi and Moles',
                    'Nail Fungus and other Nail Disease',
                    'Seborrheic Keratoses and other Benign Tumors',
                    'Bullous Disease Photos',
                    'Exanthems and Drug Eruptions',
                    'Herpes HPV and other STDs Photos',
                    'Urticaria Hives',
                    'Systemic Disease',
                    'Scabies Lyme Disease and other Infestations and Bites'
                    ])
            print(f"Found {len(class_names)} classes")
        else:
            # If directory doesn't exist, use a placeholder list of classes
            # You should replace this with your actual classes when possible
            print(f"Warning: Training directory not found. Using placeholder class names")
            class_names = ["Class1", "Class2", "Class3", "Class4", "Class5"]
        
        # Load the model
        model = tf.keras.models.load_model(model_path, 
                                         custom_objects={'preprocess_input': preprocess_input})
        print("Model loaded successfully")
        
    except Exception as e:
        print(f"ERROR loading model or classes: {e}")
        # In a real app, you might want to exit here if the model can't be loaded
        # For testing, we'll continue and let the /predict endpoint handle the error

@app.route('/predict', methods=['POST'])
def predict():
    if model is None:
        return jsonify({"error": "Model not loaded. Check server logs for details."}), 500
    
    if 'image' not in request.files and 'image_base64' not in request.json:
        return jsonify({"error": "No image provided. Send either a file upload or base64 image"}), 400
    
    try:
        if 'image' in request.files:
            # Handle file upload
            file = request.files['image']
            print(f"Received image file: {file.filename}")
            img = Image.open(file.stream).convert("RGB")
        else:
            # Handle base64 image
            base64_image = request.json['image_base64']
            img_data = base64.b64decode(base64_image.split(',')[1] if ',' in base64_image else base64_image)
            img = Image.open(BytesIO(img_data)).convert("RGB")
            print("Received base64 image")
        
        # Resize and preprocess
        target_size = (299, 299)  # Xception model input size
        img = img.resize(target_size)
        img_array = np.array(img)
        processed_img = np.expand_dims(img_array, axis=0)
        
        # Predict
        print("Running prediction...")
        predictions = model.predict(processed_img, verbose=0)
        
        # Get top 3 predictions
        top_indices = np.argsort(predictions[0])[::-1][:3]
        result = []
        
        for i in top_indices:
            result.append({
                "class": class_names[i],
                "confidence": float(predictions[0][i])
            })
        
        response_data = {
            "top_prediction": {
                "class": class_names[np.argmax(predictions[0])],
                "confidence": float(predictions[0][np.argmax(predictions[0])])
            },
            "top_3_predictions": result
        }
        
        print(f"Prediction results: {response_data}")
        return jsonify(response_data)
        
    except Exception as e:
        print(f"Error during prediction: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Simple endpoint to check if the server is running"""
    status = "ok" if model is not None else "model not loaded"
    return jsonify({
        "status": status,
        "classes_loaded": len(class_names)
    })

if __name__ == "__main__":
    print("Starting Flask ML API server...")
    load_model_and_classes()
    app.run(debug=True, host='0.0.0.0', port=5001)