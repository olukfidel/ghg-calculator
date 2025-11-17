"""
Database Seeding Script.

This file provides a Flask CLI command `flask seed_db` to
pre-populate the `EmissionFactor` table with realistic data.
"""

import click
from . import db
from .models import EmissionFactor

# A list of realistic emission factors
# Sources: EPA, DEFRA, etc. (values are illustrative)
SEED_DATA = [
    # --- Scope 1 ---
    {'name': 'Natural Gas', 'category': 'Fuel', 'scope': 1, 'factor_value': 0.183, 'unit': 'kWh', 'co2e_unit': 'kg CO2e', 'source': 'DEFRA 2023'},
    {'name': 'Natural Gas', 'category': 'Fuel', 'scope': 1, 'factor_value': 2.045, 'unit': 'cubic_meter', 'co2e_unit': 'kg CO2e', 'source': 'DEFRA 2023'},
    {'name': 'Diesel (100% mineral)', 'category': 'Fuel', 'scope': 1, 'factor_value': 2.680, 'unit': 'liter', 'co2e_unit': 'kg CO2e', 'source': 'EPA 2023'},
    {'name': 'Petrol (100% mineral)', 'category': 'Fuel', 'scope': 1, 'factor_value': 2.330, 'unit': 'liter', 'co2e_unit': 'kg CO2e', 'source': 'EPA 2023'},
    {'name': 'Company Car (Average, Petrol)', 'category': 'Vehicles', 'scope': 1, 'factor_value': 0.170, 'unit': 'km', 'co2e_unit': 'kg CO2e', 'source': 'DEFRA 2023'},
    {'name': 'Company Car (Average, Diesel)', 'category': 'Vehicles', 'scope': 1, 'factor_value': 0.165, 'unit': 'km', 'co2e_unit': 'kg CO2e', 'source': 'DEFRA 2023'},
    {'name': 'Company Van (Average)', 'category': 'Vehicles', 'scope': 1, 'factor_value': 0.250, 'unit': 'km', 'co2e_unit': 'kg CO2e', 'source': 'DEFRA 2023'},

    # --- Scope 2 ---
    {'name': 'Grid Electricity (US Average)', 'category': 'Electricity', 'scope': 2, 'factor_value': 0.371, 'unit': 'kWh', 'co2e_unit': 'kg CO2e', 'source': 'EPA eGRID 2023'},
    {'name': 'Grid Electricity (UK Average)', 'category': 'Electricity', 'scope': 2, 'factor_value': 0.212, 'unit': 'kWh', 'co2e_unit': 'kg CO2e', 'source': 'DEFRA 2023'},
    {'name': 'Grid Electricity (Germany)', 'category': 'Electricity', 'scope': 2, 'factor_value': 0.434, 'unit': 'kWh', 'co2e_unit': 'kg CO2e', 'source': 'UBA 2023'},
    {'name': 'Grid Electricity (France)', 'category': 'Electricity', 'scope': 2, 'factor_value': 0.055, 'unit': 'kWh', 'co2e_unit': 'kg CO2e', 'source': 'ADEME 2023'},

    # --- Scope 3 ---
    {'name': 'Employee Commuting (Car)', 'category': 'Commuting', 'scope': 3, 'factor_value': 0.168, 'unit': 'km', 'co2e_unit': 'kg CO2e', 'source': 'DEFRA 2023'},
    {'name': 'Employee Commuting (Bus)', 'category': 'Commuting', 'scope': 3, 'factor_value': 0.103, 'unit': 'km', 'co2e_unit': 'kg CO2e', 'source': 'DEFRA 2023'},
    {'name': 'Employee Commuting (Rail)', 'category': 'Commuting', 'scope': 3, 'factor_value': 0.035, 'unit': 'km', 'co2e_unit': 'kg CO2e', 'source': 'DEFRA 2023'},
    {'name': 'Business Travel (Air, Short-haul)', 'category': 'Business Travel', 'scope': 3, 'factor_value': 0.150, 'unit': 'km', 'co2e_unit': 'kg CO2e', 'source': 'DEFRA 2023'},
    {'name': 'Business Travel (Air, Long-haul)', 'category': 'Business Travel', 'scope': 3, 'factor_value': 0.110, 'unit': 'km', 'co2e_unit': 'kg CO2e', 'source': 'DEFRA 2023'},
    {'name': 'Business Travel (Rail, Eurostar)', 'category': 'Business Travel', 'scope': 3, 'factor_value': 0.004, 'unit': 'km', 'co2e_unit': 'kg CO2e', 'source': 'DEFRA 2023'},
    {'name': 'Waste to Landfill', 'category': 'Waste', 'scope': 3, 'factor_value': 0.580, 'unit': 'tonne', 'co2e_unit': 'kg CO2e', 'source': 'EPA WARM 2023'},
    {'name': 'Waste Recycled', 'category': 'Waste', 'scope': 3, 'factor_value': 0.020, 'unit': 'tonne', 'co2e_unit': 'kg CO2e', 'source': 'EPA WARM 2023'},
    {'name': 'Water Supply', 'category': 'Water', 'scope': 3, 'factor_value': 0.298, 'unit': 'cubic_meter', 'co2e_unit': 'kg CO2e', 'source': 'DEFRA 2023'},
]

@click.command(name='seed_db')
def seed_db_command():
    """
    Seeds the database with emission factors.
    
    This command clears the existing EmissionFactor table and
    populates it with the data from SEED_DATA.
    """
    try:
        # Clear existing data
        db.session.query(EmissionFactor).delete()
        db.session.commit()
        
        click.echo('Seeding emission factors...')
        
        # Add new data
        for item in SEED_DATA:
            factor = EmissionFactor(
                name=item['name'],
                category=item['category'],
                scope=item['scope'],
                factor_value=item['factor_value'],
                unit=item['unit'],
                co2e_unit=item['co2e_unit'],
                source=item['source']
            )
            db.session.add(factor)
        
        # Commit the session
        db.session.commit()
        
        click.echo(f'Successfully seeded {len(SEED_DATA)} emission factors.')
        
    except Exception as e:
        db.session.rollback()
        click.echo(f'Error seeding database: {str(e)}')