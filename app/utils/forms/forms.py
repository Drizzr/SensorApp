from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, EmailField, HiddenField, TextAreaField, SelectMultipleField
from wtforms.validators import DataRequired, Email, Length, EqualTo
from wtforms.widgets import TextArea

class LoginForm(FlaskForm):
    email = EmailField('e-mail', validators=[Email(), Length(min=5, max=24)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=5, max=24)])
    remember_me = BooleanField('remember me')
    submit = SubmitField('sign in')


class SignUpForm(FlaskForm):
    email = EmailField('e-mail', validators=[Email(), Length(min=5, max=24)])
    name = StringField("username", validators=[DataRequired(), Length(min=5, max=24)])
    password = PasswordField('password', validators=[DataRequired(), Length(min=5, max=24)])
    confirmPassword = PasswordField('confirm password', validators=[DataRequired(), Length(min=5, max=24), EqualTo("password")])
    submit = SubmitField('sign up')


class RegisterRoomForm(FlaskForm):
    name = StringField("room name", validators=[DataRequired(), Length(min=5, max=24)])
    description = TextAreaField('room description', widget=TextArea())
    submit = SubmitField('register')


class RegisterSensorForm(FlaskForm):
    name = StringField("sensor name", validators=[DataRequired(), Length(min=5, max=24)])
    value1 = StringField("first value", validators=[DataRequired(), Length(max=20)], description="f.e. Temperature")
    unit1 = StringField("unit", validators=[DataRequired(message="required!"), Length(max=20)], description="f.e. °C")
    value2 = StringField("second value", validators=[Length(max=20)], description="optional")
    unit2 = StringField("unit", validators=[Length(max=20)], description="f.e. °C")
    value3 = StringField("third value", validators=[Length(max=20)], description="optional")
    unit3 = StringField("unit", validators=[Length(max=20)], description="f.e. °C")
    submit = SubmitField('register')