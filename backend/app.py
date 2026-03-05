from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import numpy as np
from PIL import Image
import io
import base64

app = Flask(__name__)
CORS(app)

# Load insect database
with open('insects_db.json', 'r') as f:
    INSECTS_DB = json.load(f)

INSECT_CLASSES = list(INSECTS_DB.keys())

def simulate_classification(image_bytes):
    # Review 1: Simulated prediction
    # Final Review: Replace with real TensorFlow model
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img_array = np.array(img)
    
    # Picks insect based on image pixel values
    pixel_sum = int(img_array.sum()) % len(INSECT_CLASSES)
    predicted_class = INSECT_CLASSES[pixel_sum]
    confidence = round(72 + (int(img_array.mean()) % 25), 1)
    
    return predicted_class, confidence

@app.route('/api/identify', methods=['POST'])
def identify_insect():
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    image_bytes = file.read()
    
    predicted_class, confidence = simulate_classification(image_bytes)
    insect_data = INSECTS_DB[predicted_class]
    
    img_b64 = base64.b64encode(image_bytes).decode('utf-8')
    
    return jsonify({
        'success': True,
        'prediction': {
            'class_id': predicted_class,
            'confidence': confidence
        },
        'insect_info': insect_data,
        'image_b64': img_b64
    })

@app.route('/api/insects', methods=['GET'])
def get_all_insects():
    return jsonify(INSECTS_DB)

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ArthroLens API running!'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)