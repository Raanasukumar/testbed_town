from flask import Blueprint, render_template, redirect, url_for, flash, Response, request, session
from app.models import db
from app.models import User, Testbed, TopologyField
from app.forms import RegistrationForm, LoginForm
from flask_login import login_user, logout_user, login_required, current_user
import os, yaml, time


# Define the main blueprint
main = Blueprint('main', __name__)

@main.route('/')
@login_required
def home():
    return render_template('home.html', user=current_user)

@main.route('/dashboard')
@login_required
def index():
    return render_template('index.html')

@main.route('/testbed_health')
@login_required
def testbed_health():
    testbed_directory = os.path.join(os.getcwd(), "app", "static", "config")
    testbed_files = os.listdir(testbed_directory)
    return render_template('testbed_health.html', testbed_files=testbed_files)

@main.route('/testbed_health_device')
@login_required
def testbed_health_device():
    file = request.args.get('file')
    return Response(stream_device_status(file), mimetype='text/event-stream')

@main.route('/add_topology',methods=['GET', 'POST'])
@login_required
def add_topology():
    if request.method == 'POST':
        topology_name = request.form.get('topology_name')
        description = request.form.get('description')  # Capture description
        contact_owner = request.form.get('contact')  # Capture contact_owner

        if not topology_name or not contact_owner:
            flash("Topology Name and Contact Owner are required!", "danger")
            return redirect(url_for('main.add_topology'))

        # Create and save topology
        new_topology = Testbed(name=topology_name, description=description, contact_owner=contact_owner)
        db.session.add(new_topology)
        db.session.commit()

        # Store dynamic fields
        configured_fields = session.get('configured_fields', [])
        for field in configured_fields:
            field_value = request.form.get(field)
            if field_value:
                new_field = TopologyField(
                    topology_id=new_topology.id,
                    field_name=field,
                    field_value=field_value
                )
                db.session.add(new_field)

        db.session.commit()
        return redirect(url_for('main.testbed_reservation', topology_id=new_topology.id))

    configured_fields = session.get('configured_fields', [])
    return render_template('add_topology.html', configured_fields=configured_fields)

@main.route('/configuration')
@login_required
def configuration():
    return render_template('configuration.html')

@main.route('/testbed_reservation')
@login_required
def testbed_reservation():
    testbeds = Testbed.query.all()  # Get all testbeds
    
    # Fetch dynamic fields for each testbed
    testbed_data = []
    for testbed in testbeds:
        fields = TopologyField.query.filter_by(topology_id=testbed.id).all()
        field_data = {field.field_name: field.field_value for field in fields}
        
        testbed_data.append({
            'id': testbed.id,
            'name': testbed.name,
            'description': testbed.description,
            'contact_owner': testbed.contact_owner,
            'reserved': testbed.reserved,
            'fields': field_data  # Store dynamic fields
        })

    return render_template('testbed_reservation.html', testbeds=testbed_data)


@main.route('/reserve_testbed/<int:testbed_id>', methods=['POST'])
@login_required
def reserve_testbed(testbed_id):
    testbed = Testbed.query.get_or_404(testbed_id)
    if not testbed.reserved:
        testbed.reserved = True
        db.session.commit()
    return redirect(url_for('main.testbed_reservation'))

@main.route('/unreserve_testbed/<int:testbed_id>', methods=['POST'])
@login_required
def unreserve_testbed(testbed_id):
    testbed = Testbed.query.get_or_404(testbed_id)
    if testbed.reserved:
        testbed.reserved = False
        db.session.commit()
    return redirect(url_for('main.testbed_reservation'))


def ping_device(ip):
    import platform, subprocess
    """Pings a device and returns if it is reachable or not."""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, "1", ip]
    return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

def stream_device_status(file):
    yaml_path = os.path.join(os.getcwd(), "app", "static", "config", file)

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
