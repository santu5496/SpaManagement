"""
Enhanced Packages views and routes with session tracking and validity management
"""
from flask import render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_required, current_user
from app import app, db
from forms import PackageForm
from models import Package, PackageService, ClientPackage, Service
from .packages_queries import (
    get_all_packages, get_package_by_id, create_package, update_package,
    delete_package, get_client_packages, assign_package_to_client,
    get_package_services, add_service_to_package, get_available_services,
    track_package_usage, auto_expire_packages, export_packages_csv,
    export_package_usage_csv
)

@app.route('/packages')
@login_required
def packages():
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    # Auto-expire packages based on validity
    auto_expire_packages()
    
    packages_list = get_all_packages()
    services = get_available_services()
    client_packages = get_client_packages()
    
    form = PackageForm()
    
    return render_template('packages.html',
                         packages=packages_list,
                         services=services,
                         client_packages=client_packages,
                         form=form)

@app.route('/packages/create', methods=['POST'])
@login_required
def create_package_route():
    """Create new package with multiple services and session tracking"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('packages'))
    
    form = PackageForm()
    if form.validate_on_submit():
        try:
            # Create package
            package_data = {
                'name': form.name.data,
                'description': form.description.data,
                'total_sessions': form.total_sessions.data,
                'validity_days': form.validity_days.data,
                'total_price': form.total_price.data,
                'discount_percentage': form.discount_percentage.data or 0.0,
                'is_active': form.is_active.data
            }
            
            package = create_package(package_data, form.included_services.data)
            flash(f'Package "{package.name}" created successfully with {len(form.included_services.data)} services', 'success')
            
        except Exception as e:
            flash(f'Error creating package: {str(e)}', 'danger')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash(f'{field}: {error}', 'danger')
    
    return redirect(url_for('packages'))

@app.route('/packages/<int:package_id>/edit', methods=['POST'])
@login_required
def edit_package(package_id):
    """Edit package"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('packages'))
    
    package = get_package_by_id(package_id)
    if not package:
        flash('Package not found', 'danger')
        return redirect(url_for('packages'))
    
    form = PackageForm()
    if form.validate_on_submit():
        try:
            package_data = {
                'name': form.name.data,
                'description': form.description.data,
                'total_sessions': form.total_sessions.data,
                'validity_days': form.validity_days.data,
                'total_price': form.total_price.data,
                'discount_percentage': form.discount_percentage.data or 0.0,
                'is_active': form.is_active.data
            }
            
            update_package(package_id, package_data, form.included_services.data)
            flash(f'Package "{package.name}" updated successfully', 'success')
            
        except Exception as e:
            flash(f'Error updating package: {str(e)}', 'danger')
    
    return redirect(url_for('packages'))

@app.route('/packages/<int:package_id>/delete', methods=['POST'])
@login_required
def delete_package_route(package_id):
    """Delete package"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('packages'))
    
    try:
        result = delete_package(package_id)
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'warning')
    except Exception as e:
        flash(f'Error deleting package: {str(e)}', 'danger')
    
    return redirect(url_for('packages'))

@app.route('/packages/<int:package_id>/assign', methods=['POST'])
@login_required
def assign_package_route(package_id):
    """Assign package to client"""
    if not current_user.can_access('packages'):
        return jsonify({'success': False, 'message': 'Access denied'})
    
    try:
        client_id = request.json.get('client_id')
        if not client_id:
            return jsonify({'success': False, 'message': 'Client ID required'})
        
        client_package = assign_package_to_client(client_id, package_id)
        return jsonify({
            'success': True, 
            'message': 'Package assigned successfully',
            'client_package_id': client_package.id
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/packages/usage/<int:client_package_id>')
@login_required
def package_usage_details(client_package_id):
    """View detailed package usage for a client"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('packages'))
    
    try:
        usage_data = track_package_usage(client_package_id)
        return render_template('package_usage.html', usage_data=usage_data)
    except Exception as e:
        flash(f'Error retrieving package usage: {str(e)}', 'danger')
        return redirect(url_for('packages'))

@app.route('/packages/export')
@login_required
def export_packages():
    """Export packages to CSV"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('packages'))
    
    try:
        csv_data = export_packages_csv()
        response = make_response(csv_data)
        response.headers['Content-Disposition'] = 'attachment; filename=packages.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response
    except Exception as e:
        flash(f'Error exporting packages: {str(e)}', 'danger')
        return redirect(url_for('packages'))

@app.route('/packages/usage/export')
@login_required
def export_package_usage():
    """Export package usage data to CSV"""
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('packages'))
    
    try:
        csv_data = export_package_usage_csv()
        response = make_response(csv_data)
        response.headers['Content-Disposition'] = 'attachment; filename=package_usage.csv'
        response.headers['Content-Type'] = 'text/csv'
        return response
    except Exception as e:
        flash(f'Error exporting package usage: {str(e)}', 'danger')
        return redirect(url_for('packages'))
        if package:
            flash('Package created successfully', 'success')
        else:
            flash('Failed to create package', 'danger')
    
    return redirect(url_for('packages'))

@app.route('/packages/assign/<int:package_id>/<int:client_id>', methods=['POST'])
@login_required
def assign_package_route(package_id, client_id):
    if not current_user.can_access('packages'):
        flash('Access denied', 'danger')
        return redirect(url_for('dashboard'))
    
    client_package = assign_package_to_client(client_id, package_id)
    if client_package:
        flash('Package assigned to client successfully!', 'success')
    else:
        flash('Error assigning package', 'danger')
    
    return redirect(url_for('packages'))