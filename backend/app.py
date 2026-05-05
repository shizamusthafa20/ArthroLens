from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import json, os, io

from classifier import classifier, CLASS_NAMES
from gradcam import generate_gradcam_heatmap, overlay_heatmap_on_image, compute_density_score

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), 'insects_db.json')
with open(DB_PATH) as f:
    INSECTS_DB = json.load(f)
print(f'Loaded {len(INSECTS_DB)} insects from database')


@app.route('/api/identify', methods=['POST'])
def identify():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    file    = request.files['image']
    pil_img = Image.open(io.BytesIO(file.read())).convert('RGB')

    class_name, confidence, img_array, class_idx = classifier.predict(pil_img)

    gradcam_image = None
    density = {'level': 'Unknown', 'color': '#888', 'percentage': 0}

    if classifier.model:
        heatmap       = generate_gradcam_heatmap(classifier.model, img_array, class_idx)
        density       = compute_density_score(heatmap)
        gradcam_image = overlay_heatmap_on_image(pil_img, heatmap)

    insect_info = INSECTS_DB.get(class_name, {
        'common_name':     class_name.replace('_', ' ').title(),
        'scientific_name': 'Unknown',
        'risk_level':      'Unknown',
        'risk_color':      '#888888',
        'crop_impact':     {},
        'human_hazard':    {},
        'fun_fact':        'Data coming soon!'
    })

    density_key = density['level'].lower()
    crop_recs   = []
    if 'crop_impact' in insect_info:
        crop_recs = insect_info['crop_impact'].get(
            'recommendations', {}).get(density_key, [])

    return jsonify({
        'class_name':           class_name,
        'confidence':           round(confidence * 100, 2),
        'insect_info':          insect_info,
        'gradcam_image':        gradcam_image,
        'density':              density,
        'crop_recommendations': crop_recs
    })


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'classes': len(CLASS_NAMES)})


@app.route('/api/insects', methods=['GET'])
def get_all():
    return jsonify(INSECTS_DB)


if __name__ == '__main__':
    app.run(debug=True, port=5000)