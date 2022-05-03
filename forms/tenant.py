from flask_wtf import FlaskForm
from wtforms import SubmitField, SelectField
from wtforms.validators import DataRequired


class TenantForm(FlaskForm):
    person_id = SelectField('Person', coerce=int, validators=[DataRequired()])
    building_id = SelectField('Building_ID', coerce=int, validators=[DataRequired()])
    apartment_id = SelectField('Apartment ID', coerce=int, validators=[DataRequired()])

    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})
    submit = SubmitField('Submit')
