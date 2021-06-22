from flask import Markup
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, PasswordField,\
                    SelectField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp

class OrcidForm(FlaskForm):

    name    = StringField('Name',               validators=[Length(2, 50,
                                                            message = Markup('<b class="text-danger">Name field must be between %(min)d and %(max)d characters long</b>'))])
    orcidID = StringField('ORCID (special ID)', validators=[Regexp('^\d{4}-\d{4}-\d{4}-\d{4}',
                                                            message = Markup('<b class="text-danger">Wrong ORCID</b>'))])
    submit  = SubmitField('Generate')
