# Phase 6 — Tumor Segmentation with Attention U-Net
# Localize tumor region on MRI image

import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy as np
import cv2
from typing import Tuple
import matplotlib.pyplot as plt
from PIL import Image
import base64
from io import BytesIO

# ============================================================
# ATTENTION MECHANISMS
# ============================================================

class ChannelAttention(nn.Module):
    """Channel Attention Module (squeeze-excitation)"""
    
    def __init__(self, in_channels, reduction_ratio=16):
        super().__init__()
        
        self.fc = nn.Sequential(
            nn.Linear(in_channels, in_channels // reduction_ratio, bias=False),
            nn.ReLU(),
            nn.Linear(in_channels // reduction_ratio, in_channels, bias=False),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        batch, channels, _, _ = x.shape
        
        # Global average pooling
        gap = F.adaptive_avg_pool2d(x, 1).view(batch, channels)
        
        # FC layers
        weights = self.fc(gap).view(batch, channels, 1, 1)
        
        # Apply weights
        return x * weights


class SpatialAttention(nn.Module):
    """Spatial Attention Module"""
    
    def __init__(self, kernel_size=7):
        super().__init__()
        
        self.conv = nn.Sequential(
            nn.Conv2d(2, 1, kernel_size, padding=kernel_size // 2, bias=False),
            nn.BatchNorm2d(1),
            nn.Sigmoid()
        )
    
    def forward(self, x):
        # Channel-wise statistics
        avg_pool = torch.mean(x, dim=1, keepdim=True)
        max_pool, _ = torch.max(x, dim=1, keepdim=True)
        
        # Concatenate
        concat = torch.cat([avg_pool, max_pool], dim=1)
        
        # Spatial attention
        attention = self.conv(concat)
        
        return x * attention


class AttentionGate(nn.Module):
    """Attention Gate for U-Net"""
    
    def __init__(self, F_g, F_l, F_int):
        """
        Args:
            F_g: Gate channels
            F_l: Skip connection channels
            F_int: Intermediate channels
        """
        super().__init__()
        
        self.W_gate = nn.Conv2d(F_g, F_int, 1)
        self.W_skip = nn.Conv2d(F_l, F_int, 1)
        self.psi = nn.Conv2d(F_int, 1, 1)
        self.relu = nn.ReLU()
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, gate, skip):
        """
        Args:
            gate: From decoder (H, W)
            skip: From encoder (2H, 2W)
        """
        # Upsample gate to match skip
        gate = F.interpolate(gate, size=skip.shape[2:], mode='bilinear', align_corners=False)
        
        # Combine
        combined = self.W_gate(gate) + self.W_skip(skip)
        combined = self.relu(combined)
        
        # Attention weights
        attention = self.psi(combined)
        attention = self.sigmoid(attention)
        
        # Apply attention to skip
        return skip * attention


# ============================================================
# ATTENTION U-NET ARCHITECTURE
# ============================================================

class AttentionUNet(nn.Module):
    """
    U-Net with Attention Gates for semantic segmentation
    Learns to focus on tumor regions
    """
    
    def __init__(self, in_channels=3, out_channels=1, base_channels=64):
        super().__init__()
        
        self.base_channels = base_channels
        
        # Encoder (Downsampling)
        self.enc1 = self.conv_block(in_channels, base_channels)
        self.pool1 = nn.MaxPool2d(2, 2)
        
        self.enc2 = self.conv_block(base_channels, base_channels * 2)
        self.pool2 = nn.MaxPool2d(2, 2)
        
        self.enc3 = self.conv_block(base_channels * 2, base_channels * 4)
        self.pool3 = nn.MaxPool2d(2, 2)
        
        self.enc4 = self.conv_block(base_channels * 4, base_channels * 8)
        self.pool4 = nn.MaxPool2d(2, 2)
        
        # Bottleneck
        self.bottleneck = self.conv_block(base_channels * 8, base_channels * 16)
        
        # Decoder (Upsampling) + Attention Gates
        self.upconv4 = nn.ConvTranspose2d(base_channels * 16, base_channels * 8, 2, 2)
        self.att4 = AttentionGate(base_channels * 8, base_channels * 8, base_channels * 4)
        self.dec4 = self.conv_block(base_channels * 16, base_channels * 8)
        
        self.upconv3 = nn.ConvTranspose2d(base_channels * 8, base_channels * 4, 2, 2)
        self.att3 = AttentionGate(base_channels * 4, base_channels * 4, base_channels * 2)
        self.dec3 = self.conv_block(base_channels * 8, base_channels * 4)
        
        self.upconv2 = nn.ConvTranspose2d(base_channels * 4, base_channels * 2, 2, 2)
        self.att2 = AttentionGate(base_channels * 2, base_channels * 2, base_channels)
        self.dec2 = self.conv_block(base_channels * 4, base_channels * 2)
        
        self.upconv1 = nn.ConvTranspose2d(base_channels * 2, base_channels, 2, 2)
        self.att1 = AttentionGate(base_channels, base_channels, base_channels // 2)
        self.dec1 = self.conv_block(base_channels * 2, base_channels)
        
        # Output
        self.final_conv = nn.Conv2d(base_channels, out_channels, 1)
        self.sigmoid = nn.Sigmoid()
    
    def conv_block(self, in_ch, out_ch):
        """Double convolution block"""
        return nn.Sequential(
            nn.Conv2d(in_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_ch, out_ch, 3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True)
        )
    
    def forward(self, x):
        # Encoder
        enc1 = self.enc1(x)
        pool1 = self.pool1(enc1)
        
        enc2 = self.enc2(pool1)
        pool2 = self.pool2(enc2)
        
        enc3 = self.enc3(pool2)
        pool3 = self.pool3(enc3)
        
        enc4 = self.enc4(pool3)
        pool4 = self.pool4(enc4)
        
        # Bottleneck
        bn = self.bottleneck(pool4)
        
        # Decoder with Attention
        upconv4 = self.upconv4(bn)
        att4 = self.att4(upconv4, enc4)
        dec4 = self.dec4(torch.cat([upconv4, att4], dim=1))
        
        upconv3 = self.upconv3(dec4)
        att3 = self.att3(upconv3, enc3)
        dec3 = self.dec3(torch.cat([upconv3, att3], dim=1))
        
        upconv2 = self.upconv2(dec3)
        att2 = self.att2(upconv2, enc2)
        dec2 = self.dec2(torch.cat([upconv2, att2], dim=1))
        
        upconv1 = self.upconv1(dec2)
        att1 = self.att1(upconv1, enc1)
        dec1 = self.dec1(torch.cat([upconv1, att1], dim=1))
        
        # Output
        output = self.final_conv(dec1)
        output = self.sigmoid(output)
        
        return output


# ============================================================
# SEGMENTATION INFERENCE
# ============================================================

class TumorSegmenter:
    """
    Segment tumor region from MRI image
    """
    
    def __init__(self, model_path: str, device: str = 'cpu'):
        """
        Args:
            model_path: Path to trained Attention U-Net
            device: 'cpu' or 'cuda'
        """
        self.device = torch.device(device)
        self.model = AttentionUNet().to(self.device)
        
        # Load weights with memory mapping for free tiers
        checkpoint = torch.load(model_path, map_location=self.device, weights_only=False, mmap=True)
        if isinstance(checkpoint, dict) and 'model_state' in checkpoint:
            self.model.load_state_dict(checkpoint['model_state'])
        else:
            self.model.load_state_dict(checkpoint)
        
        self.model.eval()
    
    def segment(self, image: np.ndarray,
               threshold: float = 0.5) -> Tuple[np.ndarray, float]:
        """
        Segment tumor from image
        
        Args:
            image: Input image (H, W, 3) with values [0, 1] or [0, 255]
            threshold: Probability threshold for segmentation
            
        Returns:
            mask: Binary segmentation mask (H, W)
            confidence: Average probability in tumor region
        """
        # Normalize if needed
        if image.max() > 1:
            image = image / 255.0
        
        # Resize to 224x224
        original_size = image.shape[:2]
        image_resized = cv2.resize(image, (224, 224))
        
        # Preprocess
        image_tensor = torch.from_numpy(image_resized).permute(2, 0, 1).float()
        image_tensor = image_tensor.unsqueeze(0).to(self.device)
        
        # Normalize (using EDA values)
        mean = torch.tensor([0.18, 0.18, 0.18]).view(1, 3, 1, 1).to(self.device)
        std = torch.tensor([0.177, 0.177, 0.177]).view(1, 3, 1, 1).to(self.device)
        image_tensor = (image_tensor - mean) / std
        
        # Segment
        with torch.no_grad():
            prob_map = self.model(image_tensor)[0, 0].cpu().numpy()
        
        # Apply threshold
        mask = (prob_map > threshold).astype(np.uint8)
        
        # Resize back to original
        mask = cv2.resize(mask, (original_size[1], original_size[0]), interpolation=cv2.INTER_NEAREST)
        
        # Calculate confidence
        confidence = prob_map[prob_map > threshold].mean() if mask.sum() > 0 else 0.0
        
        return mask, float(confidence)
    
    def segment_with_contours(self, image: np.ndarray,
                             threshold: float = 0.5) -> Tuple[np.ndarray, list, float]:
        """
        Segment and extract tumor contours
        
        Args:
            image: Input image (H, W, 3)
            threshold: Probability threshold
            
        Returns:
            mask: Binary mask
            contours: List of contours
            confidence: Segmentation confidence
        """
        mask, confidence = self.segment(image, threshold)
        
        # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        return mask, contours, confidence


# ============================================================
# VISUALIZATION
# ============================================================

def visualize_segmentation(image: np.ndarray,
                          mask: np.ndarray,
                          contours: list = None,
                          title: str = "Tumor Segmentation") -> np.ndarray:
    """
    Create segmentation overlay visualization
    
    Args:
        image: Original image (H, W, 3)
        mask: Binary mask (H, W)
        contours: Optional list of contours
        title: Figure title
        
    Returns:
        Overlay image (H, W, 3)
    """
    overlay = image.copy()
    
    # Normalize image
    if image.max() > 1:
        overlay = overlay / 255.0
    if overlay.dtype != np.uint8:
        overlay = (overlay * 255).astype(np.uint8)
    
    # Apply mask as red overlay
    mask_rgb = np.zeros_like(overlay)
    mask_rgb[mask == 1] = [255, 0, 0]  # Red for tumor
    
    # Blend
    overlay = cv2.addWeighted(overlay, 0.7, mask_rgb, 0.3, 0)
    
    # Draw contours if provided
    if contours:
        cv2.drawContours(overlay, contours, -1, (0, 255, 0), 2)
    
    return overlay


def create_segmentation_report(image: np.ndarray,
                              mask: np.ndarray,
                              overlay: np.ndarray,
                              confidence: float) -> bytes:
    """
    Create 3-panel comparison figure
    
    Args:
        image: Original image
        mask: Binary mask
        overlay: Segmentation overlay
        confidence: Segmentation confidence
        
    Returns:
        PNG bytes
    """
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(f'Tumor Segmentation (Confidence: {confidence:.2%})', 
                fontweight='bold')
    
    # Original
    axes[0].imshow(image)
    axes[0].set_title('Original MRI')
    axes[0].axis('off')
    
    # Mask
    axes[1].imshow(mask, cmap='gray')
    axes[1].set_title('Segmentation Mask')
    axes[1].axis('off')
    
    # Overlay
    axes[2].imshow(overlay)
    axes[2].set_title('Segmentation Overlay')
    axes[2].axis('off')
    
    plt.tight_layout()
    
    # Save to bytes
    buf = BytesIO()
    plt.savefig(buf, format='png', dpi=100, bbox_inches='tight')
    plt.close()
    
    buf.seek(0)
    return buf.getvalue()


def mask_to_base64(mask: np.ndarray) -> str:
    """Convert mask to base64 PNG"""
    # Convert to uint8
    mask_uint8 = (mask * 255).astype(np.uint8)
    
    # Convert to PIL
    pil_image = Image.fromarray(mask_uint8, mode='L')
    
    # Save to bytes
    buffer = BytesIO()
    pil_image.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Encode
    image_bytes = buffer.getvalue()
    base64_str = base64.b64encode(image_bytes).decode('utf-8')
    
    return f"data:image/png;base64,{base64_str}"


# ============================================================
# USAGE EXAMPLE
# ============================================================

if __name__ == '__main__':
    """
    # Example usage
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    # Load segmentation model
    segmenter = TumorSegmenter('segmentation_model.pth', device=device)
    
    # Load MRI image
    image = cv2.imread('mri_image.jpg')
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Segment
    mask, contours, confidence = segmenter.segment_with_contours(image, threshold=0.5)
    
    # Visualize
    overlay = visualize_segmentation(image, mask, contours)
    
    # Create report
    report = create_segmentation_report(image, mask, overlay, confidence)
    
    # Save
    with open('segmentation_report.png', 'wb') as f:
        f.write(report)
    
    print(f"Segmentation Confidence: {confidence:.2%}")
    print(f"Tumor Area: {mask.sum()} pixels")
    """
    pass