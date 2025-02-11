from flask import Blueprint, render_template, redirect, url_for, flash, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user
from app.models import User
from app import db
from app.forms import RegistrationForm
from app.forms import LoginForm

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            session['username'] = user.username
            flash('Login successful!', category='success')
            return redirect(url_for('main.home'))
        else:
            flash('Invalid email or password.', category='error')

    return render_template('login.html', form=form)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered. Please log in.", "danger")
            return redirect(url_for("auth.login"))
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=8)
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        new_user.password = form.password.data

        db.session.add(new_user)
        db.session.commit()
        flash('Account created successfully!', category='success')
        return redirect(url_for('auth.login'))

    return render_template('register.html', form=form)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('username', None)  # Remove username from session
    flash('You have been logged out.', category='info')
    return redirect(url_for('main.home'))
