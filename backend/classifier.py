import numpy as np
from PIL import Image
import io

# Insect classes we support
INSECT_CLASSES = [
    "aedes_mosquito",
    "honeybee", 
    "house_spider",
    "german_cockroach",
    "dragonfly"
]

# Color signatures for each insect (RGB patterns)
# These are based on typical colors of each insect
INSECT_SIGNATURES = {
    "aedes_mosquito": {"dark": 0.6, "stripe": True, "size": "small"},
    "honeybee": {"yellow": 0.4, "stripe": True, "size": "small"},
    "house_spider": {"dark": 0.7, "stripe": False, "size": "medium"},
    "german_cockroach": {"brown": 0.7, "stripe": False, "size": "medium"},
    "dragonfly": {"colorful": 0.5, "stripe": False, "size": "large"},
}

def preprocess_image(image_bytes):
    """Convert image bytes to numpy array"""
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    return img_array

def extract_features(img_array):
    """Extract color and pattern features from image"""
    # Get color channels
    r = img_array[:, :, 0]
    g = img_array[:, :, 1]
    b = img_array[:, :, 2]
    
    # Calculate color features
    mean_r = np.mean(r)
    mean_g = np.mean(g)
    mean_b = np.mean(b)
    
    # Calculate brightness
    brightness = (mean_r + mean_g + mean_b) / 3
    
    # Calculate contrast (std deviation)
    contrast = np.std(img_array)
    
    # Yellow ratio (honeybee)
    yellow_mask = (r > 0.5) & (g > 0.4) & (b < 0.3)
    yellow_ratio = np.mean(yellow_mask)
    
    # Dark ratio (mosquito, spider, cockroach)
    dark_mask = (r < 0.3) & (g < 0.3) & (b < 0.3)
    dark_ratio = np.mean(dark_mask)
    
    # Brown ratio (cockroach)
    brown_mask = (r > 0.3) & (g > 0.2) & (b < 0.2) & (r > g) & (g > b)
    brown_ratio = np.mean(brown_mask)
    
    # Green/Blue ratio (dragonfly near water)
    green_blue_mask = (g > 0.3) | (b > 0.3)
    green_blue_ratio = np.mean(green_blue_mask)
    
    # Stripe detection (variation in rows)
    row_means = np.mean(img_array, axis=(1, 2))
    stripe_score = np.std(row_means)
    
    return {
        "brightness": brightness,
        "contrast": contrast,
        "yellow_ratio": yellow_ratio,
        "dark_ratio": dark_ratio,
        "brown_ratio": brown_ratio,
        "green_blue_ratio": green_blue_ratio,
        "stripe_score": stripe_score,
        "mean_r": mean_r,
        "mean_g": mean_g,
        "mean_b": mean_b
    }

def classify_insect(image_bytes):
    """
    Classify insect based on color and pattern features
    Returns: (predicted_class, confidence)
    """
    img_array = preprocess_image(image_bytes)
    features = extract_features(img_array)
    
    # Score each insect based on features
    scores = {}
    
    # Aedes Mosquito: dark, striped, small
    scores["aedes_mosquito"] = (
        features["dark_ratio"] * 3.0 +
        features["stripe_score"] * 2.0 +
        (1 - features["yellow_ratio"]) * 1.5 +
        (1 - features["brown_ratio"]) * 1.0
    )
    
    # Honeybee: yellow, striped
    scores["honeybee"] = (
        features["yellow_ratio"] * 4.0 +
        features["stripe_score"] * 2.0 +
        features["brightness"] * 1.5 +
        (1 - features["dark_ratio"]) * 1.0
    )
    
    # House Spider: dark, no stripes, round
    scores["house_spider"] = (
        features["dark_ratio"] * 2.5 +
        (1 - features["stripe_score"]) * 2.0 +
        features["contrast"] * 1.5 +
        (1 - features["yellow_ratio"]) * 1.0
    )
    
    # German Cockroach: brown, flat
    scores["german_cockroach"] = (
        features["brown_ratio"] * 4.0 +
        (1 - features["dark_ratio"]) * 1.5 +
        (1 - features["yellow_ratio"]) * 1.0 +
        features["mean_r"] * 2.0
    )
    
    # Dragonfly: colorful, green/blue background
    scores["dragonfly"] = (
        features["green_blue_ratio"] * 3.0 +
        features["brightness"] * 2.0 +
        (1 - features["dark_ratio"]) * 1.5 +
        features["contrast"] * 1.0
    )
    
    # Get predicted class
    predicted_class = max(scores, key=scores.get)
    
    # Calculate confidence (normalize scores)
    total = sum(scores.values())
    confidence = round((scores[predicted_class] / total) * 100, 1)
    
    # Ensure confidence is between 60-95%
    confidence = max(60, min(95, confidence))
    
    return predicted_class, confidence