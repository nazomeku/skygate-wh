from flask_wtf import FlaskForm
from wtforms import ValidationError, StringField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, required
from .models import Product


class ManageProduct(FlaskForm):
    """Form to manage products."""

    name = StringField('Name', validators=[DataRequired("Please enter product name."), Length(min=1, max=50)])
    quantity = IntegerField('Quantity', validators=[required("Please enter a number.")])
    submit = SubmitField('Add product')

    def validate_name(self, field):
        if Product.query.filter_by(name=field.data.lower()).first():
            raise ValidationError('Product already in warehouse.')
        elif len(Product.query.all()) == 5:
            raise ValidationError('Too much products in warehouse.')
