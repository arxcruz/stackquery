import mechanize
from collections import OrderedDict

from stackquery.db.models import RedHatBugzillaReport


def get_csv_from_url(url, username=None, password=None):
    br = mechanize.Browser()
    br.set_handle_robots(False)
    br.open(url)
    br.select_form(name='login')
    if username:
        br['Bugzilla_login'] = username
    if password:
        br['Bugzilla_password'] = password

    res = br.submit()
    content = res.read()
    return content


def parse_csv(csv_content):
    tmp_tables = csv_content.split('\n\n')

    tables = list()
    for table in tmp_tables:
        table_split = table.split('\n')
        tables.append(table_split)

    return tables


def parse_url(url):
    tmp_url = url
    if 'GoAheadAndLogIn' not in url:
        tmp_url = tmp_url + '&GoAheadAndLogIn=1'

    if 'ctype=csv' not in url:
        tmp_url = tmp_url + '&ctype=csv'

    return tmp_url


def jsonify_csv(tables):
    return_value = []
    for table in tables:
        dic_to_json = dict()
        data_rows = []
        headers = table[0].replace('"', '').split(',')
        for row in table[1:]:
            columns = row.replace('"', '').split(',')
            columns = [int(x) if x.isdigit() else x for x in columns]
            data_rows.append(OrderedDict(zip(headers, columns)))

        dic_to_json['data'] = data_rows
        return_value.append(dic_to_json)

    return return_value


def get_report_by_id(report_id, username, password):

    rhbz_report = RedHatBugzillaReport.query.get(report_id)
    csv_document = get_csv_from_url(rhbz_report.url,
                                    username=username,
                                    password=password)
    if '<!DOCTYPE html PUBLIC' in csv_document:
        return None

    reports = parse_csv(csv_document)
    reports = jsonify_csv(reports)
    return reports