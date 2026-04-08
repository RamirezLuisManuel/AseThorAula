from flask import Blueprint, render_template, url_for, flash, redirect, request
from app import db
from app.forms.estudiante_forms import UpdateProfileForm
from flask_login import login_required, current_user

estudiante = Blueprint('estudiante', __name__, url_prefix='/estudiante')

@estudiante.before_request
@login_required
def check_estudiante():
    if current_user.role not in ['Estudiante', 'Asesor']:
        flash('Acceso denegado. Esta sección es solo para estudiantes y asesores.', 'danger')
        return redirect(url_for('main.home'))

@estudiante.route('/profile', methods=['GET', 'POST'])
def profile():
    form = UpdateProfileForm()
    if form.validate_on_submit():
        current_user.profile.full_name = form.full_name.data
        current_user.profile.bio = form.bio.data
        current_user.profile.strengths = form.strengths.data
        current_user.profile.focus_areas = form.focus_areas.data
        db.session.commit()
        flash('Tu perfil ha sido actualizado.', 'success')
        return redirect(url_for('estudiante.profile'))
    elif request.method == 'GET':
        form.full_name.data = current_user.profile.full_name
        form.bio.data = current_user.profile.bio
        form.strengths.data = current_user.profile.strengths
        form.focus_areas.data = current_user.profile.focus_areas
        
    from app.models import RoleRequest
    pending_request = RoleRequest.query.filter_by(user_id=current_user.id, status='Pendiente').first()
    return render_template('estudiante/profile.html', title='Mi Perfil', form=form, pending_request=pending_request)

@estudiante.route('/request_asesor', methods=['POST'])
def request_asesor():
    from app.models import RoleRequest
    existing_request = RoleRequest.query.filter_by(user_id=current_user.id, status='Pendiente').first()
    if existing_request:
        flash('Ya tienes una solicitud pendiente.', 'warning')
        return redirect(url_for('estudiante.profile'))
        
    new_request = RoleRequest(user_id=current_user.id)
    db.session.add(new_request)
    db.session.commit()
    flash('Tu solicitud para ser Asesor ha sido enviada y está pendiente de aprobación.', 'success')
    return redirect(url_for('estudiante.profile'))

from app.models import TutoringSession, Enrollment, User, Profile
from sqlalchemy import or_

@estudiante.route('/search')
def search():
    query = TutoringSession.query
    
    # Get filters from request arguments
    topic = request.args.get('topic')
    session_type = request.args.get('session_type')
    date = request.args.get('date')
    
    if topic:
        query = query.filter(TutoringSession.topic.ilike(f'%{topic}%'))
    if session_type:
        query = query.filter(TutoringSession.session_type == session_type)
    if date:
        query = query.filter(TutoringSession.date == date)
        
    sessions = query.order_by(TutoringSession.date, TutoringSession.start_time).all()
    # Fetch all advisors for the carousel
    asesores = User.query.filter_by(role='Asesor').all()
    return render_template('estudiante/search.html', title='Buscar Asesorías', sessions=sessions, asesores=asesores)

@estudiante.route('/enroll/<int:session_id>', methods=['POST'])
def enroll(session_id):
    session = TutoringSession.query.get_or_404(session_id)
    
    # Check if Asesor tries to enroll in their own session
    if session.asesor_id == current_user.id:
        flash('No puedes inscribirte a tu propia asesoría.', 'warning')
        return redirect(url_for('estudiante.search'))
    
    # Check if already enrolled
    existing_enrollment = Enrollment.query.filter_by(student_id=current_user.id, session_id=session_id).first()
    if existing_enrollment:
        flash('Ya estás inscrito en esta asesoría.', 'warning')
        return redirect(url_for('estudiante.search'))
        
    # Check capacity
    enrolled_count = Enrollment.query.filter_by(session_id=session_id).count()
    if enrolled_count >= session.capacity:
        flash('Lo sentimos, esta asesoría ya está llena.', 'danger')
        return redirect(url_for('estudiante.search'))
        
    enrollment = Enrollment(student_id=current_user.id, session_id=session_id)
    db.session.add(enrollment)
    db.session.commit()
    flash('Te has inscrito exitosamente a la asesoría.', 'success')
    return redirect(url_for('estudiante.my_sessions'))

@estudiante.route('/my_sessions')
def my_sessions():
    enrollments = Enrollment.query.filter_by(student_id=current_user.id).all()
    return render_template('estudiante/my_sessions.html', title='Mis Asesorías Inscritas', enrollments=enrollments)

from app.forms.estudiante_forms import ReviewForm
from app.models import Review

@estudiante.route('/review/<int:session_id>', methods=['GET', 'POST'])
def review_session(session_id):
    session = TutoringSession.query.get_or_404(session_id)
    
    # Check if student is enrolled
    enrollment = Enrollment.query.filter_by(student_id=current_user.id, session_id=session_id).first()
    if not enrollment:
        flash('No puedes calificar una asesoría a la que no estás inscrito.', 'danger')
        return redirect(url_for('estudiante.my_sessions'))
        
    # Check if already reviewed
    existing_review = Review.query.filter_by(student_id=current_user.id, session_id=session_id).first()
    if existing_review:
        flash('Ya has calificado esta asesoría.', 'info')
        return redirect(url_for('estudiante.my_sessions'))
        
    form = ReviewForm()
    if form.validate_on_submit():
        review = Review(
            student_id=current_user.id,
            session_id=session_id,
            asesor_id=session.asesor_id,
            rating=form.rating.data,
            comment=form.comment.data
        )
        db.session.add(review)
        db.session.commit()
        
        # Recalculate Average Rating for Asesor
        asesor_profile = Profile.query.filter_by(user_id=session.asesor_id).first()
        all_reviews = Review.query.filter_by(asesor_id=session.asesor_id).all()
        if all_reviews:
            avg_rating = sum(r.rating for r in all_reviews) / len(all_reviews)
            asesor_profile.rating_avg = round(avg_rating, 1)
            db.session.commit()
            
        flash('Gracias por tu calificación.', 'success')
        return redirect(url_for('estudiante.my_sessions'))
        
    return render_template('estudiante/review.html', title='Calificar Asesoría', form=form, session=session)
