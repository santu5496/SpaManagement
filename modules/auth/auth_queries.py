"""
Authentication-related database queries
"""
from models import User

def get_user_by_username(username):
    """Get user by username"""
    return User.query.filter_by(username=username).first()

def get_user_by_email(email):
    """Get user by email"""
    return User.query.filter_by(email=email).first()

def get_user_by_id(user_id):
    """Get user by ID"""
    return User.query.get(int(user_id))

def get_active_user_by_username(username):
    """Get active user by username"""
    return User.query.filter_by(username=username, is_active=True).first()

def validate_user_credentials(username, password):
    """Validate user credentials"""
    user = get_active_user_by_username(username)
    if user and user.check_password(password):
        return user
    return None