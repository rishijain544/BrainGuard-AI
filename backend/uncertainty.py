# Phase 5 — MC Dropout Uncertainty Estimation
# Quantify prediction confidence and uncertainty

import torch
import torch.nn as nn
import numpy as np
from typing import Tuple, List, Dict
import warnings

# ============================================================
# MC DROPOUT UTILITY
# ============================================================

class MCDropout:
    """
    Monte Carlo Dropout for uncertainty estimation
    Run model multiple times with dropout enabled to get prediction distribution
    """
    
    def __init__(self, model, num_samples: int = 30):
        """
        Args:
            model: PyTorch model with dropout layers
            num_samples: Number of forward passes (T)
        """
        self.model = model
        self.num_samples = num_samples
    
    def enable_dropout(self):
        """Enable dropout during inference"""
        for module in self.model.modules():
            if isinstance(module, nn.Dropout):
                module.train()
    
    def disable_dropout(self):
        """Disable dropout"""
        self.model.eval()
    
    def predict_with_uncertainty(self, 
                                 image_tensor: torch.Tensor,
                                 class_names: List[str] = None) -> Dict:
        """
        Get predictions with uncertainty estimates
        
        Args:
            image_tensor: Input tensor (1, 3, 224, 224)
            class_names: List of class names
            
        Returns:
            {
                'ensemble_prediction': class,
                'ensemble_confidence': float,
                'uncertainty': float,  # [0, 1]
                'confidence_interval': (lower, upper),
                'predictions': [dict, ...],  # T predictions
                'epistemic_uncertainty': float,  # Model uncertainty
                'aleatoric_uncertainty': float,  # Data uncertainty
                'uncertainty_level': 'low' | 'moderate' | 'high'
            }
        """
        device = image_tensor.device
        predictions = []
        
        # Enable dropout
        self.enable_dropout()
        
        with torch.no_grad():
            for _ in range(self.num_samples):
                logits = self.model(image_tensor)
                probs = torch.softmax(logits, dim=1)
                predictions.append(probs[0].cpu().numpy())
        
        # Disable dropout
        self.disable_dropout()
        
        # Convert to array: (T, C)
        predictions = np.array(predictions)
        
        # Compute statistics
        mean_pred = predictions.mean(axis=0)  # (C,)
        std_pred = predictions.std(axis=0)    # (C,)
        
        # Ensemble prediction (average probability)
        ensemble_class = mean_pred.argmax()
        ensemble_confidence = mean_pred[ensemble_class]
        
        # Uncertainty metrics
        entropy = -np.sum(mean_pred * np.log(mean_pred + 1e-10))  # [0, log(C)]
        normalized_entropy = entropy / np.log(len(mean_pred))  # [0, 1]
        
        # Epistemic uncertainty (model/reducible):
        # Variance of predicted class across samples
        epistemic = std_pred[ensemble_class]
        
        # Aleatoric uncertainty (data/irreducible):
        # Expected variance across samples
        aleatoric = predictions.var(axis=0).mean()
        
        # Classify uncertainty level
        if normalized_entropy < 0.3:
            uncertainty_level = 'low'
        elif normalized_entropy < 0.6:
            uncertainty_level = 'moderate'
        else:
            uncertainty_level = 'high'
        
        # Confidence interval (95%)
        z_score = 1.96  # 95% CI
        ci_lower = ensemble_confidence - z_score * epistemic
        ci_upper = ensemble_confidence + z_score * epistemic
        ci_lower = np.clip(ci_lower, 0, 1)
        ci_upper = np.clip(ci_upper, 0, 1)
        
        result = {
            'ensemble_prediction': int(ensemble_class),
            'ensemble_confidence': float(ensemble_confidence),
            'uncertainty': float(normalized_entropy),
            'confidence_interval': (float(ci_lower), float(ci_upper)),
            'epistemic_uncertainty': float(epistemic),
            'aleatoric_uncertainty': float(aleatoric),
            'uncertainty_level': uncertainty_level,
            'mean_probabilities': mean_pred.tolist(),
            'std_probabilities': std_pred.tolist(),
            'entropy': float(entropy),
            'num_samples': self.num_samples,
            'predictions': self._format_predictions(
                predictions, class_names
            )
        }
        
        return result
    
    def _format_predictions(self, predictions: np.ndarray, 
                           class_names: List[str] = None) -> List[Dict]:
        """Format T predictions into readable format"""
        num_classes = predictions.shape[1]
        
        if class_names is None:
            class_names = [f'Class {i}' for i in range(num_classes)]
        
        formatted = []
        for i, pred in enumerate(predictions):
            class_idx = pred.argmax()
            formatted.append({
                'sample': i + 1,
                'predicted_class': int(class_idx),
                'predicted_name': class_names[class_idx],
                'confidence': float(pred[class_idx]),
                'probabilities': pred.tolist()
            })
        
        return formatted


# ============================================================
# BAYESIAN PREDICTION
# ============================================================

class BayesianPredictor:
    """
    Bayesian approach to uncertainty estimation
    Treats model as distribution, not point estimate
    """
    
    def __init__(self, models: List[nn.Module]):
        """
        Args:
            models: List of trained models (ensemble)
        """
        self.models = models
        self.num_models = len(models)
    
    def predict_ensemble(self, 
                        image_tensor: torch.Tensor,
                        class_names: List[str] = None) -> Dict:
        """
        Ensemble prediction from multiple models
        
        Args:
            image_tensor: Input tensor (1, 3, 224, 224)
            class_names: List of class names
            
        Returns:
            Ensemble prediction with uncertainty
        """
        predictions = []
        
        for model in self.models:
            model.eval()
            with torch.no_grad():
                logits = model(image_tensor)
                probs = torch.softmax(logits, dim=1)[0].cpu().numpy()
                predictions.append(probs)
        
        # Convert to array: (M, C)
        predictions = np.array(predictions)
        
        # Mean and std across models
        mean_pred = predictions.mean(axis=0)
        std_pred = predictions.std(axis=0)
        
        # Best prediction
        best_class = mean_pred.argmax()
        best_confidence = mean_pred[best_class]
        
        # Disagreement between models
        disagreement = std_pred[best_class]
        
        # Entropy
        entropy = -np.sum(mean_pred * np.log(mean_pred + 1e-10))
        
        result = {
            'ensemble_prediction': int(best_class),
            'ensemble_confidence': float(best_confidence),
            'model_disagreement': float(disagreement),
            'entropy': float(entropy),
            'num_models': self.num_models,
            'mean_probabilities': mean_pred.tolist(),
            'std_probabilities': std_pred.tolist(),
            'individual_predictions': self._format_model_predictions(
                predictions, class_names
            )
        }
        
        return result
    
    def _format_model_predictions(self, predictions: np.ndarray,
                                  class_names: List[str] = None) -> List[Dict]:
        """Format predictions from each model"""
        num_classes = predictions.shape[1]
        
        if class_names is None:
            class_names = [f'Class {i}' for i in range(num_classes)]
        
        formatted = []
        for i, pred in enumerate(predictions):
            class_idx = pred.argmax()
            formatted.append({
                'model': i + 1,
                'predicted_class': int(class_idx),
                'predicted_name': class_names[class_idx],
                'confidence': float(pred[class_idx]),
                'probabilities': pred.tolist()
            })
        
        return formatted


# ============================================================
# CONFIDENCE CALIBRATION
# ============================================================

class ConfidenceCalibrator:
    """
    Calibrate model confidence to match actual accuracy
    Some models are over/under confident
    """
    
    @staticmethod
    def temperature_scaling(logits: np.ndarray, 
                           temperature: float = 1.0) -> np.ndarray:
        """
        Scale logits by temperature before softmax
        T > 1: flatter distribution (less confident)
        T < 1: sharper distribution (more confident)
        
        Args:
            logits: Raw model outputs
            temperature: Scaling factor
            
        Returns:
            Calibrated probabilities
        """
        scaled_logits = logits / temperature
        return np.exp(scaled_logits) / np.sum(np.exp(scaled_logits))
    
    @staticmethod
    def find_optimal_temperature(logits: np.ndarray, 
                                labels: np.ndarray) -> float:
        """
        Find optimal temperature for calibration using validation data
        
        Args:
            logits: Validation set logits (N, C)
            labels: True labels (N,)
            
        Returns:
            Optimal temperature
        """
        def nll_loss(T):
            """Negative log likelihood with temperature T"""
            probs = np.exp(logits / T) / np.sum(np.exp(logits / T), axis=1, keepdims=True)
            nll = -np.mean(np.log(probs[np.arange(len(labels)), labels] + 1e-10))
            return nll
        
        # Grid search
        temps = np.linspace(0.1, 5.0, 50)
        losses = [nll_loss(T) for T in temps]
        
        optimal_temp = temps[np.argmin(losses)]
        return optimal_temp


# ============================================================
# UNCERTAINTY-AWARE DECISION MAKING
# ============================================================

class UncertaintyAwareDecision:
    """
    Use uncertainty to make better decisions:
    - Flag uncertain predictions for manual review
    - Adjust confidence thresholds
    - Suggest additional tests
    """
    
    @staticmethod
    def get_recommendation(prediction: int,
                          confidence: float,
                          uncertainty: float,
                          class_names: List[str] = None) -> Dict:
        """
        Generate clinical recommendation based on prediction and uncertainty
        
        Args:
            prediction: Predicted class
            confidence: Prediction confidence [0, 1]
            uncertainty: Normalized uncertainty [0, 1]
            class_names: Class names
            
        Returns:
            {
                'recommendation': str,
                'action': str,
                'confidence_level': 'high' | 'moderate' | 'low',
                'suggested_next_step': str
            }
        """
        class_names = class_names or ['Glioma', 'Meningioma', 'Pituitary', 'No Tumor']
        
        # Determine confidence level
        if confidence > 0.9 and uncertainty < 0.2:
            conf_level = 'high'
        elif confidence > 0.7 and uncertainty < 0.5:
            conf_level = 'moderate'
        else:
            conf_level = 'low'
        
        # Determine action
        if conf_level == 'high':
            action = f"CONFIDENT: {class_names[prediction]} detected"
            next_step = "Proceed with clinical protocols for this condition"
        elif conf_level == 'moderate':
            action = f"LIKELY: {class_names[prediction]} detected"
            next_step = "Review imaging with radiologist; consider additional tests"
        else:
            action = f"UNCERTAIN: {class_names[prediction]} suggested"
            next_step = "MANUAL REVIEW REQUIRED; Get second opinion; Additional imaging"
        
        return {
            'recommendation': action,
            'action': action,
            'confidence_level': conf_level,
            'suggested_next_step': next_step,
            'confidence_score': float(confidence),
            'uncertainty_score': float(uncertainty)
        }


# ============================================================
# USAGE EXAMPLE
# ============================================================

if __name__ == '__main__':
    """
    import torch
    from pathlib import Path
    
    # Example 1: MC Dropout
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = load_model('cnn_best.pth').to(device)
    
    # Load image
    image = Image.open('path/to/mri.jpg').convert('RGB')
    image_array = np.array(image)
    image_tensor = preprocess_image(image_array).unsqueeze(0).to(device)
    
    # Get predictions with uncertainty
    mc_dropout = MCDropout(model, num_samples=30)
    result = mc_dropout.predict_with_uncertainty(image_tensor)
    
    print(f"Prediction: {result['ensemble_prediction']}")
    print(f"Confidence: {result['ensemble_confidence']:.2%}")
    print(f"Uncertainty: {result['uncertainty']:.2%}")
    print(f"Level: {result['uncertainty_level']}")
    
    # Example 2: Ensemble Bayesian
    models = [
        load_model('cnn_best.pth'),
        load_model('resnet_best.pth'),
        load_model('vit_best.pth')
    ]
    
    bayesian = BayesianPredictor(models)
    result = bayesian.predict_ensemble(image_tensor)
    
    print(f"Ensemble Prediction: {result['ensemble_prediction']}")
    print(f"Model Disagreement: {result['model_disagreement']:.2%}")
    
    # Example 3: Recommendation
    rec = UncertaintyAwareDecision.get_recommendation(
        prediction=result['ensemble_prediction'],
        confidence=result['ensemble_confidence'],
        uncertainty=result.get('uncertainty', 0.5),
        class_names=['Glioma', 'Meningioma', 'Pituitary', 'No Tumor']
    )
    
    print(f"Recommendation: {rec['recommendation']}")
    print(f"Next Step: {rec['suggested_next_step']}")
    """
    pass