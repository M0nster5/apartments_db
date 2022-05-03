from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired


class LeaseForm(FlaskForm):
    person_id = SelectField('Person', coerce=int, validators=[DataRequired()])
    expires_on = DateField("Expires On", validators=[DataRequired()])
    monthly_amt = IntegerField("Monthly Amount", validators=[DataRequired()])

    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})
    submit = SubmitField('Submit')
