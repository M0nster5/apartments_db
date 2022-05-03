from flask_wtf import FlaskForm
from wtforms import StringField, validators, SubmitField


class LoginForm(FlaskForm):
    email = StringField('Username', [validators.Length(min=4, max=100)])
    password = StringField('Password', [validators.Length(min=6, max=100)])

    submit = SubmitField('Submit')
    sign_up = SubmitField('Sign Up', render_kw={'formnovalidate': True})