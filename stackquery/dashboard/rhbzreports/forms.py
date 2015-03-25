from wtforms import Form
from wtforms import TextAreaField
from wtforms import TextField
from wtforms import validators
from flask_wtf.html5 import URLField


class RedHatBugzillaReportForm(Form):
    name = TextField('Name', [validators.Length(min=3, max=128)])
    url = URLField('URL', [validators.Length(min=4)])
    description = TextAreaField('Description')
