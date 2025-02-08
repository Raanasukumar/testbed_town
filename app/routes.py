from flask import Blueprint, render_template, redirect, url_for, flash
from app import db
from app.models import User
from app.forms import RegistrationForm, LoginForm
from flask_login import login_user, logout_user, login_required

# Define the main blueprint
main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=form.password.data
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created!', 'success')
        return redirect(url_for('main.login'))
    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and user.verify_password(form.password.data):
            login_user(user)
            return redirect(url_for('main.index'))
        else:
            flash('Login failed. Check email and password.', 'danger')
    return render_template('login.html', form=form)

@main.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/testbed_health')
def testbed_health():
    return render_template('testbed_health.html')

@main.route('/testbed_reservation')
def testbed_reservation():
    return render_template('testbed_reservation.html')
