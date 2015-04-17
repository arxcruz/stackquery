from flask_wtf.html5 import URLField
from wtforms import Form, TextAreaField, TextField, validators


class RedHatBugzillaReportForm(Form):
    name = TextField('Name', [validators.Length(min=3, max=128)])
    url = URLField('URL', [validators.Length(min=4)])
    description = TextAreaField('Description')
