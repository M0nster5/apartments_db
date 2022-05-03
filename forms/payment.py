from flask_wtf import FlaskForm
from wtforms import DateField, SelectField, IntegerField, SubmitField
from wtforms.validators import DataRequired


class PaymentForm(FlaskForm):
    person_id = SelectField('Person', coerce=int, validators=[DataRequired()])
    paid_on = DateField("Paid on", validators=[DataRequired()])
    amount = IntegerField("Amount Paid", validators=[DataRequired()])

    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})
    submit = SubmitField('Submit')
