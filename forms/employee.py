from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField, StringField
from wtforms.validators import DataRequired


class EmployeeForm(FlaskForm):
    person_id = SelectField('Person', coerce=int, validators=[DataRequired()])
    type = StringField('Type', validators=[DataRequired()])

    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})
    submit = SubmitField('Submit')
