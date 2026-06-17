---
title: BrainGuard AI
emoji: 🧠
colorFrom: purple
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

<div align="center">
  <img src="frontend/public/assets/brainguard_logo.png" alt="BrainGuard AI Logo" width="180"/>
  
  # BrainGuard AI 🧠
  
  **Advanced Deep Learning MRI Analysis & Clinical Diagnosis Platform**
  
  [![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-black?style=for-the-badge&logo=vercel)](https://brain-guard-ai.vercel.app/)
  [![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
  [![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=for-the-badge&logo=pytorch)](https://pytorch.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)

</div>

---

## 🌟 Executive Summary

**BrainGuard AI** is a comprehensive, end-to-end medical imaging platform engineered to assist clinical professionals in diagnosing brain tumors from Magnetic Resonance Imaging (MRI) scans. 

Moving beyond simple classification, this project incorporates an extensive data science lifecycle—from initial **Exploratory Data Analysis (EDA)** to the deployment of a highly accurate **Ensemble Deep Learning** model utilizing CNNs, ResNets, and Vision Transformers (ViT). 

Furthermore, the platform provides rich Explainable AI (XAI) features, ensuring that predictions are transparent and visually verifiable by medical staff.

👉 **[Experience the Live Application Here](https://brain-guard-ai.vercel.app/)**

---

## 📊 Exploratory Data Analysis (EDA)

Before modeling, an exhaustive EDA phase was conducted to understand the underlying distributions and challenges within the MRI dataset. Key findings and preprocessing steps included:

- **Class Distribution Analysis:** Evaluated the balance between Glioma, Meningioma, Pituitary, and No Tumor classes to prevent model bias.
- **Image Standardization:** Addressed variations in MRI contrast, brightness, and resolution by applying histogram equalization and resizing all images to a uniform tensor shape.
- **Augmentation Strategies:** Implemented spatial transformations (rotations, flips) and color jitter to artificially expand the dataset and improve the model's ability to generalize to new patient scans.
- **Pixel Intensity Profiling:** Analyzed the grayscale distribution to establish thresholds separating dense tumor mass from normal brain tissue.

---

## 🧠 Deep Learning Architectures

To achieve near-perfect clinical accuracy, BrainGuard AI does not rely on a single algorithm. Instead, it utilizes an ensemble of cutting-edge computer vision architectures:

### 1. Custom Convolutional Neural Network (CNN)
A highly optimized, lightweight CNN built from scratch to act as the baseline feature extractor. It captures local spatial patterns and edges (like the distinct boundaries of a meningioma) rapidly and effectively.

### 2. ResNet (Residual Networks)
Leveraging Transfer Learning, a pre-trained **ResNet50** model was fine-tuned on our MRI dataset. The residual skip connections allow the network to learn extremely deep hierarchical features without suffering from the vanishing gradient problem. It excels at identifying deep-tissue structural anomalies.

### 3. Vision Transformer (ViT)
Transformers are revolutionizing computer vision. The **ViT** model divides the MRI scan into sequential patches, utilizing self-attention mechanisms to understand the *global context* of the brain. While CNNs focus on local textures, the ViT understands the relationship between distant regions of the brain, leading to unmatched predictive robustness.

### 4. Ensemble Prediction Engine
The final diagnosis is computed through a weighted ensemble of the CNN, ResNet, and ViT models. By combining their diverse "perspectives" (local features vs. global attention), the application achieves exceptional diagnostic confidence.

---

## ✨ Clinical Explainability & Advanced Analytics

Medical AI must be transparent. BrainGuard AI provides medical professionals with deep insights into *why* a prediction was made:

- 🗺️ **Grad-CAM (Gradient-weighted Class Activation Mapping):** Generates a colored heatmap over the MRI, highlighting the exact pixels the neural network focused on to make its diagnosis.
- 📉 **Pixel Intensity Histogram:** Maps the grayscale values of the scan. Tumors often present as anomalous peaks in brightness or darkness, which are instantly visible here.
- ⚖️ **Brain Symmetry Analysis:** Healthy brains exhibit bilateral symmetry. The app algorithmically compares the left and right hemispheres to detect physical distortions caused by growing masses.
- 📍 **Lobe Detection & Quadrant Heatzone:** Estimates which quadrant (and corresponding brain lobe: Frontal, Parietal, Temporal, Occipital) is most affected by the mass.
- 📄 **Automated PDF Clinical Reports:** With one click, generates a professional medical report containing the patient's ID, the AI's diagnosis, confidence scores, and the Grad-CAM visualization for patient records.

---

## 🛠️ Technology Stack & Deployment

**Frontend:**
- HTML5, Vanilla JavaScript, CSS3 (Glassmorphism & Medical UI aesthetics)
- Chart.js (Dynamic analytical visualizations)
- **Vercel** (Global Edge CDN Hosting)

**Backend:**
- Python 3.10+
- FastAPI (High-performance asynchronous API)
- PyTorch & Torchvision (Deep Learning inference)
- OpenCV, Pillow, Scikit-learn (Image processing and data handling)
- **Docker** (Containerized for consistent production environments)
- **Hugging Face Spaces** (Cloud execution of the PyTorch ML containers utilizing 16GB RAM)

---

## 🚀 Running Locally

Want to run the complete data pipeline and web application on your own machine?

### 1. Clone the Repository
```bash
git clone https://github.com/rishijain544/BrainGuard-AI.git
cd BrainGuard-AI
```

### 2. Setup the Environment
You will need Python 3.10+ installed.
```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate

# Install all backend dependencies
pip install -r backend/requirements.txt
```

### 3. Add Pre-trained Weights
Ensure you place your pre-trained PyTorch weight files (`cnn_best.pth`, `resnet_best.pth`, `vit_best.pth`) inside the `backend/models/` directory. *(Note: These are excluded from GitHub by default due to standard file size limits).*

### 4. Start the Application
Run the backend API:
```bash
uvicorn backend.fastapi_backend:app --host 0.0.0.0 --port 8000
```
Then, open `frontend/index.html` in any modern web browser to access the UI.

---

## 🤝 Contributing

Contributions to improve accuracy, speed, or UX are highly encouraged! Feel free to fork the repository and submit a pull request, or check the [issues page](https://github.com/rishijain544/BrainGuard-AI/issues).

---

<div align="center">
  <i>Built with ❤️ for the advancement of medical AI.</i>
</div>
