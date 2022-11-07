from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField, URLField, DecimalField, SubmitField, SelectField
from wtforms.validators import DataRequired


class NewCafeForm(FlaskForm):
    name = StringField('Cafe name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    map_url = URLField('Map location URL', validators=[DataRequired()])
    img_url = URLField('Image URL', validators=[DataRequired()])
    seats = StringField('Number of seats', validators=[DataRequired()])
    has_toilet = BooleanField('Has toilet')
    has_wifi = BooleanField('Has WIFI')
    has_sockets = BooleanField('Has sockets')
    can_take_calls = BooleanField('Allows to take calls')
    coffee_price = DecimalField('Coffee price', validators=[DataRequired()])
    submit = SubmitField('Add cafe')


class DeleteCafe(FlaskForm):
    name = SelectField('Cafe', validators=[DataRequired()])
    submit = SubmitField('Delete cafe')

    def __init__(self, cafes, **kwargs):
        super().__init__(**kwargs)
        self.name.choices = [(c.id, c.name) for c in cafes]

