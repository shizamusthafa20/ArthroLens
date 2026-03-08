import gradio as gr
import json
import numpy as np
from PIL import Image
import tensorflow as tf

# Load insect database
with open('insects_db.json', 'r') as f:
    INSECTS_DB = json.load(f)

CLASS_NAMES = {
    0: "honeybee",
    1: "butterfly",
    2: "dragonfly",
    3: "scorpion",
    4: "house_spider"
}

# Load model
model = tf.keras.models.load_model('arthrolens_model.h5')

def identify_insect(image):
    # Preprocess
    img = Image.fromarray(image).resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    # Predict
    predictions = model.predict(img_array, verbose=0)
    predicted_idx = int(np.argmax(predictions[0]))
    confidence = round(float(np.max(predictions[0])) * 100, 1)
    predicted_class = CLASS_NAMES[predicted_idx]
    
    insect = INSECTS_DB[predicted_class]
    
    # Format output
    diseases = ", ".join(insect['diseases']) if insect['diseases'] else "None"
    precautions = "\n".join([f"• {p}" for p in insect['precautions']])
    
    result = f"""
# {insect['common_name']} 🔬
**Scientific Name:** *{insect['scientific_name']}*
**Taxonomy:** {insect['taxonomy']['order']} → {insect['taxonomy']['family']} → {insect['taxonomy']['genus']}
**Confidence:** {confidence}%

## ⚠️ Risk Level: {insect['risk_level']}
**Rarity:** {insect['rarity']}
**Active Season:** {insect['active_season']}
**Allergy Risk:** {insect['allergy_risk']}

## 🦠 Associated Diseases
{diseases}

## 🛡️ Precautions
{precautions}

## 🌍 Ecological Indicator
{insect['bioindicator']}

## 💡 Fun Fact
*{insect['fun_fact']}*

## ⚡ Immediate Action
{insect['immediate_action']}
"""
    return result

# Create Gradio interface
demo = gr.Interface(
    fn=identify_insect,
    inputs=gr.Image(label="Upload Insect Photo"),
    outputs=gr.Markdown(label="Identification Report"),
    title="🔬 ArthroLens",
    description="AI-Powered Arthropod Identification & Risk Intelligence Platform",
    examples=[],
    theme=gr.themes.Soft()
)

demo.launch()