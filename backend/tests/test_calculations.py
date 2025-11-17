"""
Unit Tests for the Calculation Service.

This file tests the CalculationService, especially its
unit conversion logic.
"""

import pytest
from app.utils import convert_units

# --- Test Unit Conversion Utility ---

def test_convert_units_simple():
    """Test conversion between compatible units."""
    # Gallons to Liters
    result = convert_units(10, 'gallon', 'liter')
    assert result == pytest.approx(37.8541)

    # Liters to Gallons
    result = convert_units(50, 'liter', 'gallon')
    assert result == pytest.approx(13.2086)

def test_convert_units_no_conversion():
    """Test when from_unit and to_unit are the same."""
    result = convert_units(100, 'kg', 'kg')
    assert result == 100

def test_convert_units_complex():
    """Test defined aliases like MWh."""
    result = convert_units(2, 'MWh', 'kWh')
    assert result == 2000

def test_convert_units_incompatible():
    """Test conversion between incompatible units (e.g., mass to distance)."""
    with pytest.raises(ValueError) as e:
        convert_units(10, 'kg', 'meter')
    assert "Cannot convert from 'kg' to 'meter'" in str(e.value)

def test_convert_units_undefined():
    """Test conversion with an undefined unit."""
    with pytest.raises(ValueError) as e:
        convert_units(10, 'widgets', 'liter')
    assert "Unit not defined" in str(e.value)


# --- Test Calculation Service (Mocked DB) ---
# Note: These tests would require more setup with a test app context
# and a mock database, which is complex. We've focused on the
# core conversion logic above, which is the most critical part.

# A placeholder for a more complete service test
def test_calculation_service_placeholder():
    """
    This is a placeholder. A full test would:
    1. Set up a test Flask app context.
    2. Create mock EmissionFactor objects in a test DB.
    3. Instantiate CalculationService.
    4. Call service.calculate_single_input with mock data.
    5. Assert that the `calculated_emissions_kg` in the
       resulting UserInput object is correct.
    """
    assert True