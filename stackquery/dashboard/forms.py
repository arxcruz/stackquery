from flask_wtf.html5 import URLField
from wtforms import Form
from wtforms import TextAreaField
from wtforms import TextField
from wtforms import validators


class ProjectForm(Form):
    name = TextField('Name', [validators.Length(min=3, max=128)])
    git_url = TextField('Git url', [validators.Length(min=4, max=255)])


class RedHatBugzillaReportForm(Form):
    name = TextField('Name', [validators.Length(min=3, max=128)])
    url = URLField('URL', [validators.Length(min=4)])
    description = TextAreaField('Description')


class TeamForm(Form):
    name = TextField('Team name', [validators.Length(min=3, max=128)])


class UserForm(Form):
    name = TextField('Name', [validators.Length(min=3, max=128)])
    user_id = TextField('User id', [validators.Length(min=4, max=25)])
    email = TextField('Email Address', [validators.Length(min=6, max=35)])