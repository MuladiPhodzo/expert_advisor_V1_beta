// ```python
import pytest

from my_module import add


def test_add_positive_numbers():
    """Test that adding two positive numbers returns the correct sum."""
    assert add(1, 2) == 3


def test_add_negative_numbers():
    """Test that adding two negative numbers returns the correct sum."""
    assert add(-1, -2) == -3


def test_add_zero():
    """Test that adding zero to a number returns the original number."""
    assert add(0, 1) == 1
    assert add(1, 0) == 1


def test_add_mixed_numbers():
    """Test that adding a positive and a negative number returns the correct sum."""
    assert add(1, -2) == -1
    assert add(-1, 2) == 1
// ```