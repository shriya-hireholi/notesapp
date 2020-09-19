from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    SubmitField,
    TextAreaField,
    PasswordField,
    BooleanField)
from wtforms.validators import (
    DataRequired,
    Length, Email,
    EqualTo,
    ValidationError)
from notes.models import Users, Notebook
from flask_login import current_user


class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(), Length(min=2, max=30)])
    email = StringField('Email', validators=[
        DataRequired(),
        Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = Users.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username Taken')
    
    def validate_email(self, email):
        email = Users.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Email Taken')


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(),
        Email()])
    password = PasswordField('Password', validators=[
        DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class NotebookForm(FlaskForm):
    name = StringField('Name', validators=[
        DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Add Notebook')


class NoteForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(), Length(min=2, max=20)])
    content = TextAreaField('Content', validators=[
        DataRequired(), Length(min=2, max=300)])
    submit = SubmitField('Add Note')


class ResetRequestForm(FlaskForm):
    email = email = StringField('Email', validators=[
        DataRequired(),
        Email()])
    submit = SubmitField('Send')

    def validate_email(self, email):
        email = Users.query.filter_by(email=email.data).first()
        if email is None:
            raise ValidationError('There is no account with this email.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[
        DataRequired(),
        EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = PasswordField('Confirm password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Change Password')


class UpdateAccountForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    submit = SubmitField('Update')

    def validate_email(self, email):
        if email.data != current_user.email:
            user = Users.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError(
                    'That email is taken. Please choose a different one.')


class SearchForm(FlaskForm):
    search = StringField('Search', validators=[DataRequired()])
