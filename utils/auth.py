# utils/auth.py
from functools import wraps
from flask import redirect, session, url_for

def login_required_role(role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or session.get('role') != role:
                return redirect(url_for(f'{role}_login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
