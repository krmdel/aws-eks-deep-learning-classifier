"""
Tests for model loading and inference.
"""
import pytest
import numpy as np
from app import session, classes, input_name, output_name


def test_model_session_loaded():
    """Test that ONNX model session is loaded."""
    assert session is not None
    assert hasattr(session, 'run')


def test_model_input_output_names():
    """Test that model input and output names are correctly identified."""
    assert input_name is not None
    assert isinstance(input_name, str)
    
    assert output_name is not None
    assert isinstance(output_name, str)


def test_model_classes():
    """Test that all expected classes are defined."""
    expected_classes = [
        "dress", "hat", "longsleeve", "outwear", "pants",
        "shirt", "shoes", "shorts", "skirt", "t-shirt"
    ]
    
    assert len(classes) == 10
    assert set(classes) == set(expected_classes)


def test_model_input_shape():
    """Test that model input shape is correct."""
    inputs = session.get_inputs()
    assert len(inputs) > 0
    
    input_shape = inputs[0].shape
    # Should be [batch, channels, height, width] or [batch, height, width, channels]
    assert len(input_shape) == 4


def test_model_output_shape():
    """Test that model output shape is correct."""
    outputs = session.get_outputs()
    assert len(outputs) > 0
    
    output_shape = outputs[0].shape
    # Should be [batch, num_classes]
    assert len(output_shape) == 2
    assert output_shape[1] == 10  # 10 clothing classes



