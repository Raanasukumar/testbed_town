from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    @property
    def password(self):
        raise AttributeError('Password is not readable!')
    
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)  # Hashing password

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class Testbed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    contact_owner = db.Column(db.String(100), nullable=False)
    reserved = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Testbed {self.name}>'

# ✅ Add TopologyField model
class TopologyField(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topology_id = db.Column(db.Integer, db.ForeignKey('testbed.id'), nullable=False)
    field_name = db.Column(db.String(100), nullable=False)
    field_value = db.Column(db.String(255), nullable=True)

    def __repr__(self):
        return f'<TopologyField {self.field_name}: {self.field_value}>'