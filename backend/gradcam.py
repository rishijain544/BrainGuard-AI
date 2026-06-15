# Phase 4 — Grad-CAM Explainability
# Brain Tumor MRI Classification with Visual Explanations

import torch
import torch.nn.functional as F
import numpy as np
import cv2
from PIL import Image
import matplotlib.pyplot as plt
from typing import Tuple, Optional
import base64
from io import BytesIO

# ============================================================
# GRAD-CAM IMPLEMENTATION
# ============================================================

class GradCAM:
    """
    Gradient-weighted Class Activation Mapping (Grad-CAM)
    Visualizes which regions of the image contributed to the model's prediction
    """
    
    def __init__(self, model, target_layer):
        """
        Args:
            model: PyTorch model
            target_layer: Layer to compute gradients for
        """
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        # Register hooks
        self.target_layer.register_forward_hook(self.save_activation)
        self.target_layer.register_backward_hook(self.save_gradient)
    
    def save_activation(self, module, input, output):
        """Hook to save activation maps"""
        self.activations = output.detach()
    
    def save_gradient(self, module, grad_input, grad_output):
        """Hook to save gradients"""
        self.gradients = grad_output[0].detach()
    
    def generate_cam(self, input_tensor: torch.Tensor, 
                    target_class: Optional[int] = None) -> np.ndarray:
        """
        Generate Grad-CAM heatmap
        
        Args:
            input_tensor: Input image tensor (1, 3, 224, 224)
            target_class: Target class index. If None, use predicted class
            
        Returns:
            CAM heatmap (224, 224) with values in [0, 1]
        """
        # Forward pass
        self.model.eval()
        logits = self.model(input_tensor)
        
        if target_class is None:
            target_class = logits.argmax(dim=1).item()
        
        # Backward pass
        self.model.zero_grad()
        target_score = logits[0, target_class]
        target_score.backward()
        
        # Compute Grad-CAM
        # Shape: (C, H, W)
        gradients = self.gradients[0]  # (C, H, W)
        activations = self.activations[0]  # (C, H, W)
        
        # Compute channel weights
        weights = gradients.mean(dim=(1, 2))  # (C,)
        
        # Weighted sum of activations
        cam = torch.zeros(activations.shape[1:], device=activations.device)
        for i in range(activations.shape[0]):
            cam += weights[i] * activations[i]
        
        # ReLU
        cam = F.relu(cam)
        
        # Normalize
        cam_min = cam.min()
        cam_max = cam.max()
        if cam_max - cam_min > 0:
            cam = (cam - cam_min) / (cam_max - cam_min)
        else:
            cam = torch.zeros_like(cam)
        
        return cam.cpu().numpy()


class VitPatchSaliency:
    """
    Vision Transformer Patch Saliency
    Uses attention weights to show which patches the model focuses on
    """
    
    def __init__(self, model):
        self.model = model
        self.attention_weights = []
        self.register_hooks()
    
    def register_hooks(self):
        """Register hooks to capture attention weights"""
        for block in self.model.blocks:
            block.attn.register_forward_hook(self.capture_attention)
    
    def capture_attention(self, module, input, output):
        """Capture attention weights from each block"""
        # output is (B, H, N, N) where H is num heads, N is num patches
        self.attention_weights.append(output.detach())
    
    def generate_saliency(self, input_tensor: torch.Tensor) -> np.ndarray:
        """
        Generate patch saliency from attention weights
        
        Args:
            input_tensor: Input image tensor (1, 3, 224, 224)
            
        Returns:
            Saliency map (224, 224) with values in [0, 1]
        """
        self.model.eval()
        self.attention_weights = []
        
        with torch.no_grad():
            _ = self.model(input_tensor)
        
        # Get attention from last block, first head, CLS token attention
        if not self.attention_weights:
            return np.ones((224, 224)) * 0.5
        
        # Last layer attention: (B, H, N, N)
        last_attention = self.attention_weights[-1]
        batch_idx = 0
        head_idx = 0
        
        # CLS token attention to all patches: (N,)
        cls_attention = last_attention[batch_idx, head_idx, 0, 1:]
        
        # Reshape to (14, 14)
        saliency = cls_attention.reshape(14, 14).cpu().numpy()
        
        # Normalize
        saliency = (saliency - saliency.min()) / (saliency.max() - saliency.min() + 1e-8)
        
        # Upsample to 224x224
        saliency = cv2.resize(saliency, (224, 224), interpolation=cv2.INTER_CUBIC)
        
        return saliency


# ============================================================
# HEATMAP GENERATION & VISUALIZATION
# ============================================================

def generate_heatmap_overlay(image: np.ndarray, 
                            saliency_map: np.ndarray,
                            alpha: float = 0.4) -> np.ndarray:
    """
    Overlay heatmap on original image
    
    Args:
        image: Original image (H, W, 3) with values [0, 255]
        saliency_map: Saliency map (H, W) with values [0, 1]
        alpha: Transparency of overlay
        
    Returns:
        Overlaid image (H, W, 3)
    """
    # Convert saliency to 0-255
    saliency_map = (saliency_map * 255).astype(np.uint8)
    
    # Apply JET colormap (red for high values, blue for low)
    heatmap = cv2.applyColorMap(saliency_map, cv2.COLORMAP_JET)
    
    # Convert to RGB (OpenCV uses BGR)
    heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
    
    # Blend with original image
    overlay = cv2.addWeighted(image, 1 - alpha, heatmap, alpha, 0)
    
    return overlay


def create_comparison_figure(original: np.ndarray,
                            saliency: np.ndarray,
                            overlay: np.ndarray,
                            title: str = "Grad-CAM Visualization") -> bytes:
    """
    Create 3-panel comparison figure: Original | Saliency | Overlay
    
    Args:
        original: Original image (H, W, 3)
        saliency: Saliency map (H, W)
        overlay: Overlay image (H, W, 3)
        title: Figure title
        
    Returns:
        PNG image as bytes
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(title, fontsize=14, fontweight='bold')
    
    # Original
    axes[0].imshow(original)
    axes[0].set_title('Original MRI')
    axes[0].axis('off')
    
    # Saliency
    axes[1].imshow(saliency, cmap='jet')
    axes[1].set_title('Grad-CAM Heatmap')
    axes[1].axis('off')
    cbar1 = plt.colorbar(axes[1].images[0], ax=axes[1])
    cbar1.set_label('Activation')
    
    # Overlay
    axes[2].imshow(overlay)
    axes[2].set_title('Overlay')
    axes[2].axis('off')
    
    plt.tight_layout()
    
    # Save to bytes
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    
    buf.seek(0)
    return buf.getvalue()


def image_to_base64(image: np.ndarray) -> str:
    """
    Convert image array to base64 PNG string
    
    Args:
        image: Image array (H, W, 3)
        
    Returns:
        Base64 encoded PNG string with data URI prefix
    """
    # Convert to uint8 if needed
    if image.dtype != np.uint8:
        image = (image * 255).astype(np.uint8)
    
    # Convert to PIL Image
    pil_image = Image.fromarray(image)
    
    # Save to bytes buffer
    buffer = BytesIO()
    pil_image.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Encode to base64
    image_bytes = buffer.getvalue()
    base64_str = base64.b64encode(image_bytes).decode('utf-8')
    
    return f"data:image/png;base64,{base64_str}"


# ============================================================
# INTEGRATION WITH MODELS
# ============================================================

class ExplainableModel:
    """
    Wrapper for any model to add Grad-CAM explanations
    """
    
    def __init__(self, model, model_type: str = 'cnn'):
        """
        Args:
            model: PyTorch model
            model_type: 'cnn', 'resnet', or 'vit'
        """
        self.model = model
        self.model_type = model_type
        
        if model_type == 'cnn':
            # Last Conv2d layer in features
            target_layer = model.features[-3]  # Last Conv2d
            self.explainer = GradCAM(model, target_layer)
        
        elif model_type == 'resnet':
            # layer4[-1].conv3
            target_layer = model.model.layer4[-1].conv3
            self.explainer = GradCAM(model, target_layer)
        
        elif model_type == 'vit':
            self.explainer = VitPatchSaliency(model)
    
    def predict_with_explanation(self, 
                                 image_tensor: torch.Tensor,
                                 original_image: np.ndarray) -> dict:
        """
        Get prediction and explanation
        
        Args:
            image_tensor: Preprocessed image tensor (1, 3, 224, 224)
            original_image: Original image array (H, W, 3) for visualization
            
        Returns:
            {
                'prediction': class_index,
                'confidence': probability,
                'saliency_map': numpy array,
                'overlay_image': numpy array,
                'overlay_base64': base64 string
            }
        """
        self.model.eval()
        
        with torch.no_grad():
            logits = self.model(image_tensor)
            probabilities = torch.softmax(logits, dim=1)
        
        pred_class = logits.argmax(dim=1).item()
        confidence = probabilities[0, pred_class].item()
        
        # Generate explanation
        if self.model_type == 'vit':
            saliency = self.explainer.generate_saliency(image_tensor)
        else:
            saliency = self.explainer.generate_cam(image_tensor, pred_class)
        
        # Upsample saliency to match original image size
        saliency = cv2.resize(saliency, (original_image.shape[1], original_image.shape[0]))
        
        # Generate overlay
        overlay = generate_heatmap_overlay(original_image, saliency)
        
        # Convert to base64
        overlay_base64 = image_to_base64(overlay)
        
        return {
            'prediction': pred_class,
            'confidence': float(confidence),
            'saliency_map': saliency,
            'overlay_image': overlay,
            'overlay_base64': overlay_base64
        }


# ============================================================
# USAGE EXAMPLE
# ============================================================

if __name__ == '__main__':
    # Example (requires trained models)
    """
    import torch
    from PIL import Image
    from torchvision import transforms
    
    # Load model
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = load_model('cnn_best.pth').to(device)
    
    # Load and preprocess image
    image_path = 'path/to/mri.jpg'
    image = Image.open(image_path).convert('RGB')
    image_array = np.array(image)
    
    # Preprocess
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.18, 0.18, 0.18],
                            std=[0.177, 0.177, 0.177])
    ])
    image_tensor = transform(image).unsqueeze(0).to(device)
    
    # Get prediction with explanation
    explainer = ExplainableModel(model, model_type='cnn')
    result = explainer.predict_with_explanation(image_tensor, image_array)
    
    print(f"Prediction: {result['prediction']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Overlay base64: {result['overlay_base64'][:50]}...")
    """
    pass