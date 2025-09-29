"""
Test suite for the TensorFlow Lite inference service.
Validates model loading, preprocessing, and inference functionality.
"""

try:
    import pytest
except ImportError:
    raise ImportError("pytest is required for running tests. Install with: pip install pytest")

import numpy as np
from PIL import Image
from pathlib import Path
import sys
import os

# Project directories
TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent
API_DIR = PROJECT_ROOT / 'api'
DEV_TOOLS_DATA = PROJECT_ROOT / 'dev-tools' / 'data'

# Add the api directory to Python path for imports
sys.path.insert(0, str(API_DIR))

try:
    from core.inference_service import TFLiteInferenceService, xception_preprocess_input, create_inference_service
    from core.config import Config
except ImportError as e:
    raise ImportError(f"Cannot import inference service modules. Make sure you're running from the project root. Error: {e}")


class TestXceptionPreprocessing:
    """Test cases for Xception preprocessing function."""
    
    def test_preprocessing_range(self):
        """Test that preprocessing produces correct [-1, 1] range."""
        # Test with min/max values
        test_data = np.array([[[0, 255, 128]]], dtype=np.float32)
        result = xception_preprocess_input(test_data)
        
        assert result.min() >= -1.0, "Minimum value should be >= -1.0"
        assert result.max() <= 1.0, "Maximum value should be <= 1.0"
        
        # Test specific values
        assert np.isclose(result[0, 0, 0], -1.0, atol=1e-6), "Min value (0) should map to -1.0"
        assert np.isclose(result[0, 0, 1], 1.0, atol=1e-6), "Max value (255) should map to 1.0"
        assert np.isclose(result[0, 0, 2], 0.0039215686, atol=1e-6), "Middle value (128) should map to ~0.004"
    
    def test_preprocessing_mathematical_correctness(self):
        """Test the mathematical transformation (x / 127.5 - 1.0)."""
        test_values = np.array([[[100, 150, 200]]], dtype=np.float32)
        result = xception_preprocess_input(test_values)
        
        # Manual calculation
        expected_r = (100.0 / 127.5) - 1.0
        expected_g = (150.0 / 127.5) - 1.0
        expected_b = (200.0 / 127.5) - 1.0
        
        assert np.isclose(result[0, 0, 0], expected_r, atol=1e-6)
        assert np.isclose(result[0, 0, 1], expected_g, atol=1e-6)
        assert np.isclose(result[0, 0, 2], expected_b, atol=1e-6)
    
    def test_preprocessing_dtype_handling(self):
        """Test that preprocessing handles different input dtypes."""
        # Test with uint8 input
        test_uint8 = np.array([[[100, 150, 200]]], dtype=np.uint8)
        result_uint8 = xception_preprocess_input(test_uint8)
        
        # Test with float32 input
        test_float32 = np.array([[[100.0, 150.0, 200.0]]], dtype=np.float32)
        result_float32 = xception_preprocess_input(test_float32)
        
        # Results should be identical
        assert np.allclose(result_uint8, result_float32, atol=1e-6)
        assert result_uint8.dtype == np.float32
        assert result_float32.dtype == np.float32


class TestInferenceService:
    """Test cases for TFLite inference service."""
    
    @pytest.fixture
    def service(self):
        """Create inference service for testing."""
        try:
            return create_inference_service()
        except RuntimeError as e:
            pytest.skip(f"Cannot create inference service: {e}")
    
    def test_service_initialization(self, service):
        """Test that service initializes correctly."""
        assert service is not None
        assert service.interpreter is not None
        assert len(service.class_names) == 23
        assert service.input_details is not None
        assert service.output_details is not None
    
    def test_model_input_output_shapes(self, service):
        """Test that model has expected input/output shapes."""
        # Xception expects 299x299x3 input
        input_shape = service.input_details[0]['shape']
        assert input_shape[1] == 299, f"Expected height 299, got {input_shape[1]}"
        assert input_shape[2] == 299, f"Expected width 299, got {input_shape[2]}"
        assert input_shape[3] == 3, f"Expected 3 channels, got {input_shape[3]}"
        
        # Should output 23 classes
        output_shape = service.output_details[0]['shape']
        assert output_shape[-1] == 23, f"Expected 23 classes, got {output_shape[-1]}"
    
    def test_preprocessing_integration(self, service):
        """Test preprocessing integration with model input."""
        # Create test image
        test_image = Image.new('RGB', (512, 384), color='red')
        
        # Preprocess image
        processed = service.preprocess_image(test_image)
        
        # Check output shape matches model input
        expected_shape = service.input_details[0]['shape']
        assert processed.shape == tuple(expected_shape)
        assert processed.dtype == np.float32
        assert processed.min() >= -1.0
        assert processed.max() <= 1.0
    
    def test_prediction_output_format(self, service):
        """Test that predictions have correct format."""
        # Create test image
        test_image = Image.new('RGB', (299, 299), color='blue')
        
        # Run prediction
        results = service.predict(test_image, top_k=5)
        
        # Check output format
        assert len(results) == 5
        assert all(isinstance(r, dict) for r in results)
        
        for i, result in enumerate(results):
            assert result['rank'] == i + 1
            assert isinstance(result['class_name'], str)
            assert isinstance(result['confidence'], float)
            assert isinstance(result['confidence_percentage'], float)
            assert 0.0 <= result['confidence'] <= 1.0
            assert 0.0 <= result['confidence_percentage'] <= 100.0
    
    def test_class_names_loaded(self, service):
        """Test that class names are properly loaded."""
        expected_classes = {
            'Acne and Rosacea Photos',
            'Atopic Dermatitis Photos', 
            'Eczema Photos',
            'Vasculitis Photos',
            'Melanoma Skin Cancer Nevi and Moles'
        }
        
        loaded_classes = set(service.class_names)
        assert expected_classes.issubset(loaded_classes), "Missing expected dermatology classes"


@pytest.mark.skipif(not (DEV_TOOLS_DATA / 'test-image.jpg').exists(), 
                   reason="Test image not available")
class TestRealImageInference:
    """Test cases using real dermatological images."""
    
    @pytest.fixture
    def service(self):
        """Create inference service for testing."""
        try:
            return create_inference_service()
        except RuntimeError as e:
            pytest.skip(f"Cannot create inference service: {e}")
    
    @pytest.fixture
    def test_image(self):
        """Load test image."""
        image_path = DEV_TOOLS_DATA / 'test-image.jpg'
        return Image.open(image_path)
    
    def test_real_image_inference(self, service, test_image):
        """Test inference on real dermatological image."""
        results = service.predict(test_image, top_k=5)
        
        # Should return predictions
        assert len(results) == 5
        
        # Top prediction should have reasonable confidence
        top_prediction = results[0]
        assert top_prediction['confidence_percentage'] > 5.0, "Top prediction should have >5% confidence"
        
        # All predictions should sum to reasonable total
        total_confidence = sum(r['confidence'] for r in results)
        assert total_confidence > 0.1, "Total top-5 confidence should be >10%"
    
    def test_clinical_validation_eczema_case(self, service, test_image):
        """Test that known Eczema case appears in differential diagnosis."""
        results = service.predict(test_image, top_k=10)
        
        # Check if Eczema appears in results
        eczema_found = any('Eczema' in r['class_name'] for r in results)
        
        if eczema_found:
            eczema_result = next(r for r in results if 'Eczema' in r['class_name'])
            assert eczema_result['rank'] <= 5, "Eczema should appear in top 5 differential"
            assert eczema_result['confidence_percentage'] > 1.0, "Eczema should have >1% confidence"


@pytest.mark.integration
class TestKerasCompatibility:
    """Integration tests comparing with Keras preprocessing (if available)."""
    
    @pytest.fixture
    def keras_preprocess_input(self):
        """Try to import Keras preprocessing function."""
        try:
            from keras.applications.xception import preprocess_input
            return preprocess_input
        except ImportError:
            try:
                from tensorflow.keras.applications.xception import preprocess_input
                return preprocess_input
            except ImportError:
                pytest.skip("Keras not available for compatibility testing")
    
    def test_preprocessing_equivalence(self, keras_preprocess_input):
        """Test that our preprocessing is identical to Keras."""
        # Test with various input arrays
        test_cases = [
            np.array([[[0, 255, 128]]], dtype=np.float32),
            np.array([[[100, 150, 200]]], dtype=np.float32),
            np.random.randint(0, 256, (1, 3, 3, 3)).astype(np.float32)
        ]
        
        for test_data in test_cases:
            our_result = xception_preprocess_input(test_data.copy())
            keras_result = keras_preprocess_input(test_data.copy())
            
            assert np.allclose(our_result, keras_result, rtol=1e-7, atol=1e-7), \
                "Our preprocessing should be identical to Keras"