from flask import Markup
from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    PasswordField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.validators import DataRequired, Email, Length, Regexp


class OrcidForm(FlaskForm):

    name = StringField(
        "Name",
        validators=[
            Length(
                2,
                50,
                message=Markup(
                    '<b class="text-danger">Name field must be between %(min)d and %(max)d characters long</b>'
                ),
            )
        ],
    )
    orcidID = StringField(
        "ORCID (special ID)",
        validators=[Regexp("^\d{4}-\d{4}-\d{4}-\d{4}", message=Markup('<b class="text-danger">Wrong ORCID</b>'))],
    )
    submit = SubmitField("Generate")
