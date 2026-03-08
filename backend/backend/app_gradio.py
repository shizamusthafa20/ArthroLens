import gradio as gr
import json
import numpy as np
from PIL import Image
import tensorflow as tf

with open('insects_db.json', 'r') as f:
    INSECTS_DB = json.load(f)

CLASS_NAMES = {
    0: "honeybee",
    1: "butterfly",
    2: "dragonfly",
    3: "scorpion",
    4: "house_spider"
}

model = tf.keras.models.load_model('arthrolens_model.h5')

RISK_EMOJI = {
    "High Risk": "🔴",
    "Caution": "🟡",
    "Safe": "🟢"
}

def identify_insect(image):
    img = Image.fromarray(image).resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    
    predictions = model.predict(img_array, verbose=0)
    predicted_idx = int(np.argmax(predictions[0]))
    confidence = round(float(np.max(predictions[0])) * 100, 1)
    predicted_class = CLASS_NAMES[predicted_idx]
    
    insect = INSECTS_DB[predicted_class]
    diseases = "\n".join([f"- 🦠 {d}" for d in insect['diseases']]) if insect['diseases'] else "- ✅ No known diseases"
    precautions = "\n".join([f"- ✅ {p}" for p in insect['precautions']])
    risk_emoji = RISK_EMOJI.get(insect['risk_level'], "⚪")
    
    result = f"""# 🔬 {insect['common_name']}

---

### 📋 Classification
| Field | Details |
|-------|---------|
| **Scientific Name** | *{insect['scientific_name']}* |
| **Order** | {insect['taxonomy']['order']} |
| **Family** | {insect['taxonomy']['family']} |
| **Genus** | {insect['taxonomy']['genus']} |
| **Confidence** | {confidence}% |
| **Rarity** | {insect['rarity']} |
| **Active Season** | {insect['active_season']} |
| **Invasive** | {'Yes ⚠️' if insect['invasive'] else 'No ✅'} |

---

### {risk_emoji} Risk Level: {insect['risk_level']}
**Allergy Risk:** {insect['allergy_risk']}

---

### 🦠 Associated Diseases
{diseases}

---

### 🛡️ Precautions
{precautions}

---

### ⚡ Immediate Action
> {insect['immediate_action']}

---

### 🌍 Ecological Indicator
> {insect['bioindicator']}

**Ecological Role:** {insect['ecological_role']}

---

### 💡 Fun Fact
> *{insect['fun_fact']}*
"""
    return result

demo = gr.Interface(
    fn=identify_insect,
    inputs=gr.Image(label="📷 Upload Insect Photo"),
    outputs=gr.Markdown(label="🔬 Identification Report"),
    title="🔬 ArthroLens",
    description="### AI-Powered Arthropod Identification & Risk Intelligence Platform\nUpload a photo of an insect to get instant biological and health risk analysis.",
    theme=gr.themes.Soft(),
    css="""
        .gradio-container {max-width: 1200px !important}
        h1 {color: #00ff88 !important}
    """
)

demo.launch()