"""
TensorFlow Lite Inference Service for Dermatological Condition Classification

This service handles loading the TFLite model, preprocessing images, and running inference
for the hybrid AI dermatology diagnostic tool.

Uses the same preprocessing as keras.applications.xception.preprocess_input for consistency
with the original training pipeline.
"""

import tensorflow as tf
import numpy as np
from PIL import Image
from typing import List, Dict, Any, Optional
import logging
from pathlib import Path

from .config import Config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def xception_preprocess_input(x: np.ndarray) -> np.ndarray:
    """
    Preprocesses a numpy array encoding an image for Xception model.
    
    This function implements the same preprocessing as:
    keras.applications.xception.preprocess_input
    
    The pixel values are scaled from [0, 255] to the [-1, 1] range, matching
    keras.applications.xception.preprocess_input exactly.
    
    Args:
        x: Input array with shape (batch_size, height, width, channels)
        
    Returns:
        Preprocessed array with the same shape as input
    """
    # Ensure input is float32
    x = x.astype(np.float32)
    
    # Scale to [-1, 1] range (this is what Xception preprocess_input does)
    x = x / 127.5 - 1.0
    
    return x


class TFLiteInferenceService:
    """Service for TensorFlow Lite model inference on dermatological images."""
    
    def __init__(self, config: Config):
        self.config = config
        self.interpreter: Optional[tf.lite.Interpreter] = None
        self.class_names: List[str] = []
        self.input_details: Optional[List[Dict[str, Any]]] = None
        self.output_details: Optional[List[Dict[str, Any]]] = None
        
    def load_model_and_classes(self) -> bool:
        """
        Load the TFLite model and class names from the configured paths.
        
        Returns:
            bool: True if loading successful, False otherwise
        """
        try:
            # Load TensorFlow Lite model
            model_path = Path(self.config.MODEL_PATH)
            if not model_path.exists():
                logger.error(f"Model file not found: {model_path}")
                return False
                
            logger.info(f"Loading TFLite model from: {model_path}")
            self.interpreter = tf.lite.Interpreter(model_path=str(model_path))
            
            # Type guard: ensure interpreter is properly initialized
            if self.interpreter is None:
                logger.error("Failed to initialize TensorFlow Lite interpreter")
                return False
                
            self.interpreter.allocate_tensors()
            
            # Get input and output details
            self.input_details = self.interpreter.get_input_details()
            self.output_details = self.interpreter.get_output_details()
            
            # Validate that we got the details
            if not self.input_details or not self.output_details:
                logger.error("Failed to get model input/output details")
                return False
            
            logger.info(f"Model input shape: {self.input_details[0]['shape']}")
            logger.info(f"Model output shape: {self.output_details[0]['shape']}")
            
            # Load class names
            class_names_path = Path(self.config.CLASS_NAMES_PATH)
            if not class_names_path.exists():
                logger.error(f"Class names file not found: {class_names_path}")
                return False
                
            logger.info(f"Loading class names from: {class_names_path}")
            with open(class_names_path, 'r', encoding='utf-8') as f:
                self.class_names = [line.strip() for line in f.readlines() if line.strip()]
            
            logger.info(f"Loaded {len(self.class_names)} class names")
            
            # Validate model and class names compatibility
            if self.output_details and len(self.output_details) > 0:
                expected_output_shape = len(self.class_names)
                actual_output_shape = self.output_details[0]['shape'][-1]
                
                if expected_output_shape != actual_output_shape:
                    logger.warning(
                        f"Class count mismatch: {expected_output_shape} classes, "
                        f"but model outputs {actual_output_shape} values"
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model or class names: {str(e)}")
            return False
    
    def preprocess_image(self, image: Image.Image) -> np.ndarray:
        """
        Preprocess a PIL Image for TFLite model inference using Xception preprocessing.
        
        This method uses the same preprocessing as keras.applications.xception.preprocess_input
        to ensure consistency with the original model training pipeline.
        
        Args:
            image (Image.Image): PIL Image to preprocess
            
        Returns:
            np.ndarray: Preprocessed image array ready for inference
        """
        try:
            # Get expected input shape from model
            if self.input_details is None:
                raise RuntimeError("Model not loaded. Call load_model_and_classes() first.")
            input_shape = self.input_details[0]['shape']
            target_size = (input_shape[1], input_shape[2])  # (height, width)
            
            # Resize image to model's expected size (299, 299 for Xception)
            if image.mode != 'RGB':
                image = image.convert('RGB')
                
            image_resized = image.resize(target_size, Image.Resampling.LANCZOS)
            
            # Convert to numpy array
            image_array = np.array(image_resized, dtype=np.float32)
            
            # Add batch dimension
            image_array = np.expand_dims(image_array, axis=0)
            
            # Apply Xception preprocessing (equivalent to keras.applications.xception.preprocess_input)
            image_array = xception_preprocess_input(image_array)
            
            logger.info(f"Xception preprocess_input applied: range [{image_array.min():.3f}, {image_array.max():.3f}]")
            
            return image_array
            
        except Exception as e:
            logger.error(f"Image preprocessing failed: {str(e)}")
            raise ValueError(f"Failed to preprocess image: {str(e)}")
    
    def predict(self, image: Image.Image, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Run inference on a preprocessed image and return top predictions.
        
        Args:
            image (Image.Image): PIL Image for prediction
            top_k (int): Number of top predictions to return (default: 3)
            
        Returns:
            List[Dict[str, Any]]: List of top predictions with class names and confidence scores
        """
        try:
            if self.interpreter is None or self.input_details is None or self.output_details is None:
                raise RuntimeError("Model not loaded. Call load_model_and_classes() first.")
            
            # Preprocess the image
            processed_image = self.preprocess_image(image)
            
            # Set the input tensor
            self.interpreter.set_tensor(self.input_details[0]['index'], processed_image)
            
            # Run inference
            self.interpreter.invoke()
            
            # Get the output
            output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
            predictions = output_data[0]  # Remove batch dimension
            
            # Get top-k predictions
            top_indices = np.argsort(predictions)[-top_k:][::-1]
            
            results = []
            for i, idx in enumerate(top_indices):
                confidence = float(predictions[idx])
                class_name = self.class_names[idx] if idx < len(self.class_names) else f"Class_{idx}"
                
                results.append({
                    "rank": i + 1,
                    "class_name": class_name,
                    "confidence": confidence,
                    "confidence_percentage": round(confidence * 100, 2)
                })
            
            logger.info(f"Prediction completed. Top prediction: {results[0]['class_name']} ({results[0]['confidence_percentage']:.2f}%)")
            
            return results
            
        except Exception as e:
            logger.error(f"Prediction failed: {str(e)}")
            raise RuntimeError(f"Failed to run prediction: {str(e)}")


# Factory function for easy instantiation
def create_inference_service(config: Optional[Config] = None) -> TFLiteInferenceService:
    """
    Create and initialize a TFLite inference service.
    
    Args:
        config (Config, optional): Configuration object. Creates default if None.
        
    Returns:
        TFLiteInferenceService: Initialized inference service
    """
    if config is None:
        config = Config()
        
    service = TFLiteInferenceService(config)
    
    # Load model and classes on creation
    if not service.load_model_and_classes():
        raise RuntimeError("Failed to initialize inference service: Could not load model or class names")
    
    return service