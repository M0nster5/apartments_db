from flask_wtf import FlaskForm
from wtforms import StringField, validators, SubmitField, DateField


class SignUpForm(FlaskForm):
    dob = DateField("Date of Birth")
    first_name = StringField('First Name', [validators.Length(max=25)])
    last_name = StringField('Last Name', [validators.Length( max=25)])
    email = StringField('Email', [validators.Length(min=4, max=25)])
    password = StringField('Password', [validators.Length(min=6, max=35)])

    submit = SubmitField('Submit')
