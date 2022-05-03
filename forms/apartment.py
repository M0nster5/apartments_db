from flask_wtf import FlaskForm
from wtforms import StringField, validators, SubmitField, IntegerField


class ApartmentForm(FlaskForm):
    building_id = IntegerField("Building ID")
    apartment_id = IntegerField('Apartment ID')
    type = StringField('Type', [validators.Length( max=25)])

    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})
    submit = SubmitField('Submit')
