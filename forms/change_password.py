from flask_wtf import FlaskForm
from wtforms import StringField, validators, SubmitField


class ChangePasswordForm(FlaskForm):
    email = StringField('Username', [validators.Length(min=4, max=25)])
    old_password = StringField('Old Password', [validators.Length(min=6, max=35)])
    new_password = StringField('New Password', [validators.Length(min=6, max=35)])

    submit = SubmitField('Submit')
