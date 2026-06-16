# ============================================================
#  BrainGuard AI — FastAPI Backend (COMPLETE FIXED VERSION)
#  Brain Tumor Detection API with Ensemble Inference
# ============================================================

import os
import io
import time
import logging
import base64
from datetime import datetime
from typing import List, Optional, Dict

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from PIL import Image
from torchvision import models

from segmentation import TumorSegmenter, visualize_segmentation

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel

# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# CONFIGURATION — paths always relative to THIS file
# ============================================================

# This is D:\brain_tumour_prediction\backend\
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PUBLIC_DIR = os.path.join(os.path.dirname(BASE_DIR), 'frontend', 'public')

# Models folder is INSIDE backend/models/
MODEL_PATH        = os.path.join(BASE_DIR, 'models')
CNN_MODEL_PATH    = os.path.join(MODEL_PATH, 'cnn_best.pth')
RESNET_MODEL_PATH = os.path.join(MODEL_PATH, 'resnet_best.pth')
VIT_MODEL_PATH    = os.path.join(MODEL_PATH, 'vit_best.pth')
SEGMENTATION_MODEL_PATH = os.path.join(MODEL_PATH, 'segmentation_model.pth')

# Print paths so we can verify at startup
logger.info(f"BASE_DIR          : {BASE_DIR}")
logger.info(f"MODEL_PATH        : {MODEL_PATH}")
logger.info(f"CNN exists        : {os.path.exists(CNN_MODEL_PATH)}")
logger.info(f"ResNet exists     : {os.path.exists(RESNET_MODEL_PATH)}")
logger.info(f"ViT exists        : {os.path.exists(VIT_MODEL_PATH)}")

DEVICE      = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
CLASS_NAMES = ['glioma', 'meningioma', 'notumor', 'pituitary']
MEAN        = [0.18,  0.18,  0.18]
STD         = [0.177, 0.177, 0.177]

logger.info(f"Using device: {DEVICE}")

# ============================================================
# MODEL ARCHITECTURES  (must exactly match training code)
# ============================================================

class BaseCNN(nn.Module):
    def __init__(self, num_classes=4):
        super().__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3,   32,  3, padding=1), nn.BatchNorm2d(32),  nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(32,  64,  3, padding=1), nn.BatchNorm2d(64),  nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(64,  128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(128, 256, 3, padding=1), nn.BatchNorm2d(256), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(256, 512, 3, padding=1), nn.BatchNorm2d(512), nn.ReLU(), nn.MaxPool2d(2),
        )
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d(1), nn.Flatten(),
            nn.Linear(512, 256), nn.ReLU(), nn.Dropout(0.5),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        return self.classifier(self.features(x))


class ResNet50Transfer(nn.Module):
    def __init__(self, num_classes=4):
        super().__init__()
        self.model = models.resnet50(weights=None)
        self.model.fc = nn.Sequential(
            nn.Linear(2048, 512), nn.ReLU(), nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        return self.model(x)


class HybridResNetViT(nn.Module):
    def __init__(self, num_classes=4, embed_dim=384, num_heads=6, num_blocks=4):
        super().__init__()
        from timm.models.vision_transformer import Block

        resnet = models.resnet50(weights=None)
        self.backbone = nn.Sequential(
            resnet.conv1, resnet.bn1, resnet.relu, resnet.maxpool,
            resnet.layer1, resnet.layer2, resnet.layer3
        )
        self.patch_proj = nn.Conv2d(1024, embed_dim, kernel_size=1)
        num_patches     = 14 * 14
        self.cls_token  = nn.Parameter(torch.zeros(1, 1, embed_dim))
        self.pos_embed  = nn.Parameter(torch.zeros(1, num_patches + 1, embed_dim))
        nn.init.trunc_normal_(self.cls_token, std=0.02)
        nn.init.trunc_normal_(self.pos_embed, std=0.02)
        self.blocks = nn.ModuleList([
            Block(dim=embed_dim, num_heads=num_heads, mlp_ratio=4.0, qkv_bias=True)
            for _ in range(num_blocks)
        ])
        self.norm    = nn.LayerNorm(embed_dim)
        self.dropout = nn.Dropout(0.1)
        self.head    = nn.Linear(embed_dim, num_classes)

    def forward(self, x):
        B   = x.shape[0]
        x   = self.backbone(x)
        x   = self.patch_proj(x)
        x   = x.flatten(2).transpose(1, 2)
        cls = self.cls_token.expand(B, -1, -1)
        x   = torch.cat([cls, x], dim=1)
        x   = self.dropout(x + self.pos_embed)
        for block in self.blocks:
            x = block(x)
        x = self.norm(x[:, 0])
        return self.head(x)


# ============================================================
# AUTO-DETECT VIT PARAMS FROM CHECKPOINT
# ============================================================

def detect_vit_params(state: dict) -> dict:
    """Read checkpoint → return correct embed_dim / num_heads / num_blocks."""
    cls  = state.get('cls_token')   # shape (1, 1, embed_dim)
    embed_dim  = int(cls.shape[2]) if cls is not None else 384
    num_heads  = embed_dim // 64   # 64 dims per head (standard)
    block_idxs = set()
    for k in state.keys():
        if k.startswith('blocks.'):
            part = k.split('.')[1]
            if part.isdigit():
                block_idxs.add(int(part))
    num_blocks = len(block_idxs) if block_idxs else 4
    logger.info(f"ViT auto-detected: embed_dim={embed_dim}, num_heads={num_heads}, num_blocks={num_blocks}")
    return dict(embed_dim=embed_dim, num_heads=num_heads, num_blocks=num_blocks)


# ============================================================
# GRAD-CAM
# ============================================================

class GradCAM:
    def __init__(self, model, target_layer):
        self.model       = model
        self.gradients   = None
        self.activations = None
        target_layer.register_forward_hook(self._save_activation)
        target_layer.register_backward_hook(self._save_gradient)

    def _save_activation(self, module, inp, out):
        self.activations = out.detach()

    def _save_gradient(self, module, grad_in, grad_out):
        self.gradients = grad_out[0].detach()

    def generate(self, tensor: torch.Tensor, class_idx: int) -> np.ndarray:
        self.model.eval()
        logits = self.model(tensor)
        self.model.zero_grad()
        logits[0, class_idx].backward()
        weights = self.gradients[0].mean(dim=(1, 2))
        cam     = (weights[:, None, None] * self.activations[0]).sum(0)
        cam     = F.relu(cam)
        cam_np  = cam.cpu().numpy()
        cam_np  = (cam_np - cam_np.min()) / (cam_np.max() - cam_np.min() + 1e-8)
        cam_np  = cv2.resize(cam_np, (224, 224))
        return cam_np


def make_overlay(image_rgb: np.ndarray, cam: np.ndarray, alpha: float = 0.45) -> str:
    heatmap = cv2.applyColorMap((cam * 255).astype(np.uint8), cv2.COLORMAP_JET)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    img_u8  = image_rgb.astype(np.uint8)
    overlay = cv2.addWeighted(img_u8, 1 - alpha, heatmap, alpha, 0)
    pil_img = Image.fromarray(overlay)
    buf     = io.BytesIO()
    pil_img.save(buf, format='PNG')
    b64     = base64.b64encode(buf.getvalue()).decode('utf-8')
    return f"data:image/png;base64,{b64}"


# ============================================================
# PREPROCESSING
# ============================================================

def preprocess_image_standard(img: Image.Image) -> torch.Tensor:
    arr   = np.array(img)
    arr_r = cv2.resize(arr, (224, 224))
    t     = torch.from_numpy(arr_r).permute(2, 0, 1).float() / 255.0
    mean  = torch.tensor(MEAN).view(3, 1, 1)
    std   = torch.tensor(STD ).view(3, 1, 1)
    t     = (t - mean) / std
    t     = t.unsqueeze(0).to(DEVICE)
    return t

def preprocess_image_notebook(img: Image.Image) -> torch.Tensor:
    img_resized = img.resize((224, 224), Image.BILINEAR)
    pixels = list(img_resized.getdata())
    t = torch.tensor(pixels, dtype=torch.float32).reshape(3, 224, 224) / 255.0
    mean  = torch.tensor(MEAN).view(3, 1, 1)
    std   = torch.tensor(STD ).view(3, 1, 1)
    t     = (t - mean) / std
    t     = t.unsqueeze(0).to(DEVICE)
    return t


# ============================================================
# RESPONSE SCHEMAS
# ============================================================

class ModelPrediction(BaseModel):
    class_name:    str
    class_index:   int
    confidence:    float
    probabilities: Dict[str, float]


class PredictionResponse(BaseModel):
    timestamp:              str
    filename:               str
    ensemble_prediction:    str
    ensemble_confidence:    float
    cnn_prediction:         ModelPrediction
    resnet_prediction:      ModelPrediction
    vit_prediction:         ModelPrediction
    class_probabilities:    Dict[str, float]
    model_agreement:        float
    uncertainty:            float
    gradcam_overlay_base64: str
    segmentation_overlay_base64: str
    recommendation:         str
    confidence_level:       str
    suggested_action:       str


class HealthResponse(BaseModel):
    status:        str
    models_loaded: List[str]
    device:        str
    timestamp:     str
    errors:        Optional[Dict[str, str]] = None


# ============================================================
# MODEL MANAGER
# ============================================================

class ModelManager:

    def __init__(self):
        self.models    : Dict[str, nn.Module] = {}
        self.load_time : Dict[str, str]       = {}
        self.errors    : Dict[str, str]       = {}
        self.segmenter : Optional[TumorSegmenter] = None

    def load_all(self):
        # Load all models eagerly at startup (HF Spaces has 16GB RAM)
        models_to_load = [
            ('cnn', CNN_MODEL_PATH),
            ('resnet', RESNET_MODEL_PATH),
            ('vit', VIT_MODEL_PATH)
        ]
            
        for name, path in models_to_load:
            try:
                self._load_one(name, path)
            except Exception as e:
                logger.warning(f"Could not load {name}: {e}")
                self.errors[name] = str(e)
                
        try:
            logger.info(f"Loading segmentation from {SEGMENTATION_MODEL_PATH} ...")
            t0 = time.time()
            self.segmenter = TumorSegmenter(SEGMENTATION_MODEL_PATH, device=str(DEVICE))
            self.load_time['segmentation'] = f"{time.time()-t0:.2f}s"
        except Exception as e:
            logger.warning(f"Could not load segmentation model: {e}")
            self.errors['segmentation'] = str(e)
            
        return list(self.models.keys())

    def get(self, name: str) -> nn.Module:
        if name not in self.models:
            raise RuntimeError(f"Model '{name}' not loaded")
        return self.models[name]

    @property
    def ready(self) -> bool:
        return len(self.models) >= 1

    def _load_one(self, name: str, path: str):
        logger.info(f"Loading {name} from {path} ...")

        if not os.path.exists(path):
            raise FileNotFoundError(f"Not found: {path}")

        # Use memory mapping to avoid RAM spikes on free tiers
        ckpt = torch.load(path, map_location=DEVICE, weights_only=False, mmap=True)

        # Handle all possible save formats
        if isinstance(ckpt, dict):
            if 'model_state' in ckpt:
                state = ckpt['model_state']
                logger.info(f"  key='model_state'")
            elif 'state_dict' in ckpt:
                state = ckpt['state_dict']
                logger.info(f"  key='state_dict'")
            elif 'model' in ckpt:
                state = ckpt['model']
                logger.info(f"  key='model'")
            else:
                state = ckpt
                logger.info(f"  dict IS the state_dict")
        else:
            state = ckpt
            logger.info(f"  direct state_dict")

        arch = self._build_arch(name, state)
        arch.load_state_dict(state, strict=False)
        arch.to(DEVICE)
        arch.eval()

        if name in ['resnet', 'vit']:
            for param in arch.parameters():
                param.requires_grad = False

        self.models[name]    = arch
        self.load_time[name] = datetime.now().isoformat()
        logger.info(f"✓ {name} loaded successfully")

    @staticmethod
    def _build_arch(name: str, state: dict = None) -> nn.Module:
        if name == 'cnn':
            return BaseCNN(num_classes=4)
        if name == 'resnet':
            return ResNet50Transfer(num_classes=4)
        if name == 'vit':
            params = detect_vit_params(state) if state is not None else {}
            return HybridResNetViT(num_classes=4, **params)
        raise ValueError(f"Unknown architecture: {name}")


# ============================================================
# ENSEMBLE PREDICTOR
# ============================================================

class EnsemblePredictor:

    def __init__(self, manager: ModelManager):
        self.manager = manager

    def predict(self, tensors: Dict[str, torch.Tensor]) -> dict:
        individual = {}
        probs_list = []

        for name in self.manager.models.keys():
            model = self.manager.get(name)
            tensor = tensors['notebook'] if name == 'cnn' else tensors['standard']
            with torch.no_grad():
                logits = model(tensor)
                probs  = torch.softmax(logits, dim=1)[0].cpu().numpy()
            probs_list.append(probs)
            idx = int(probs.argmax())
            individual[name] = {
                'class_name':    CLASS_NAMES[idx],
                'class_index':   idx,
                'confidence':    float(probs[idx]),
                'probabilities': {CLASS_NAMES[i]: float(probs[i]) for i in range(4)},
            }

        # Fill missing models with zeros so response schema is always valid
        for name in ('cnn', 'resnet', 'vit'):
            if name not in individual:
                individual[name] = {
                    'class_name':    'unavailable',
                    'class_index':   0,
                    'confidence':    0.0,
                    'probabilities': {c: 0.0 for c in CLASS_NAMES},
                }

        arr       = np.array(probs_list)
        ens_probs = arr.mean(axis=0)
        ens_idx   = int(ens_probs.argmax())
        ens_conf  = float(ens_probs[ens_idx])
        agreement = float(1.0 - arr[:, ens_idx].std()) if len(arr) > 1 else 1.0

        return {
            'individual':          individual,
            'ensemble_class':      ens_idx,
            'ensemble_class_name': CLASS_NAMES[ens_idx],
            'ensemble_confidence': ens_conf,
            'ensemble_probs':      {CLASS_NAMES[i]: float(ens_probs[i]) for i in range(4)},
            'model_agreement':     agreement,
        }


# ============================================================
# GRAD-CAM HELPER
# ============================================================

def compute_gradcam(manager: ModelManager,
                    tensors: Dict[str, torch.Tensor],
                    image_rgb: np.ndarray,
                    class_idx: int) -> str:
    try:
        model = manager.get('cnn')
        target_layer = None
        for m in reversed(list(model.features.children())):
            if isinstance(m, nn.Conv2d):
                target_layer = m
                break
        gc  = GradCAM(model, target_layer)
        tensor = tensors['notebook']
        cam = gc.generate(tensor.clone().requires_grad_(True), class_idx)
        return make_overlay(image_rgb, cam)
    except Exception as e:
        logger.warning(f"CNN Grad-CAM failed: {e}")

    try:
        model = manager.get('resnet')
        target_layer = model.model.layer4[-1].conv3
        gc  = GradCAM(model, target_layer)
        tensor = tensors['standard']
        cam = gc.generate(tensor.clone().requires_grad_(True), class_idx)
        return make_overlay(image_rgb, cam)
    except Exception as e:
        logger.warning(f"ResNet Grad-CAM failed: {e}")

    return "data:image/png;base64,"


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title       = "BrainGuard AI - Brain Tumor Detection API",
    version     = "1.0.0",
    description = "AI-powered brain tumor classification with Grad-CAM explainability"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins     = ["*"],
    allow_credentials = True,
    allow_methods     = ["*"],
    allow_headers     = ["*"],
)

model_manager      = ModelManager()
ensemble_predictor = EnsemblePredictor(model_manager)


@app.on_event('startup')
async def startup():
    logger.info("=" * 60)
    logger.info("BrainGuard AI API starting ...")
    logger.info(f"Models directory: {MODEL_PATH}")
    loaded = model_manager.load_all()
    logger.info(f"Loaded models: {loaded}")
    if not loaded:
        logger.error("NO MODELS LOADED — check your models/ folder!")
    logger.info("=" * 60)


@app.on_event('shutdown')
async def shutdown():
    logger.info("Shutting down.")


@app.get('/health', response_model=HealthResponse)
async def health():
    return HealthResponse(
        status        = 'ok' if model_manager.ready else 'no_models',
        models_loaded = list(model_manager.models.keys()),
        device        = str(DEVICE),
        timestamp     = datetime.now().isoformat(),
        errors        = model_manager.errors
    )


@app.post('/predict', response_model=PredictionResponse)
async def predict(file: UploadFile = File(...)):
    t0 = time.time()

    if not model_manager.ready:
        raise HTTPException(503, f"No models loaded. Check {MODEL_PATH}")

    content = await file.read()
    if not content:
        raise HTTPException(422, "Uploaded file is empty")

    try:
        img_pil = Image.open(io.BytesIO(content)).convert('RGB')
            
        tensor_std = preprocess_image_standard(img_pil)
        tensor_nb = preprocess_image_notebook(img_pil)
        tensors = {
            'standard': tensor_std,
            'notebook': tensor_nb
        }
        img_rgb = cv2.resize(np.array(img_pil), (224, 224))
    except Exception as e:
        raise HTTPException(422, f"Cannot read image: {e}")

    result      = ensemble_predictor.predict(tensors)
    gradcam_b64 = compute_gradcam(model_manager, tensors, img_rgb, result['ensemble_class'])
    
    # Generate segmentation overlay
    seg_b64 = ""
    if model_manager.segmenter is not None:
        try:
            mask, contours, conf = model_manager.segmenter.segment_with_contours(img_rgb)
            overlay_img = visualize_segmentation(img_rgb, mask, contours)
            is_success, buffer = cv2.imencode(".png", cv2.cvtColor(overlay_img, cv2.COLOR_RGB2BGR))
            if is_success:
                seg_b64 = f"data:image/png;base64,{base64.b64encode(buffer).decode('utf-8')}"
        except Exception as e:
            logger.warning(f"Segmentation failed: {e}")

    p         = np.array(list(result['ensemble_probs'].values()))
    entropy   = float(-np.sum(p * np.log(p + 1e-10)) / np.log(4))

    conf      = result['ensemble_confidence']
    pred_name = result['ensemble_class_name'].upper()
    is_tumor  = result['ensemble_class_name'] != 'notumor'

    if conf > 0.90:
        conf_level = 'high'
        action = f"Proceed with clinical protocols for {pred_name}." if is_tumor else "No tumor detected with high confidence."
    elif conf > 0.70:
        conf_level = 'moderate'
        action = f"Likely {pred_name}. Review with a radiologist."
    else:
        conf_level = 'low'
        action = "LOW CONFIDENCE — manual review required."

    recommendation = f"{pred_name} DETECTED" if is_tumor else "NO TUMOR DETECTED"
    logger.info(f"Done in {time.time()-t0:.2f}s → {recommendation} ({conf:.1%})")

    return PredictionResponse(
        timestamp              = datetime.now().isoformat(),
        filename               = file.filename or 'upload',
        ensemble_prediction    = result['ensemble_class_name'],
        ensemble_confidence    = conf,
        cnn_prediction         = ModelPrediction(**result['individual']['cnn']),
        resnet_prediction      = ModelPrediction(**result['individual']['resnet']),
        vit_prediction         = ModelPrediction(**result['individual']['vit']),
        class_probabilities    = result['ensemble_probs'],
        model_agreement        = result['model_agreement'],
        uncertainty            = entropy,
        gradcam_overlay_base64 = gradcam_b64,
        segmentation_overlay_base64 = seg_b64,
        recommendation         = recommendation,
        confidence_level       = conf_level,
        suggested_action       = action,
    )


@app.get('/models')
async def get_models():
    return {
        'loaded_models': list(model_manager.models.keys()),
        'load_times':    model_manager.load_time,
        'device':        str(DEVICE),
        'class_names':   CLASS_NAMES,
        'model_dir':     MODEL_PATH,
    }


@app.get('/info')
async def info():
    return {
        'title':        'BrainGuard AI',
        'version':      '1.0.0',
        'models':       ['BaseCNN', 'ResNet50Transfer', 'HybridResNetViT'],
        'classes':      CLASS_NAMES,
        'device':       str(DEVICE),
        'models_ready': model_manager.ready,
        'model_dir':    MODEL_PATH,
    }


class ReportRequest(BaseModel):
    patient_name: str
    patient_id: str
    age: Optional[int] = None
    scan_date: Optional[str] = None
    prediction: str
    confidence: float
    class_probabilities: Dict[str, float]
    model_predictions: Dict[str, Dict]
    uncertainty: float
    gradcam_image_base64: str
    recommendation: str
    confidence_level: str
    suggested_action: str


@app.post('/api/report')
async def generate_pdf_report(req: ReportRequest):
    try:
        from pdf_reports import PdfReportGenerator
        
        logger.info(f"Generating PDF report for Patient ID: {req.patient_id}")
        generator = PdfReportGenerator(
            patient_name=req.patient_name,
            patient_id=req.patient_id,
            age=req.age,
            scan_date=req.scan_date
        )
        
        # Calculate rough confidence interval
        ci_lower = max(0.0, req.confidence - req.uncertainty * 0.1)
        ci_upper = min(1.0, req.confidence + req.uncertainty * 0.1)
        
        pdf_bytes = generator.generate_report(
            prediction=req.prediction,
            confidence=req.confidence,
            class_probabilities=req.class_probabilities,
            model_predictions=req.model_predictions,
            gradcam_image=req.gradcam_image_base64,
            uncertainty=req.uncertainty,
            confidence_interval=(ci_lower, ci_upper),
            recommendation=req.recommendation,
            confidence_level=req.confidence_level,
            suggested_action=req.suggested_action
        )
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="BrainGuardAI_Report_{req.patient_id}.pdf"'}
        )
    except Exception as e:
        logger.error(f"Failed to generate PDF report: {e}")
        raise HTTPException(500, f"Failed to generate report: {str(e)}")


# Serve static files from the 'public' directory at root
if os.path.exists(PUBLIC_DIR):
    logger.info(f"Mounting static files from: {PUBLIC_DIR}")
    app.mount("/", StaticFiles(directory=PUBLIC_DIR, html=True), name="public")
else:
    logger.warning(f"Static public directory NOT found at: {PUBLIC_DIR}. Make sure it is created.")


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        'fastapi_backend:app',
        host      = '0.0.0.0',
        port      = int(os.getenv('API_PORT', 8000)),
        log_level = 'info',
        reload    = False,
    )