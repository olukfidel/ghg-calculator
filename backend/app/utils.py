"""
Utility Functions.

This file holds utility functions, primarily for handling
unit conversions using the Pint library.
"""

from pint import UnitRegistry, UndefinedUnitError, DimensionalityError

# Initialize the unit registry
# This object understands units and their conversions
ureg = UnitRegistry()

# Define common quantity aliases
ureg.define('gallon = 3.78541 * liter = gal')
ureg.define('US_gallon = gallon')
ureg.define('tonne = 1000 * kilogram = t')
ureg.define('metric_ton = tonne')
ureg.define('MWh = 1000 * kWh')
ureg.define('cubic_meter = 1000 * liter = m^3')

def convert_units(value, from_unit, to_unit):
    """
    Converts a value from one unit to another using Pint.
    
    Args:
        value (float): The numerical value to convert.
        from_unit (str): The unit of the input value (e.g., "gallon").
        to_unit (str): The target unit (e.g., "liter").
        
    Returns:
        float: The converted value.
        
    Raises:
        ValueError: If units are incompatible or undefined.
    """
    if from_unit == to_unit:
        return value
        
    try:
        # Create a "Quantity" object (value + unit)
        quantity = value * ureg(from_unit)
        
        # Convert to the target unit
        converted_quantity = quantity.to(ureg(to_unit))
        
        # Return just the magnitude (the float value)
        return converted_quantity.magnitude
        
    except UndefinedUnitError as e:
        raise ValueError(f"Unit conversion error: Unit not defined. {str(e)}")
    except DimensionalityError as e:
        raise ValueError(f"Unit conversion error: Cannot convert from '{from_unit}' to '{to_unit}'. {str(e)}")
    except Exception as e:
        raise ValueError(f"An unexpected error occurred during unit conversion: {str(e)}")