"""
API Endpoints.

This file defines the RESTful API routes for the application, excluding auth routes.
All routes here are protected and require a valid JWT.
"""

from flask import Blueprint, request, jsonify
from . import db
from .models import EmissionFactor, UserInput, Report
from .auth import token_required
from .services import CalculationService
from datetime import datetime

# Define the Blueprint for API routes
api = Blueprint('api', __name__)

# Instantiate the service
calc_service = CalculationService()


# --- Emission Factor Routes ---

@api.route('/factors', methods=['GET'])
@token_required
def get_factors(current_user):
    """
    Get all available emission factors.
    Used to populate dropdowns in the frontend.
    """
    try:
        factors = EmissionFactor.query.order_by(EmissionFactor.category, EmissionFactor.name).all()
        return jsonify([factor.to_dict() for factor in factors]), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching factors: {str(e)}'}), 500

@api.route('/factors', methods=['POST'])
@token_required
def add_factor(current_user):
    """
    (Admin) Add a new emission factor.
    Note: In a real app, you'd add an admin role check.
    """
    # if not current_user.is_admin:
    #     return jsonify({'message': 'Admin access required.'}), 403
        
    data = request.get_json()
    try:
        new_factor = EmissionFactor(
            name=data['name'],
            category=data['category'],
            scope=data['scope'],
            factor_value=data['factor_value'],
            unit=data['unit'],
            co2e_unit=data.get('co2e_unit', 'kg CO2e'),
            source=data.get('source')
        )
        db.session.add(new_factor)
        db.session.commit()
        return jsonify(new_factor.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'message': f'Error adding factor: {str(e)}'}), 400


# --- Data Input Routes ---

@api.route('/inputs', methods=['POST'])
@token_required
def submit_input(current_user):
    """
    Submit a new activity input.
    This endpoint calls the CalculationService.
    """
    data = request.get_json()
    
    # Basic validation
    required_fields = ['factor_id', 'activity_value', 'activity_unit', 'date_period_start']
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'Missing required fields.'}), 400

    try:
        # Use the service to handle calculation and saving
        new_input = calc_service.calculate_single_input(data, current_user.id)
        return jsonify(new_input.to_dict()), 201
        
    except ValueError as e:
        # Catch errors from the service (e.g., unit conversion)
        return jsonify({'message': str(e)}), 400
    except Exception as e:
        return jsonify({'message': f'An unexpected error occurred: {str(e)}'}), 500


@api.route('/inputs', methods=['GET'])
@token_required
def get_inputs(current_user):
    """
    Get historical user inputs, with pagination.
    """
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    
    try:
        inputs_pagination = UserInput.query.filter_by(
            user_id=current_user.id
        ).order_by(
            UserInput.date_period_start.desc(), UserInput.created_at.desc()
        ).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'inputs': [input_item.to_dict() for input_item in inputs_pagination.items],
            'total_pages': inputs_pagination.pages,
            'current_page': inputs_pagination.page,
            'total_items': inputs_pagination.total
        }), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching inputs: {str(e)}'}), 500


# --- Reporting & Dashboard Routes ---

@api.route('/dashboard/summary', methods=['GET'])
@token_required
def get_dashboard_summary(current_user):
    """
    Get high-level stats for the dashboard.
    """
    try:
        summary_data = calc_service.get_dashboard_summary(current_user.id)
        return jsonify(summary_data), 200
    except Exception as e:
        return jsonify({'message': f'Error fetching dashboard data: {str(e)}'}), 500


@api.route('/reports', methods=['POST'])
@token_required
def generate_report(current_user):
    """
    Generate a new aggregated report for a date range.
    """
    data = request.get_json()

    # --- START OF DEBUGGING ---
    print(f"\n--- GENERATE REPORT: RECEIVED DATA ---")
    print(f"Data type: {type(data)}")
    print(f"Data content: {data}")
    print(f"----------------------------------------\n")
    # --- END OF DEBUGGING ---

    # Basic validation
    required_fields = ['report_name', 'start_date', 'end_date']
    
    # Add a check for 'data' being None or not a dict
    if not isinstance(data, dict):
        print("--- GENERATE REPORT: FAILED (data is not a dictionary) ---")
        return jsonify({'message': 'Invalid JSON payload received.'}), 400
        
    if not all(field in data for field in required_fields):
        print(f"--- GENERATE REPORT: FAILED (Missing fields) ---")
        print(f"Required: {required_fields}")
        print(f"Got keys: {list(data.keys()) if data else 'None'}")
        return jsonify({'message': 'Missing required fields.'}), 400

    try:
        start_date = datetime.fromisoformat(data['start_date']).date()
        end_date = datetime.fromisoformat(data['end_date']).date()

        # Use the service to generate and save the report
        new_report = calc_service.generate_report(
            user_id=current_user.id,
            report_name=data['report_name'],
            start_date=start_date,
            end_date=end_date
        )
        print("--- GENERATE REPORT: SUCCESS ---")
        return jsonify(new_report.to_dict()), 201
        
    except ValueError as e:
        # Catch date formatting errors
        print(f"--- GENERATE REPORT: FAILED (Date format error) ---")
        print(f"Error: {str(e)}")
        return jsonify({'message': f'Date format error: {str(e)}. Please use YYYY-MM-DD.'}), 400
    except Exception as e:
        print(f"--- GENERATE REPORT: FAILED (Unexpected error) ---")
        print(f"Error: {str(e)}")
        db.session.rollback()
        return jsonify({'message': f'An unexpected error occurred: {str(e)}'}), 500


@api.route('/reports', methods=['GET'])
@token_required
def get_reports(current_user):
    """
    Get a list of past generated reports.
    """
    try:
        reports = Report.query.filter_by(
            user_id=current_user.id
        ).order_by(
            Report.generated_at.desc()
        ).all()
        
        return jsonify([report.to_dict() for report in reports]), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching reports: {str(e)}'}), 500


@api.route('/reports/<int:report_id>', methods=['GET'])
@token_required
def get_report_details(current_user, report_id):
    """
    Get details for a specific report.
    """
    try:
        report = Report.query.filter_by(
            id=report_id, user_id=current_user.id
        ).first()
        
        if not report:
            return jsonify({'message': 'Report not found or access denied.'}), 404
            
        return jsonify(report.to_dict()), 200
        
    except Exception as e:
        return jsonify({'message': f'Error fetching report details: {str(e)}'}), 500