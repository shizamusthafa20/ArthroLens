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

RISK_COLORS = {
    "High Risk":  {"bg": "#2d0a0a", "border": "#e53e3e", "badge_bg": "#e53e3e", "badge_text": "#fff"},
    "Caution":    {"bg": "#2d220a", "border": "#d97706", "badge_bg": "#d97706", "badge_text": "#fff"},
    "Safe":       {"bg": "#0a2d14", "border": "#38a169", "badge_bg": "#38a169", "badge_text": "#fff"},
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
    risk = insect['risk_level']
    colors = RISK_COLORS.get(risk, {"bg": "#1a1a2e", "border": "#666", "badge_bg": "#666", "badge_text": "#fff"})

    # Build disease tags
    disease_tags = ""
    if insect['diseases']:
        for d in insect['diseases']:
            disease_tags += f'<span class="tag">{d}</span>'
    else:
        disease_tags = '<span class="tag">No known diseases</span>'

    # Build precaution list
    precautions_html = ""
    for p in insect['precautions']:
        precautions_html += f'<li>✓ {p}</li>'

    # Taxonomy flowchart
    tax = insect['taxonomy']
    taxonomy_html = f"""
    <div class="tax-flow">
      <span class="tax-node">{tax['order']}</span>
      <span class="tax-arrow">→</span>
      <span class="tax-node">{tax['family']}</span>
      <span class="tax-arrow">→</span>
      <span class="tax-node">{tax['genus']}</span>
    </div>
    """

    invasive_badge = '<span class="inv-badge warn">⚠ Invasive</span>' if insect.get('invasive') else ''

    html = f"""
    <link href="https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Inter:wght@400;500&display=swap" rel="stylesheet">
    <style>
      .card {{
        background: {colors['bg']};
        border: 1.5px solid {colors['border']};
        border-radius: 14px;
        padding: 24px 28px;
        font-family: 'Inter', sans-serif;
        color: #e2e8f0;
        max-width: 620px;
        box-shadow: 0 0 32px {colors['border']}44;
      }}
      .card-header {{
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 6px;
      }}
      .risk-badge {{
        background: {colors['badge_bg']};
        color: {colors['badge_text']};
        font-family: 'Rajdhani', sans-serif;
        font-weight: 700;
        font-size: 13px;
        padding: 3px 12px;
        border-radius: 20px;
        letter-spacing: 0.5px;
      }}
      .confidence {{
        font-size: 13px;
        color: #94a3b8;
      }}
      .common-name {{
        font-family: 'Rajdhani', sans-serif;
        font-size: 32px;
        font-weight: 700;
        color: #f1f5f9;
        margin: 4px 0 2px 0;
        line-height: 1.1;
      }}
      .scientific-name {{
        font-style: italic;
        font-size: 14px;
        color: #94a3b8;
        margin-bottom: 8px;
      }}
      .tax-flow {{
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 18px;
        flex-wrap: wrap;
      }}
      .tax-node {{
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 6px;
        padding: 3px 10px;
        font-size: 12px;
        color: #cbd5e1;
        font-family: 'Inter', sans-serif;
      }}
      .tax-arrow {{
        color: #64748b;
        font-size: 14px;
      }}
      .meta-row {{
        display: flex;
        gap: 12px;
        margin-bottom: 18px;
        flex-wrap: wrap;
      }}
      .meta-box {{
        background: rgba(255,255,255,0.05);
        border-radius: 8px;
        padding: 8px 14px;
        flex: 1;
        min-width: 110px;
      }}
      .meta-label {{
        font-size: 10px;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #64748b;
        margin-bottom: 3px;
      }}
      .meta-value {{
        font-size: 14px;
        font-weight: 500;
        color: #e2e8f0;
      }}
      .section-title {{
        font-size: 13px;
        font-weight: 600;
        color: {colors['border']};
        margin: 16px 0 8px 0;
        display: flex;
        align-items: center;
        gap: 6px;
      }}
      .tags {{
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 4px;
      }}
      .tag {{
        background: rgba(255,255,255,0.07);
        border: 1px solid rgba(255,255,255,0.15);
        border-radius: 20px;
        padding: 4px 12px;
        font-size: 12px;
        color: #e2e8f0;
      }}
      .precautions {{
        list-style: none;
        padding: 0;
        margin: 0;
      }}
      .precautions li {{
        font-size: 13px;
        color: #cbd5e1;
        padding: 3px 0;
        padding-left: 4px;
      }}
      .info-box {{
        background: rgba(255,255,255,0.04);
        border-left: 3px solid {colors['border']};
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        font-size: 13px;
        color: #94a3b8;
        margin-top: 6px;
      }}
      .fun-fact {{
        background: rgba(255,255,255,0.04);
        border-left: 3px solid #f59e0b;
        border-radius: 0 8px 8px 0;
        padding: 10px 14px;
        font-size: 13px;
        color: #fcd34d;
        font-style: italic;
        margin-top: 6px;
      }}
      .inv-badge {{
        font-size: 11px;
        padding: 2px 8px;
        border-radius: 12px;
        margin-left: 8px;
      }}
      .inv-badge.warn {{
        background: #78350f;
        color: #fbbf24;
        border: 1px solid #92400e;
      }}
    </style>

    <div class="card">
      <div class="card-header">
        <span class="risk-badge">{risk}</span>
        <span class="confidence">Confidence: {confidence}%</span>
      </div>

      <div class="common-name">{insect['common_name']} {invasive_badge}</div>
      <div class="scientific-name">{insect['scientific_name']}</div>

      {taxonomy_html}

      <div class="meta-row">
        <div class="meta-box">
          <div class="meta-label">Rarity</div>
          <div class="meta-value">{insect['rarity']}</div>
        </div>
        <div class="meta-box">
          <div class="meta-label">Active Season</div>
          <div class="meta-value">{insect['active_season']}</div>
        </div>
        <div class="meta-box">
          <div class="meta-label">Allergy Risk</div>
          <div class="meta-value">{insect['allergy_risk']}</div>
        </div>
      </div>

      <div class="section-title">⚠️ Associated Diseases</div>
      <div class="tags">{disease_tags}</div>

      <div class="section-title">🛡️ Precautions</div>
      <ul class="precautions">{precautions_html}</ul>

      <div class="section-title">🌍 Ecological Indicator</div>
      <div class="info-box">{insect['bioindicator']}</div>

      <div class="section-title">💡 Fun Fact</div>
      <div class="fun-fact">{insect['fun_fact']}</div>
    </div>
    """
    return html


demo = gr.Interface(
    fn=identify_insect,
    inputs=gr.Image(label="Upload Insect Photo"),
    outputs=gr.HTML(label="Identification Report"),
    title="🔬 ArthroLens",
    description="### AI-Powered Arthropod Identification & Risk Intelligence\nUpload a photo of an arthropod for instant biological and health risk analysis.",
    theme=gr.themes.Soft(),
    css="""
        .gradio-container { max-width: 1200px !important; background: #0f1117 !important; }
        h1 { color: #00ff88 !important; }
        footer { display: none !important; }
    """
)

demo.launch()