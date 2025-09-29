from dataclasses import dataclass

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
