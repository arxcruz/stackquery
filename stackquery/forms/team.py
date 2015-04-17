from wtforms import Form, TextField, validators


class TeamForm(Form):
    name = TextField('Team name', [validators.Length(min=3, max=128)])
