"""
Core Business Logic (Service Layer).

This file contains the `CalculationService` which handles the core
business logic for calculating emissions and generating reports.
It uses Pandas for data aggregation and `utils.py` (Pint) for
unit conversions.
"""

import pandas as pd
from . import db
from .models import UserInput, EmissionFactor, Report, User
from .utils import convert_units
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

class CalculationService:
    """
    A service class for handling GHG emissions calculations and reporting.
    """

    def calculate_single_input(self, user_input_data, user_id):
        """
        Calculates emissions for a single user activity input and saves it.
        
        Args:
            user_input_data (dict): Data from the API request.
                                    Expected keys: 'factor_id', 'activity_value',
                                    'activity_unit', 'date_period_start'.
            user_id (int): The ID of the authenticated user.
            
        Returns:
            UserInput: The newly created and saved UserInput object.
            
        Raises:
            ValueError: If calculation or unit conversion fails.
        """
        try:
            factor_id = user_input_data['factor_id']
            activity_value = float(user_input_data['activity_value'])
            activity_unit = user_input_data['activity_unit']
            
            # 1. Fetch the corresponding emission factor
            factor = EmissionFactor.query.get(factor_id)
            if not factor:
                raise ValueError(f"EmissionFactor with id {factor_id} not found.")

            # 2. Perform unit conversion if necessary
            converted_value = convert_units(
                value=activity_value,
                from_unit=activity_unit,
                to_unit=factor.unit
            )

            # 3. Calculate emissions
            # (e.g., 37.85 L * 2.68 kg CO2e/L = 101.458 kg CO2e)
            calculated_emissions = converted_value * factor.factor_value
            
            # TODO: Handle conversion if factor.co2e_unit is not 'kg CO2e'
            # For now, we assume all results are stored as kg.

            # 4. Create and save the UserInput record
            new_input = UserInput(
                user_id=user_id,
                factor_id=factor_id,
                activity_value=activity_value,
                activity_unit=activity_unit,
                date_period_start=datetime.fromisoformat(user_input_data['date_period_start']).date(),
                calculated_emissions_kg=calculated_emissions
            )
            
            db.session.add(new_input)
            db.session.commit()
            
            return new_input

        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")
        except Exception as e:
            db.session.rollback()
            # Re-raise to be caught by the API route
            raise ValueError(str(e))


    def generate_report(self, user_id, report_name, start_date, end_date):
        """
        Generates an aggregated report for a user over a date range and saves it.
        
        Args:
            user_id (int): The user's ID.
            report_name (str): The name for the new report.
            start_date (date): The start date of the reporting period.
            end_date (date): The end date of the reporting period.
            
        Returns:
            Report: The newly created and saved Report object.
        """
        try:
            # 1. Query all UserInputs for the user in the date range.
            # We join with EmissionFactor to get the 'scope'.
            query = db.session.query(
                UserInput.calculated_emissions_kg,
                EmissionFactor.scope
            ).join(
                EmissionFactor, UserInput.factor_id == EmissionFactor.id
            ).filter(
                UserInput.user_id == user_id,
                UserInput.date_period_start >= start_date,
                UserInput.date_period_start <= end_date
            )

            # 2. Load data into a Pandas DataFrame
            # --- START OF FIX ---
            # We explicitly pass the SQLAlchemy engine (`db.engine`)
            # instead of `db.session.bind` to avoid ambiguity.
            df = pd.read_sql(query.statement, con=db.engine)
            # --- END OF FIX ---
            
            if df.empty:
                # Create an empty report
                totals = {1: 0.0, 2: 0.0, 3: 0.0}
            else:
                # 3. Aggregate using Pandas
                scope_totals = df.groupby('scope')['calculated_emissions_kg'].sum()
                # Convert to dictionary, fill missing scopes with 0
                totals = {
                    1: scope_totals.get(1, 0.0),
                    2: scope_totals.get(2, 0.0),
                    3: scope_totals.get(3, 0.0)
                }

            total_all_scopes = sum(totals.values())

            # 4. Create and save the Report object
            new_report = Report(
                user_id=user_id,
                report_name=report_name,
                start_date=start_date,
                end_date=end_date,
                total_scope1_kg=totals[1],
                total_scope2_kg=totals[2],
                total_scope3_kg=totals[3],
                total_all_scopes_kg=total_all_scopes
            )
            
            db.session.add(new_report)
            db.session.commit()
            
            return new_report
            
        except SQLAlchemyError as e:
            db.session.rollback()
            raise ValueError(f"Database error: {str(e)}")
        except Exception as e:
            db.session.rollback()
            raise ValueError(str(e))
            
    def get_dashboard_summary(self, user_id):
        """
        Generates high-level summary data for the user's dashboard.
        
        Args:
            user_id (int): The user's ID.
            
        Returns:
            dict: A dictionary containing dashboard data.
        """
        
        # 1. Get Scope Totals
        query = db.session.query(
            EmissionFactor.scope,
            db.func.sum(UserInput.calculated_emissions_kg).label('total_emissions')
        ).join(
            EmissionFactor, UserInput.factor_id == EmissionFactor.id
        ).filter(
            UserInput.user_id == user_id
        ).group_by(
            EmissionFactor.scope
        )
        
        scope_totals = {row.scope: row.total_emissions for row in query.all()}
        
        # 2. Get Time Series Data (e.g., last 12 months)
        # This query groups by year and month
        time_series_query = db.session.query(
            db.func.date_trunc('month', UserInput.date_period_start).label('month'),
            db.func.sum(UserInput.calculated_emissions_kg).label('total_emissions')
        ).filter(
            UserInput.user_id == user_id
        ).group_by(
            'month'
        ).order_by(
            'month'
        )
        
        time_series = [
            {'month': row.month.strftime('%Y-%m'), 'total_emissions': row.total_emissions}
            for row in time_series_query.all()
        ]
        
        return {
            'scope_summary': {
                'scope1': scope_totals.get(1, 0.0),
                'scope2': scope_totals.get(2, 0.0),
                'scope3': scope_totals.get(3, 0.0),
                'total': sum(scope_totals.values())
            },
            'time_series': time_series
        }