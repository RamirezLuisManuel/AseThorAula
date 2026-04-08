from flask import Blueprint, render_template, url_for, flash, redirect, request
from app import db, bcrypt
from app.forms.auth_forms import RegistrationForm, LoginForm
from app.models import User, Profile
from flask_login import login_user, current_user, logout_user, login_required

auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password_hash=hashed_password, role='Estudiante')
        db.session.add(user)
        db.session.commit()
        
        profile = Profile(user_id=user.id, full_name=form.username.data)
        db.session.add(profile)
        db.session.commit()
        
        flash('Tu cuenta ha sido creada exitosamente! Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Registro', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password_hash, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            if user.role == 'Estudiante':
                return redirect(url_for('estudiante.search'))
            return redirect(url_for('main.home'))
        else:
            flash('Inicio de sesión fallido. Por favor verifica tu usuario y contraseña', 'danger')
    return render_template('auth/login.html', title='Iniciar Sesión', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))
