from flask import Blueprint, render_template, url_for, flash, redirect, request
from app import db, bcrypt
from app.forms.admin_forms import CreateUserForm
from app.models import User, Profile
from flask_login import login_required, current_user

admin = Blueprint('admin', __name__, url_prefix='/admin')

@admin.before_request
@login_required
def check_admin():
    if current_user.role not in ['Super-Admin', 'Admin']:
        flash('No tienes permiso para acceder a esta página.', 'danger')
        return redirect(url_for('main.home'))

@admin.route('/dashboard')
def dashboard():
    users = User.query.all()
    return render_template('admin/dashboard.html', title='Panel de Administración', users=users)

@admin.route('/create_user', methods=['GET', 'POST'])
def create_user():
    form = CreateUserForm()
    # Admin cannot create another Admin, only Super-Admin can
    if current_user.role == 'Admin':
        form.role.choices = [('Asesor', 'Asesor')]
        
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, password_hash=hashed_password, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        
        profile = Profile(user_id=user.id, full_name=form.username.data)
        db.session.add(profile)
        db.session.commit()
        
        flash(f'Usuario {user.username} creado exitosamente como {user.role}.', 'success')
        return redirect(url_for('admin.dashboard'))
    return render_template('admin/create_user.html', title='Crear Usuario', form=form)

@admin.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'Super-Admin':
        flash('No se puede eliminar al Super-Admin.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    if current_user.role == 'Admin' and user.role in ['Super-Admin', 'Admin']:
        flash('No tienes permisos para eliminar a este usuario.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    if user.id == current_user.id:
        flash('No puedes eliminarte a ti mismo.', 'danger')
        return redirect(url_for('admin.dashboard'))
        
    db.session.delete(user)
    db.session.commit()
    flash('Usuario eliminado exitosamente.', 'success')
    return redirect(url_for('admin.dashboard'))

from app.models import RoleRequest

@admin.route('/role_requests')
def role_requests():
    requests = RoleRequest.query.filter_by(status='Pendiente').all()
    return render_template('admin/role_requests.html', title='Solicitudes de Rol de Asesor', requests=requests)

@admin.route('/approve_request/<int:req_id>', methods=['POST'])
def approve_request(req_id):
    rolereq = RoleRequest.query.get_or_404(req_id)
    if rolereq.status != 'Pendiente':
        flash('Esta solicitud ya fue procesada.', 'warning')
        return redirect(url_for('admin.role_requests'))
        
    rolereq.status = 'Aprobado'
    rolereq.user_rel.role = 'Asesor'
    db.session.commit()
    
    flash(f'Solicitud de {rolereq.user_rel.username} aprobada. Ahora es Asesor.', 'success')
    return redirect(url_for('admin.role_requests'))

@admin.route('/reject_request/<int:req_id>', methods=['POST'])
def reject_request(req_id):
    rolereq = RoleRequest.query.get_or_404(req_id)
    if rolereq.status != 'Pendiente':
        flash('Esta solicitud ya fue procesada.', 'warning')
        return redirect(url_for('admin.role_requests'))
        
    rolereq.status = 'Rechazado'
    db.session.commit()
    
    flash(f'Solicitud de {rolereq.user_rel.username} rechazada.', 'info')
    return redirect(url_for('admin.role_requests'))

