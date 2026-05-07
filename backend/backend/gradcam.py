import numpy as np
import cv2
import tensorflow as tf
import base64
from PIL import Image
from io import BytesIO


def get_last_conv_layer(model):
    for layer in reversed(model.layers):
        if isinstance(layer, (tf.keras.layers.Conv2D,
                              tf.keras.layers.DepthwiseConv2D)):
            return layer.name
    raise ValueError('No conv layer found!')


def generate_gradcam_heatmap(model, img_array, class_idx, layer_name=None):
    if layer_name is None:
        layer_name = get_last_conv_layer(model)

    print(f"[GradCAM] Using layer: {layer_name}")

    # ✅ FIX: explicitly get single output tensor, not a list
    conv_layer_output = model.get_layer(layer_name).output
    model_output = model.output
    if isinstance(model_output, list):
        model_output = model_output[-1]  # take final output tensor

    grad_model = tf.keras.Model(
        inputs=model.inputs,
        outputs=[conv_layer_output, model_output]
    )

    img_tensor = tf.cast(img_array, tf.float32)

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_tensor, training=False)
        tape.watch(conv_outputs)

        if not isinstance(predictions, tf.Tensor):
            predictions = tf.convert_to_tensor(predictions)

        num_classes = int(predictions.shape[-1])
        safe_idx = min(int(class_idx), num_classes - 1)
        # ✅ FIX: slice with Python int, not tf.constant
        loss = predictions[0][safe_idx]

    grads = tape.gradient(loss, conv_outputs)

    if grads is None:
        raise ValueError("Gradients are None")

    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    heatmap = conv_outputs[0] @ pooled_grads[..., tf.newaxis]
    heatmap = tf.squeeze(heatmap)
    heatmap = tf.nn.relu(heatmap).numpy()

    # ensure it's 2D
    if heatmap.ndim == 0:
        heatmap = np.ones((7, 7), dtype=np.float32)
    
    if heatmap.max() > 0:
        heatmap /= heatmap.max()

    print(f"[GradCAM] Heatmap shape: {heatmap.shape}, max: {heatmap.max():.4f}")
    return heatmap


def compute_density_score(heatmap):
    active_pixels = np.sum(heatmap > 0.3)  # lowered threshold from 0.5 → 0.3
    total_pixels  = heatmap.size
    pct = round((active_pixels / total_pixels) * 100, 1)

    if pct < 15:
        return {'level': 'Low',    'color': '#33CC33', 'percentage': pct}
    elif pct < 40:
        return {'level': 'Medium', 'color': '#FFA500', 'percentage': pct}
    else:
        return {'level': 'High',   'color': '#FF3333', 'percentage': pct}


def overlay_heatmap_on_image(original_pil_img, heatmap, alpha=0.55):
    img = original_pil_img.convert('RGB').resize((224, 224))
    img_np = np.array(img)

    heatmap_resized = cv2.resize(heatmap, (224, 224))
    
    # ✅ FIX: boost contrast before applying colormap
    heatmap_resized = np.power(heatmap_resized, 0.5)  # gamma correction
    heatmap_uint8   = np.uint8(255 * heatmap_resized)
    heatmap_colored = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
    heatmap_colored = cv2.cvtColor(heatmap_colored, cv2.COLOR_BGR2RGB)

    overlay = (img_np * (1 - alpha) + heatmap_colored * alpha).astype(np.uint8)

    result_img = Image.fromarray(overlay)
    buffer = BytesIO()
    result_img.save(buffer, format='PNG')
    b64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
    return f'data:image/png;base64,{b64}'


def run_gradcam(model, img_array, class_idx, original_pil_img):
    try:
        heatmap  = generate_gradcam_heatmap(model, img_array, class_idx)
        density  = compute_density_score(heatmap)
        overlay  = overlay_heatmap_on_image(original_pil_img, heatmap)
        return overlay, density
    except Exception as e:
        print(f'Grad-CAM error: {e}')
        import traceback
        traceback.print_exc()
        return None, {'level': 'Unknown', 'color': '#888', 'percentage': 0}