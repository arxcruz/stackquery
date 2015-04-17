from wtforms import Form, TextField, validators


class ProjectForm(Form):
    name = TextField('Name', [validators.Length(min=3, max=128)])
    git_url = TextField('Git url', [validators.Length(min=4, max=255)])
