from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField
from wtforms.validators import DataRequired


class DeviceForm(FlaskForm):
    person_id = SelectField('Person', coerce=int, validators=[DataRequired()])
    type = SelectField('Device Type', coerce=int, choices=[(1, 'light'), (2, 'thermostat'), (3, 'door lock')], validators=[DataRequired()])
    name = StringField("Device Name", validators=[DataRequired()])
    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})
    submit = SubmitField('Submit')
