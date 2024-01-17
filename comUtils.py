# encoding: utf-8
from flask import  session, flash, session, flash, redirect, url_for
from functools import wraps
from flask_sqlalchemy import SQLAlchemy 
db = SQLAlchemy()

def require_login(func):
    @wraps(func)
    def inner_func(*args, **kwargs):
        if not 'username' in session:
            flash('Please login firstly!', 'danger')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return inner_func

def require_admin(func):
    @wraps(func)
    def inner_func(*args, **kwargs):
        if session.get('admin') != 1:
            flash("You don't have admin priviledge!", 'danger')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return inner_func