from flask_wtf import FlaskForm
from wtforms import StringField, validators, SubmitField, IntegerField


class BuildingForm(FlaskForm):
    building_id = IntegerField("Building ID")
    name = StringField('Building Name', [validators.Length( max=25)])

    cancel = SubmitField('Cancel', render_kw={'formnovalidate': True})
    submit = SubmitField('Submit')
