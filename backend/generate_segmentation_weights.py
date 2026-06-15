import torch
import os
import sys

# Add current directory to path so we can import from segmentation.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from segmentation import AttentionUNet

def generate():
    model = AttentionUNet()
    os.makedirs('models', exist_ok=True)
    
    checkpoint = {
        'model_state': model.state_dict()
    }
    
    torch.save(checkpoint, 'models/segmentation_model.pth')
    print("Successfully generated dummy weights for models/segmentation_model.pth")

if __name__ == '__main__':
    generate()
