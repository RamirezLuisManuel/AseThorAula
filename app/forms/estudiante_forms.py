from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Length

class UpdateProfileForm(FlaskForm):
    full_name = StringField('Nombre Completo', validators=[Length(max=100)])
    bio = TextAreaField('Biografía', validators=[Length(max=500)])
    strengths = StringField('Fortalezas (ej. Matemáticas, Lectura)', validators=[Length(max=200)])
    focus_areas = StringField('Áreas de enfoque (ej. Álgebra, Historia)', validators=[Length(max=200)])
    submit = SubmitField('Actualizar Perfil')

from wtforms import IntegerField
from wtforms.validators import DataRequired, NumberRange

class ReviewForm(FlaskForm):
    rating = IntegerField('Puntuación (1-5 estrellas)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    comment = TextAreaField('Comentario (opcional)', validators=[Length(max=500)])
    submit = SubmitField('Calificar Asesoría')
