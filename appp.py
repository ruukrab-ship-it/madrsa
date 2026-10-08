from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SECRET_KEY'] = 'a_very_secure_random_secret_key_here_12345'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portal.db'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

class Registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    grade_class = db.Column(db.String(20), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    national_id = db.Column(db.String(20), nullable=False)
    domain = db.Column(db.String(50), nullable=False)

class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))

with app.app_context():
    db.create_all()
    if not Admin.query.filter_by(username='admin').first():
        hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
        default_admin = Admin(username='admin', password=hashed_pw)
        db.session.add(default_admin)
        db.session.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        grade_class = request.form.get('grade_class')
        phone = request.form.get('phone')
        national_id = request.form.get('national_id')
        domain = request.form.get('domain')
        
        new_reg = Registration(
            full_name=full_name,
            grade_class=grade_class,
            phone=phone,
            national_id=national_id,
            domain=domain
        )
        db.session.add(new_reg)
        db.session.commit()
        return redirect(url_for('success'))
    
    return render_template('index.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        admin = Admin.query.filter_by(username=username).first()
        if admin and bcrypt.check_password_hash(admin.password, password):
            login_user(admin)
            return redirect(url_for('admin_dashboard'))
        else:
            flash('بيانات الدخول غير صحيحة', 'danger')
    return render_template('login.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    registrations = Registration.query.all()
    return render_template('admin.html', registrations=registrations)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
