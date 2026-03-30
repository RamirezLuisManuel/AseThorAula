from flask import Blueprint, render_template, url_for, flash, redirect, request
from app import db
from app.forms.asesor_forms import UpdateAsesorProfileForm
from flask_login import login_required, current_user

asesor = Blueprint('asesor', __name__, url_prefix='/asesor')

@asesor.before_request
@login_required
def check_asesor():
    if current_user.role != 'Asesor':
        flash('Acceso denegado. Esta sección es solo para asesores.', 'danger')
        return redirect(url_for('main.home'))

@asesor.route('/profile', methods=['GET', 'POST'])
def profile():
    form = UpdateAsesorProfileForm()
    if form.validate_on_submit():
        current_user.profile.full_name = form.full_name.data
        current_user.profile.bio = form.bio.data
        current_user.profile.strengths = form.strengths.data
        current_user.profile.focus_areas = form.focus_areas.data
        db.session.commit()
        flash('Tu perfil ha sido actualizado.', 'success')
        return redirect(url_for('asesor.profile'))
    elif request.method == 'GET':
        form.full_name.data = current_user.profile.full_name
        form.bio.data = current_user.profile.bio
        form.strengths.data = current_user.profile.strengths
        form.focus_areas.data = current_user.profile.focus_areas
    return render_template('asesor/profile.html', title='Perfil de Asesor', form=form)

from app.forms.asesor_forms import TutoringSessionForm
from app.models import TutoringSession

@asesor.route('/sessions')
def sessions():
    sessions = TutoringSession.query.filter_by(asesor_id=current_user.id).order_by(TutoringSession.date.desc(), TutoringSession.start_time.desc()).all()
    return render_template('asesor/sessions.html', title='Mis Asesorías', sessions=sessions)

@asesor.route('/sessions/new', methods=['GET', 'POST'])
def new_session():
    form = TutoringSessionForm()
    if form.validate_on_submit():
        overlapping_session = TutoringSession.query.filter(
            TutoringSession.asesor_id == current_user.id,
            TutoringSession.date == form.date.data,
            TutoringSession.start_time < form.end_time.data,
            TutoringSession.end_time > form.start_time.data
        ).first()
        
        if overlapping_session:
            flash(f'Ya tienes una asesoría programada en ese horario ({overlapping_session.start_time.strftime("%H:%M")} - {overlapping_session.end_time.strftime("%H:%M")}).', 'danger')
            return render_template('asesor/session_form.html', title='Nueva Asesoría', form=form, legend='Nueva Asesoría')

        capacity = 1 if form.session_type.data == 'Individual' else form.capacity.data
        session = TutoringSession(
            asesor_id=current_user.id,
            topic=form.topic.data,
            description=form.description.data,
            date=form.date.data,
            start_time=form.start_time.data,
            end_time=form.end_time.data,
            session_type=form.session_type.data,
            capacity=capacity
        )
        db.session.add(session)
        db.session.commit()
        flash('Asesoría creada exitosamente.', 'success')
        return redirect(url_for('asesor.sessions'))
    return render_template('asesor/session_form.html', title='Nueva Asesoría', form=form, legend='Nueva Asesoría')

@asesor.route('/sessions/<int:session_id>/edit', methods=['GET', 'POST'])
def edit_session(session_id):
    session = TutoringSession.query.get_or_404(session_id)
    if session.asesor_id != current_user.id:
        flash('No tienes permiso para editar esta asesoría.', 'danger')
        return redirect(url_for('asesor.sessions'))
    
    form = TutoringSessionForm()
    if form.validate_on_submit():
        overlapping_session = TutoringSession.query.filter(
            TutoringSession.asesor_id == current_user.id,
            TutoringSession.id != session_id,
            TutoringSession.date == form.date.data,
            TutoringSession.start_time < form.end_time.data,
            TutoringSession.end_time > form.start_time.data
        ).first()
        
        if overlapping_session:
            flash(f'Ya tienes otra asesoría programada en ese horario ({overlapping_session.start_time.strftime("%H:%M")} - {overlapping_session.end_time.strftime("%H:%M")}).', 'danger')
            return render_template('asesor/session_form.html', title='Editar Asesoría', form=form, legend='Editar Asesoría')

        session.topic = form.topic.data
        session.description = form.description.data
        session.date = form.date.data
        session.start_time = form.start_time.data
        session.end_time = form.end_time.data
        session.session_type = form.session_type.data
        session.capacity = 1 if form.session_type.data == 'Individual' else form.capacity.data
        db.session.commit()
        flash('Asesoría actualizada exitosamente.', 'success')
        return redirect(url_for('asesor.sessions'))
    elif request.method == 'GET':
        form.topic.data = session.topic
        form.description.data = session.description
        form.date.data = session.date
        form.start_time.data = session.start_time
        form.end_time.data = session.end_time
        form.session_type.data = session.session_type
        form.capacity.data = session.capacity
    return render_template('asesor/session_form.html', title='Editar Asesoría', form=form, legend='Editar Asesoría')

@asesor.route('/sessions/<int:session_id>/delete', methods=['POST'])
def delete_session(session_id):
    session = TutoringSession.query.get_or_404(session_id)
    if session.asesor_id != current_user.id:
        flash('No tienes permiso para eliminar esta asesoría.', 'danger')
        return redirect(url_for('asesor.sessions'))
    
    db.session.delete(session)
    db.session.commit()
    flash('Asesoría eliminada exitosamente.', 'success')
    return redirect(url_for('asesor.sessions'))
