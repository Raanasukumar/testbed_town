from flask import Blueprint, render_template, redirect, url_for, flash, Response
from app.models import db
from app.models import User
from app.forms import RegistrationForm, LoginForm
from flask_login import login_user, logout_user, login_required, current_user

# Define the main blueprint
main = Blueprint('main', __name__)

@main.route('/')
def home():
    return render_template('home.html', user=current_user)

@main.route('/dashboard')
@login_required
def index():
    return render_template('index.html')

@main.route('/testbed_health')
@login_required
def testbed_health():
    # return render_template('testbed_health.html', devices=devices)
    return Response(stream_device_status(), mimetype='text/event-stream')

@main.route('/testbed_reservation')
@login_required
def testbed_reservation():
    return render_template('testbed_reservation.html')


def ping_device(ip):
    import platform, subprocess
    """Pings a device and returns if it is reachable or not."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", ip]
    return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def stream_device_status():
    import os, yaml, time
    yaml_path = os.path.join(os.getcwd(), "app", "static", "config", "testbed.yaml")

    with open(yaml_path, "r") as file:
        data = yaml.safe_load(file)

    devices = data.get("connection", {})

    for device_name, device_info in devices.items():
        if 'ip' in device_info:
            status = "Reachable ✅" if ping_device(device_info['ip']) else "Unreachable ❌"
        else:
            status = 'no ip or hostname'
        devices[device_name]['status'] = status
        yield f"data: {device_name} - {status}\n\n"  # Streaming update
        time.sleep(0.5)  # Simulate delay
