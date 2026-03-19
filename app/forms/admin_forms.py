from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.models import User

class CreateUserForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Rol', choices=[('Admin', 'Admin'), ('Asesor', 'Asesor')])
    submit = SubmitField('Crear Usuario')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Ese nombre de usuario ya está en uso.')
