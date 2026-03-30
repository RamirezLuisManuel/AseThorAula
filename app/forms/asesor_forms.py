from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Length

class UpdateAsesorProfileForm(FlaskForm):
    full_name = StringField('Nombre Completo', validators=[Length(max=100)])
    bio = TextAreaField('Biografía', validators=[Length(max=500)])
    strengths = StringField('Temas que domina (ej. Programación, Física)', validators=[Length(max=200)])
    focus_areas = StringField('Área enfocada (ej. TICS, Ciencias Básicas)', validators=[Length(max=200)])
    submit = SubmitField('Actualizar Perfil')

from wtforms import DateField, TimeField, SelectField, IntegerField
from wtforms.validators import DataRequired, NumberRange, ValidationError
from datetime import date as datetime_date

class TutoringSessionForm(FlaskForm):
    topic = StringField('Tema', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Descripción', validators=[DataRequired()])
    date = DateField('Fecha', format='%Y-%m-%d', validators=[DataRequired()])
    start_time = TimeField('Hora de Inicio', format='%H:%M', validators=[DataRequired()])
    end_time = TimeField('Hora de Finalización', format='%H:%M', validators=[DataRequired()])
    session_type = SelectField('Tipo de Asesoría', choices=[('Individual', 'Individual'), ('Grupal', 'Grupal')])
    capacity = IntegerField('Cupo (Solo para grupal)', validators=[NumberRange(min=1)], default=1)
    submit = SubmitField('Guardar Asesoría')

    def validate_date(self, date):
        if date.data < datetime_date.today():
            raise ValidationError('La fecha de la asesoría no puede estar en el pasado.')

    def validate_end_time(self, end_time):
        if self.start_time.data and end_time.data:
            if end_time.data <= self.start_time.data:
                raise ValidationError('La hora de finalización debe ser posterior a la de inicio.')
