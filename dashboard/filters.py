from models import CustomReport

import re


def format_mark(value):
    if isinstance(value, dict):
        marks = ''
        for key in value:
            marks += "%s: %s\n" % (key, value[key])
        marks += '\n'
    elif type(value) == str:
        marks = value
    return marks


def filter_table_header(value):
    output = re.search('^"[^"]+":\s"?([^"]*)"?"[^"]*/[^"]*"', value)
    if output > 0:
        output = output.groups()[0]
        output = output.replace("-", "")
        return output[0].upper() + output[1:]

    return value.split(',')[0].replace('"', '')


def format_url(value):
    if len(value) > 50:
        return value[0:15] + '...' + value[-15:]
    return value


def get_custom_reports():
    return CustomReport.query.all()


def split_string(value):
    return_value = ""
    if isinstance(value, str):
        value = value.replace("\"", "").strip()
        return value.split(',')

    return return_value

def get_list_of_ints(value):
    return [int(x) for x in value if x.isdigit()]


def get_total_bugzilla_report(report):
    columns = [0] * (len(split_string(report[0]))-1)
    total = 0
    for row in report:
        splited_row = split_string(row)[1:]
        total += sum(get_list_of_ints(splited_row))
        for i, value in enumerate(splited_row):
            if value.isdigit():
                columns[i] = columns[i] + int(value)

    columns.append(total)

    return columns




def init_app(app):
    """Initialize a Flask application with custom filters."""
    app.jinja_env.filters['format_mark'] = format_mark
    app.jinja_env.filters['format_url'] = format_url
    app.jinja_env.filters['split_string'] = split_string
    app.jinja_env.filters['filter_table_header'] = filter_table_header
    app.jinja_env.filters['get_list_of_ints'] = get_list_of_ints
    app.jinja_env.filters['get_total_bugzilla_report'] = get_total_bugzilla_report

    app.jinja_env.globals.update(get_custom_reports=get_custom_reports)
