# Testing Guide

## Test Structure

The project uses pytest for professional testing:

```
tests/
├── __init__.py
├── requirements-test.txt      # Test dependencies
├── test_inference_service.py  # Main test suite
└── conftest.py               # Shared fixtures (if needed)
```

## Running Tests

### Install test dependencies:
```bash
pip install -r tests/requirements-test.txt
```

### Run all tests:
```bash
pytest
```

### Run with coverage:
```bash
pytest --cov=api --cov-report=html
```

### Run specific test categories:
```bash
# Core functionality only (fast)
pytest -m "not integration"

# Integration tests (requires full dependencies)
pytest -m integration

# Specific test class
pytest tests/test_inference_service.py::TestXceptionPreprocessing
```

## Test Categories

1. **Unit Tests**: Fast, isolated tests of individual functions
2. **Integration Tests**: Tests that require model files and external dependencies
3. **Clinical Validation**: Tests using real dermatological images

## Coverage Goals

- Core functions: 100% coverage
- Integration paths: 90% coverage
- Error handling: 80% coverage

## Adding New Tests

When adding features, include:
- Unit tests for new functions
- Integration tests for end-to-end workflows
- Clinical validation for medical accuracy
- Performance benchmarks for critical paths