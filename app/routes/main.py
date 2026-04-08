from flask_login import current_user
from flask import Blueprint, render_template, abort, url_for, redirect
from app.models import User, TutoringSession, Review

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    if current_user.is_authenticated and current_user.role == 'Estudiante':
        return redirect(url_for('estudiante.search'))
    return render_template('main/home.html')

@main.route('/asesor/<int:asesor_id>')
def asesor_profile(asesor_id):
    asesor = User.query.get_or_404(asesor_id)
    if asesor.role != 'Asesor':
        abort(404)
        
    active_sessions = TutoringSession.query.filter_by(asesor_id=asesor_id).order_by(TutoringSession.date.desc()).all()
    reviews = Review.query.filter_by(asesor_id=asesor_id).order_by(Review.created_at.desc()).all()
    
    return render_template('main/asesor_profile.html', title=f'Perfil de {asesor.profile.full_name or asesor.username}', asesor=asesor, sessions=active_sessions, reviews=reviews)
