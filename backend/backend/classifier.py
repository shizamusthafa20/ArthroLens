import numpy as np
from PIL import Image
import json
import os
import tensorflow as tf
from tensorflow.keras.applications.efficientnet import preprocess_input

BASE_DIR       = os.path.dirname(__file__)
MODEL_KERAS    = os.path.join(BASE_DIR, 'arthrolens_model_v2.keras')
MODEL_PATH_H5  = os.path.join(BASE_DIR, 'arthrolens_model_v2.h5')
MODEL_TFLITE   = os.path.join(BASE_DIR, 'arthrolens_model_v2.tflite')
CLASS_JSON     = os.path.join(BASE_DIR, 'class_names.json')
IMG_SIZE       = 224

with open(CLASS_JSON) as f:
    CLASS_NAMES = json.load(f)
print(f'Loaded {len(CLASS_NAMES)} class names')


class InsectClassifier:
    def __init__(self):
        self.model       = None
        self.interpreter = None
        self.use_tflite  = False
        self._load()

    def _load(self):
        if os.path.exists(MODEL_KERAS):
            print('Loading Keras model...')
            self.model = tf.keras.models.load_model(MODEL_KERAS)
            print('Model loaded!')
        elif os.path.exists(MODEL_PATH_H5):
            print('Loading H5 model...')
            self.model = tf.keras.models.load_model(MODEL_PATH_H5)
            print('Model loaded!')
        elif os.path.exists(MODEL_TFLITE):
            print('Loading TFLite model...')
            self.interpreter = tf.lite.Interpreter(model_path=MODEL_TFLITE)
            self.interpreter.allocate_tensors()
            self.use_tflite = True
        else:
            print('WARNING: No model found!')

    def preprocess(self, pil_img):
        img = pil_img.convert('RGB').resize((IMG_SIZE, IMG_SIZE))
        arr = np.array(img, dtype=np.float32)
        arr = preprocess_input(arr)
        return np.expand_dims(arr, axis=0)

    def predict(self, pil_img):
        img_array = self.preprocess(pil_img)

        if self.use_tflite:
            inp = self.interpreter.get_input_details()
            out = self.interpreter.get_output_details()
            self.interpreter.set_tensor(inp[0]['index'], img_array)
            self.interpreter.invoke()
            preds = self.interpreter.get_tensor(out[0]['index'])[0]
        elif self.model:
            preds = self.model.predict(img_array, verbose=0)[0]
        else:
            return 'unknown', 0.0, None, 0

        class_idx  = int(np.argmax(preds))
        confidence = float(preds[class_idx])
        class_name = CLASS_NAMES[class_idx]
        return class_name, confidence, img_array, class_idx


classifier = InsectClassifier()