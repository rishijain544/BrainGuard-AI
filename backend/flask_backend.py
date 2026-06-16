import os
import io
import time
import base64
import logging
from typing import Dict, Any, List

from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image
import numpy as np
import cv2

# Import custom modules
from segmentation import TumorSegmenter, make_overlay

# ============================================================
# CONFIGURATION
# ============================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('flask_backend')

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, 'models')
PUBLIC_DIR = os.path.join(os.path.dirname(BASE_DIR), 'frontend', 'public')

CNN_MODEL_PATH = os.path.join(MODEL_PATH, 'cnn_best.pth')
RESNET_MODEL_PATH = os.path.join(MODEL_PATH, 'resnet_best.pth')
VIT_MODEL_PATH = os.path.join(MODEL_PATH, 'vit_best.pth')
SEGMENTATION_MODEL_PATH = os.path.join(MODEL_PATH, 'segmentation_model.pth')

DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

app = Flask(__name__)
# Enable CORS for all routes
CORS(app, resources={r"/*": {"origins": "*"}})

class ModelManager:
    def __init__(self):
        self.models: Dict[str, Any] = {}
        self.ready: bool = False

    def load_all(self):
        models_to_check = [
            ('cnn', CNN_MODEL_PATH),
            ('resnet', RESNET_MODEL_PATH),
            ('vit', VIT_MODEL_PATH),
            ('segmentation', SEGMENTATION_MODEL_PATH)
        ]
        
        loaded_names = []
        for name, path in models_to_check:
            if os.path.exists(path):
                loaded_names.append(name)
            else:
                logger.error(f"Missing model file: {path}")
        
        self.ready = len(loaded_names) == 4
        return loaded_names

model_manager = ModelManager()

# Define simple PyTorch models
class SimpleCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32, 64, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64, 128, kernel_size=3, padding=1), nn.ReLU(), nn.MaxPool2d(2)
        )
        self.classifier = nn.Sequential(
            nn.Linear(128 * 28 * 28, 512), nn.ReLU(), nn.Dropout(0.5), nn.Linear(512, 4)
        )
    def forward(self, x):
        x = self.features(x)
        x = x.view(x.size(0), -1)
        return self.classifier(x)

class SimpleViT(nn.Module):
    def __init__(self):
        super().__init__()
        import timm
        self.model = timm.create_model('vit_base_patch16_224', pretrained=False, num_classes=4)
    def forward(self, x):
        return self.model(x)

class EnsemblePredictor:
    def __init__(self, manager: ModelManager):
        self.manager = manager
        self.classes = ['glioma', 'meningioma', 'notumor', 'pituitary']
        
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

    def _build_arch(self, name: str, state_dict: dict) -> nn.Module:
        if name == 'cnn':
            return SimpleCNN()
        elif name == 'resnet':
            arch = models.resnet50(pretrained=False)
            arch.fc = nn.Linear(arch.fc.in_features, 4)
            return arch
        elif name == 'vit':
            return SimpleViT()
        raise ValueError(f"Unknown model architecture: {name}")

    def _load_one(self, name: str, path: str) -> nn.Module:
        if name in self.manager.models:
            return self.manager.models[name]
        state = torch.load(path, map_location=DEVICE, weights_only=False, mmap=True)
        if isinstance(state, dict) and 'model_state' in state:
            state = state['model_state']
        elif isinstance(state, dict) and 'state_dict' in state:
            state = state['state_dict']
        arch = self._build_arch(name, state)
        arch.load_state_dict(state, strict=False, assign=True)
        arch.to(DEVICE)
        arch.eval()
        self.manager.models[name] = arch
        return arch

    def predict(self, image: Image.Image) -> Dict[str, Any]:
        t_img = self.transform(image).unsqueeze(0).to(DEVICE)
        
        models_to_run = [
            ('cnn', CNN_MODEL_PATH),
            ('resnet', RESNET_MODEL_PATH),
            ('vit', VIT_MODEL_PATH)
        ]
        
        preds = []
        confidences = []
        
        for name, path in models_to_run:
            try:
                model = self._load_one(name, path)
                with torch.no_grad():
                    outputs = model(t_img)
                    probs = torch.nn.functional.softmax(outputs, dim=1)
                    conf = torch.max(probs).item()
                    pred = torch.argmax(probs).item()
                    
                    preds.append(self.classes[pred])
                    confidences.append(conf)
                del self.manager.models[name]
                del model
                import gc; gc.collect()
                import ctypes
                try: ctypes.CDLL('libc.so.6').malloc_trim(0)
                except: pass
            except Exception as e:
                logger.error(f"Failed to run {name}: {e}")

        if not preds:
            raise RuntimeError("All ensemble models failed")
            
        from collections import Counter
        final_pred = Counter(preds).most_common(1)[0][0]
        avg_conf = float(np.mean(confidences))
        
        return {
            "prediction": final_pred,
            "confidence": avg_conf * 100,
            "details": dict(zip([m[0] for m in models_to_run], zip(preds, confidences)))
        }

ensemble_predictor = EnsemblePredictor(model_manager)

def generate_heatmap(image: Image.Image, pred_class: str) -> str:
    try:
        model = ensemble_predictor._load_one('cnn', CNN_MODEL_PATH)
        t_img = ensemble_predictor.transform(image).unsqueeze(0).to(DEVICE)
        t_img.requires_grad = True
        
        outputs = model(t_img)
        class_idx = ensemble_predictor.classes.index(pred_class)
        
        model.zero_grad()
        outputs[0, class_idx].backward()
        
        gradients = t_img.grad.data.cpu().numpy()[0]
        activations = t_img.data.cpu().numpy()[0]
        
        weights = np.mean(gradients, axis=(1, 2))
        cam = np.zeros(activations.shape[1:], dtype=np.float32)
        for i, w in enumerate(weights):
            cam += w * activations[i]
            
        cam = np.maximum(cam, 0)
        if np.max(cam) > 0:
            cam = cam / np.max(cam)
            
        image_rgb = np.array(image)
        cam = cv2.resize(cam, (image_rgb.shape[1], image_rgb.shape[0]))
        
        del ensemble_predictor.manager.models['cnn']
        del model
        import gc; gc.collect()
        import ctypes
        try: ctypes.CDLL('libc.so.6').malloc_trim(0)
        except: pass
        
        return make_overlay(image_rgb, cam)
    except Exception as e:
        logger.error(f"Heatmap failed: {e}")
        return ""

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok",
        "models_loaded": model_manager.load_all(),
        "device": str(DEVICE)
    })

@app.route('/', methods=['GET'])
def root():
    return jsonify({"status": "ok", "message": "BrainGuard AI Flask Backend is running"})

@app.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400

    try:
        img_bytes = file.read()
        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        image_np = np.array(image)
        
        # 1. Ensemble Prediction
        result = ensemble_predictor.predict(image)
        tumor_type = result["prediction"]
        
        # 2. Grad-CAM Heatmap
        heatmap_b64 = generate_heatmap(image, tumor_type)
        
        # 3. Segmentation (only if tumor detected)
        mask_b64 = ""
        tumor_area = 0.0
        
        if tumor_type != "notumor":
            try:
                segmenter = TumorSegmenter(SEGMENTATION_MODEL_PATH, device=str(DEVICE))
                mask, area = segmenter.segment(image_np)
                
                mask_uint8 = (mask * 255).astype(np.uint8)
                mask_colored = cv2.applyColorMap(mask_uint8, cv2.COLORMAP_JET)
                
                # Make non-tumor areas transparent
                alpha = np.where(mask > 0.1, 150, 0).astype(np.uint8)
                rgba = cv2.cvtColor(mask_colored, cv2.COLOR_BGR2BGRA)
                rgba[:, :, 3] = alpha
                
                _, buffer = cv2.imencode('.png', rgba)
                mask_b64 = base64.b64encode(buffer).decode('utf-8')
                tumor_area = float(area)
                
                del segmenter
                import gc; gc.collect()
                import ctypes
                try: ctypes.CDLL('libc.so.6').malloc_trim(0)
                except: pass
            except Exception as e:
                logger.error(f"Segmentation failed: {e}")
                
        return jsonify({
            "status": "success",
            "prediction": tumor_type.capitalize(),
            "confidence": f"{result['confidence']:.1f}%",
            "tumor_area": f"{tumor_area:.1f}%" if tumor_area > 0 else "N/A",
            "heatmap": heatmap_b64,
            "mask": mask_b64,
            "details": result["details"]
        })
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    model_manager.load_all()
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 8080)))
