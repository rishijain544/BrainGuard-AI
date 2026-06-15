<div align="center">
  <img src="frontend/public/assets/brainguard_logo.png" alt="BrainGuard AI Logo" width="150"/>
  
  # BrainGuard AI 🧠
  
  **Advanced Deep Learning MRI Analysis & Clinical Diagnosis Platform**
  
  [![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-black?style=for-the-badge&logo=vercel)](https://brain-guard-ai.vercel.app/)
  [![Python](https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python)](https://www.python.org/)
  [![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-EE4C2C?style=for-the-badge&logo=pytorch)](https://pytorch.org/)
  [![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)

</div>

---

## 🌟 Overview

**BrainGuard AI** is a state-of-the-art medical imaging application designed to assist medical professionals in detecting, classifying, and analyzing brain tumors from MRI scans. 

By leveraging an ensemble of deep learning models (ResNet50, Vision Transformers, and custom CNNs), BrainGuard provides extremely high-accuracy predictions. More than just a simple classifier, it features a comprehensive suite of **Advanced Clinical Analytics** including Grad-CAM heatzones, tumour volume estimation, pixel intensity histograms, and automated PDF report generation.

👉 **[Try the Live Application Here](https://brain-guard-ai.vercel.app/)**

---

## ✨ Key Features

- 🔬 **Ensemble Deep Learning:** Combines multiple neural network architectures (ViT, ResNet, CNN) for highly robust tumor classification (Glioma, Meningioma, Pituitary, or No Tumor).
- 🗺️ **Explainable AI (Grad-CAM):** Generates heatmaps highlighting the exact regions of the MRI that led to the model's prediction.
- 📊 **Advanced Analytics Dashboard:**
  - **Pixel Intensity Histogram:** Analyzes the grayscale distribution of the MRI.
  - **Brain Symmetry Analysis:** Detects structural asymmetry often caused by tumors.
  - **Tumor Heatzone Map:** Calculates highest activation quadrants.
  - **Lobe Detection Indicator:** Estimates affected brain lobes based on spatial activation.
- 📄 **Clinical PDF Reports:** Automatically generates professional, downloadable medical reports containing patient data, scan metrics, and the Grad-CAM visualization.
- ⚡ **Lightning Fast UI:** A premium, fully responsive frontend built with modern CSS and Chart.js animations.

---

## 🛠️ Technology Stack

**Frontend:**
- HTML5, Vanilla JavaScript, CSS3
- Chart.js (for dynamic analytics visualization)
- Vercel (Hosting)

**Backend:**
- Python 3.10+
- FastAPI (High-performance API routing)
- PyTorch & Torchvision (Deep Learning framework)
- OpenCV & Pillow (Image processing)
- Docker (Containerization for production deployment)

---

## 🚀 Running Locally

If you wish to run BrainGuard AI on your local machine:

### 1. Clone the Repository
```bash
git clone https://github.com/rishijain544/BrainGuard-AI.git
cd BrainGuard-AI
```

### 2. Setup the Backend
You will need Python 3.10+ installed.
```bash
# Create a virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r backend/requirements.txt
```

### 3. Add Pre-trained Models
Ensure you place your pre-trained `.pth` weight files (like `cnn_best.pth`, `resnet_best.pth`, etc.) inside the `backend/models/` directory. *(Note: These are excluded from GitHub due to file size limits).*

### 4. Start the Application
You can start both the frontend and backend simultaneously using the provided script:
```bash
python run_server.py
```
Alternatively, run the FastAPI server directly:
```bash
uvicorn backend.fastapi_backend:app --host 0.0.0.0 --port 8000
```

---

## 🌐 Deployment Architecture

The application is architected for a decoupled deployment:
- **Frontend** is statically hosted on **Vercel** (`https://brain-guard-ai.vercel.app/`).
- **Backend** is containerized via `Dockerfile` and hosted on a cloud container platform (e.g., Railway, Render) to handle the heavy PyTorch ML models.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/rishijain544/BrainGuard-AI/issues).

---

<div align="center">
  <i>Built with ❤️ for the advancement of medical AI.</i>
</div>
