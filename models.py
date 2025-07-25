from datetime import datetime, date, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
import json

# CRUD System Models for Dynamic Configuration
class Role(db.Model):
    """Dynamic roles management"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='user_role', lazy=True, foreign_keys='User.role_id')
    permissions = db.relationship('RolePermission', backref='role', lazy=True, cascade='all, delete-orphan')

class Permission(db.Model):
    """Dynamic permissions management"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    module = db.Column(db.String(50), nullable=False)  # dashboard, staff, clients, etc.
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    role_permissions = db.relationship('RolePermission', backref='permission', lazy=True, cascade='all, delete-orphan')

class RolePermission(db.Model):
    """Many-to-many relationship for roles and permissions"""
    id = db.Column(db.Integer, primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('role_id', 'permission_id'),)

class Category(db.Model):
    """Dynamic categories for services, products, etc."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category_type = db.Column(db.String(50), nullable=False)  # service, product, expense, etc.
    color = db.Column(db.String(7), default='#007bff')  # Hex color for UI
    icon = db.Column(db.String(50), default='fas fa-tag')  # Font Awesome icon
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    services = db.relationship('Service', backref='service_category', lazy=True)
    inventory = db.relationship('Inventory', backref='inventory_category', lazy=True)
    expenses = db.relationship('Expense', backref='expense_category', lazy=True)

class Department(db.Model):
    """Dynamic departments for staff"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    staff = db.relationship('User', backref='staff_department', lazy=True, foreign_keys='User.department_id')
    managed_by = db.relationship('User', backref='managed_departments', lazy=True, foreign_keys='Department.manager_id')

class SystemSetting(db.Model):
    """Dynamic system settings"""
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text)
    data_type = db.Column(db.String(20), default='string')  # string, integer, float, boolean, json
    category = db.Column(db.String(50), nullable=False)  # business, appearance, notifications, etc.
    display_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=False)  # Can be accessed by non-admin users
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256))
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    
    # Dynamic role system
    role_id = db.Column(db.Integer, db.ForeignKey('role.id'), nullable=True)
    role = db.Column(db.String(20), nullable=False, default='staff')  # Fallback for compatibility
    
    phone = db.Column(db.String(20))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Staff-specific fields
    commission_rate = db.Column(db.Float, default=0.0)
    hourly_rate = db.Column(db.Float, default=0.0)
    employee_id = db.Column(db.String(20), unique=True)
    department_id = db.Column(db.Integer, db.ForeignKey('department.id'))
    department = db.Column(db.String(50))  # Fallback for compatibility
    hire_date = db.Column(db.Date)
    
    # Performance tracking
    total_sales = db.Column(db.Float, default=0.0)
    total_clients_served = db.Column(db.Integer, default=0)
    average_rating = db.Column(db.Float, default=0.0)
    
    # Availability and preferences
    work_schedule = db.Column(db.Text)  # JSON for weekly schedule
    specialties = db.Column(db.Text)  # JSON for service specialties
    
    # Relationships
    appointments = db.relationship('Appointment', backref='assigned_staff', lazy=True)
    expenses = db.relationship('Expense', backref='created_by_user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def has_role(self, role):
        # Support both dynamic and legacy role systems
        if self.user_role:
            return self.user_role.name == role
        return self.role == role

    def can_access(self, resource):
        # Admin users have full access - shortcut for efficiency
        if self.role == 'admin' or (self.user_role and self.user_role.name == 'admin'):
            return True
            
        # Dynamic permissions from role-permission system
        if self.user_role:
            user_permissions = [rp.permission.name for rp in self.user_role.permissions if rp.permission.is_active]
            # Check for 'all' permission or specific resource permissions
            if 'all' in user_permissions:
                return True
            # Check for specific resource permissions (e.g., 'clients_view', 'clients_create')
            resource_permissions = [p for p in user_permissions if p.startswith(resource + '_')]
            return len(resource_permissions) > 0 or resource in user_permissions
        
        # Fallback to legacy permissions
        permissions = {
            'admin': ['all'],
            'manager': ['dashboard', 'bookings', 'clients', 'staff', 'billing', 'inventory', 'expenses', 'reports'],
            'staff': ['dashboard', 'bookings', 'clients'],
            'cashier': ['dashboard', 'bookings', 'billing']
        }
        user_role_permissions = permissions.get(self.role, [])
        return 'all' in user_role_permissions or resource in user_role_permissions
    
    def get_role_name(self):
        """Get the role name from dynamic system or fallback"""
        if self.user_role:
            return self.user_role.name
        return self.role

class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, index=True)
    phone = db.Column(db.String(20), nullable=False)
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_visit = db.Column(db.DateTime)
    total_visits = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    
    # Client preferences and notes
    preferences = db.Column(db.Text)
    allergies = db.Column(db.Text)
    notes = db.Column(db.Text)
    face_encoding = db.Column(db.Text)  # Store face encoding as JSON string
    face_image_url = db.Column(db.String(255))  # Store face image path
    
    # Loyalty status
    loyalty_points = db.Column(db.Integer, default=0)
    is_vip = db.Column(db.Boolean, default=False)
    
    # Communication preferences
    preferred_communication = db.Column(db.String(20), default='email')  # email, sms, whatsapp
    marketing_consent = db.Column(db.Boolean, default=True)
    reminder_preferences = db.Column(db.Text)  # JSON for reminder settings
    
    # Advanced client tracking
    referral_source = db.Column(db.String(100))
    lifetime_value = db.Column(db.Float, default=0.0)
    last_no_show = db.Column(db.DateTime)
    no_show_count = db.Column(db.Integer, default=0)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='client', lazy=True)
    packages = db.relationship('ClientPackage', backref='client', lazy=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def status(self):
        if not self.is_active:
            return 'Inactive'
        elif self.last_visit and (datetime.utcnow() - self.last_visit).days > 90:
            return 'Inactive Client'
        elif self.total_visits >= 10:
            return 'Loyal Client'
        else:
            return 'Regular Client'

class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration = db.Column(db.Integer, nullable=False)  # in minutes
    price = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.Column(db.String(50), nullable=False)  # Fallback for compatibility
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    appointments = db.relationship('Appointment', backref='service', lazy=True)
    package_services = db.relationship('PackageService', backref='service', lazy=True)

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default='scheduled')  # scheduled, confirmed, in_progress, completed, cancelled, no_show
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Billing
    amount = db.Column(db.Float)
    discount = db.Column(db.Float, default=0.0)
    tips = db.Column(db.Float, default=0.0)
    is_paid = db.Column(db.Boolean, default=False)

class Package(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    duration_months = db.Column(db.Integer, nullable=False)  # 3, 6, 12 months
    validity_days = db.Column(db.Integer, nullable=False, default=90)  # Validity in days
    total_sessions = db.Column(db.Integer, nullable=False, default=1)  # Total sessions in package
    total_price = db.Column(db.Float, nullable=False)
    discount_percentage = db.Column(db.Float, default=0.0)
    is_active = db.Column(db.Boolean, default=True)
    sort_order = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    services = db.relationship('PackageService', backref='package', lazy=True)
    client_packages = db.relationship('ClientPackage', backref='package', lazy=True)

    @property
    def services_included(self):
        """Get formatted list of services included"""
        return [ps.service.name for ps in self.services if ps.service]

class PackageService(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    sessions_included = db.Column(db.Integer, nullable=False)
    service_discount = db.Column(db.Float, default=0.0)  # Individual service discount percentage
    original_price = db.Column(db.Float, nullable=False)  # Original service price
    discounted_price = db.Column(db.Float, nullable=False)  # Final discounted price

class ClientPackage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('package.id'), nullable=False)
    purchase_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiry_date = db.Column(db.DateTime, nullable=False)
    sessions_used = db.Column(db.Integer, default=0)
    total_sessions = db.Column(db.Integer, nullable=False)
    amount_paid = db.Column(db.Float, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    auto_renewed = db.Column(db.Boolean, default=False)
    renewal_count = db.Column(db.Integer, default=0)
    
    # Service-wise session tracking
    sessions_remaining = db.relationship('ClientPackageSession', backref='client_package', lazy=True)

class ClientPackageSession(db.Model):
    """Track remaining sessions for each service in a client's package"""
    id = db.Column(db.Integer, primary_key=True)
    client_package_id = db.Column(db.Integer, db.ForeignKey('client_package.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    sessions_total = db.Column(db.Integer, nullable=False)
    sessions_used = db.Column(db.Integer, default=0)
    
    @property
    def sessions_remaining(self):
        return max(0, self.sessions_total - self.sessions_used)
    
    # Relationships
    service = db.relationship('Service', backref='client_sessions')

class Inventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.Column(db.String(50), nullable=False)  # Fallback for compatibility
    current_stock = db.Column(db.Integer, default=0)
    min_stock_level = db.Column(db.Integer, default=5)
    unit_price = db.Column(db.Float, default=0.0)
    supplier_name = db.Column(db.String(100))
    supplier_contact = db.Column(db.String(100))
    expiry_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def is_low_stock(self):
        return self.current_stock <= self.min_stock_level

    @property
    def is_expiring_soon(self):
        if not self.expiry_date:
            return False
        days_until_expiry = (self.expiry_date - date.today()).days
        return days_until_expiry <= 30

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.Column(db.String(50), nullable=False)  # Fallback for compatibility
    expense_date = db.Column(db.Date, nullable=False, default=date.today)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receipt_number = db.Column(db.String(50))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_number = db.Column(db.String(20), unique=True, nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    invoice_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime)
    subtotal = db.Column(db.Float, nullable=False)
    tax_amount = db.Column(db.Float, default=0.0)
    discount_amount = db.Column(db.Float, default=0.0)
    tips_amount = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, nullable=False)
    payment_status = db.Column(db.String(20), default='pending')  # pending, paid, overdue
    payment_method = db.Column(db.String(20))  # cash, card, online
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    client = db.relationship('Client', backref='invoices')
    appointment = db.relationship('Appointment', backref='invoice', uselist=False)

class StaffSchedule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)  # 0=Monday, 6=Sunday
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    
    # Relationship
    staff = db.relationship('User', backref='schedules')

# Advanced Models for Real-World Operations

class Review(db.Model):
    """Customer reviews and ratings"""
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    staff = db.relationship('User', backref='reviews')
    service = db.relationship('Service', backref='reviews')
    appointment = db.relationship('Appointment', backref='review', uselist=False)

class Communication(db.Model):
    """Track all communications with clients"""
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # email, sms, whatsapp, call, in_person
    subject = db.Column(db.String(200))
    message = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, sent, delivered, failed
    sent_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    creator = db.relationship('User', backref='communications')

class Commission(db.Model):
    """Track staff commissions and payroll"""
    id = db.Column(db.Integer, primary_key=True)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    appointment_id = db.Column(db.Integer, db.ForeignKey('appointment.id'))
    service_amount = db.Column(db.Float, nullable=False)
    commission_rate = db.Column(db.Float, nullable=False)
    commission_amount = db.Column(db.Float, nullable=False)
    pay_period_start = db.Column(db.Date, nullable=False)
    pay_period_end = db.Column(db.Date, nullable=False)
    is_paid = db.Column(db.Boolean, default=False)
    paid_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    staff = db.relationship('User', backref='commissions')
    appointment = db.relationship('Appointment', backref='commission', uselist=False)

class ProductSale(db.Model):
    """Track retail product sales"""
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    sale_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_method = db.Column(db.String(20))
    is_refunded = db.Column(db.Boolean, default=False)
    
    # Relationships
    product = db.relationship('Inventory', backref='sales')
    client = db.relationship('Client', backref='product_purchases')
    staff = db.relationship('User', backref='product_sales')

class Promotion(db.Model):
    """Marketing promotions and discounts"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    discount_type = db.Column(db.String(20), nullable=False)  # percentage, fixed_amount
    discount_value = db.Column(db.Float, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    usage_limit = db.Column(db.Integer)
    times_used = db.Column(db.Integer, default=0)
    applicable_services = db.Column(db.Text)  # JSON for service IDs
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Waitlist(db.Model):
    """Client waitlist for fully booked times"""
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    preferred_date = db.Column(db.Date, nullable=False)
    preferred_time = db.Column(db.Time)
    is_flexible = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='waiting')  # waiting, contacted, booked, expired
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime)
    
    # Relationships
    client = db.relationship('Client', backref='waitlist_entries')
    service = db.relationship('Service', backref='waitlist_entries')
    staff = db.relationship('User', backref='waitlist_requests')

class RecurringAppointment(db.Model):
    """Recurring appointment templates"""
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    staff_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    frequency = db.Column(db.String(20), nullable=False)  # weekly, biweekly, monthly
    day_of_week = db.Column(db.Integer)  # 0=Monday, 6=Sunday
    time_slot = db.Column(db.Time, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    client = db.relationship('Client', backref='recurring_appointments')
    service = db.relationship('Service', backref='recurring_bookings')
    staff = db.relationship('User', backref='recurring_schedule')

class Location(db.Model):
    """Support for multiple locations/branches"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.Text, nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_active = db.Column(db.Boolean, default=True)
    operating_hours = db.Column(db.Text)  # JSON for weekly hours
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    manager = db.relationship('User', backref='managed_locations')

class BusinessSettings(db.Model):
    """Global business settings and preferences"""
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(50), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    data_type = db.Column(db.String(20), default='string')  # string, integer, float, boolean, json
    description = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    # Relationships
    updater = db.relationship('User', backref='setting_updates')
