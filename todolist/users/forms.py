from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, IntegerField, BooleanField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_login import current_user
from todolist.models import User
from todolist import db_session

class RegistrationForm(FlaskForm):
    name = StringField("Username", validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    # Проверяем если пароли в форме совпадают
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField('Sign Up')

    # Проверяем, если почтовый адрес еще не занят
    def validate_email(self, email):
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == email.data).first()
        
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log in')
