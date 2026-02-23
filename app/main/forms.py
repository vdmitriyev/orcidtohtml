from flask_wtf import FlaskForm
from markupsafe import Markup
from wtforms import (
    StringField,
    SubmitField,
)
from wtforms.validators import Length, Regexp


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
