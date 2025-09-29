from dataclasses import dataclass
from pathlib import Path

@dataclass
class Config:
    WEIGHT_SYMPTOM: float = 1.0
    WEIGHT_LOCATION: float = 2.5
    WEIGHT_MORPHOLOGY: float = 3.5
    WEIGHT_SYSTEMIC: float = 3.5
    WEIGHT_TRIGGER: float = 1.0
    WEIGHT_SPREAD_PATTERN: float = 2.0
    WEIGHT_CONDITION: float = 1.5
    WEIGHT_DURATION: float = 3.0
    WEIGHT_AGE: float = 1.0
    WEIGHT_GENDER: float = 1.0

    BONUS_HISTORY_NAME_MATCH: float = 1.0
    BONUS_SPECIFIC_KEYWORD: float = 4.0

    MODEL_PATH: str = ""
    CLASS_NAMES_PATH: str = ""

    # ML Model Configuration
    def __post_init__(self):
        # Get the API directory path
        api_dir = Path(__file__).parent.parent
        self.MODEL_PATH = str(api_dir / "ml_models" / "quantized_dynamic_range_model.tflite")
        self.CLASS_NAMES_PATH = str(api_dir / "data" / "class_names.txt")
