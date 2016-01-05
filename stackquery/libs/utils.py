import json
import os
import mechanize
from collections import OrderedDict

from stackquery.models.gerritreview import GerritReview
from stackquery.models.team import Team
from stackquery.models.user import User

import logging

LOG = logging.getLogger(__name__)


def get_users(filter=None, first=False):
    if not filter:
        return User.query.all()
    if first:
        return User.query.filter_by(**filter).first()
    return User.query.filter_by(**filter).all()


def get_users_by_team(team_id):
    team = Team.query.get(int(team_id))
    if team:
        return team.users
    return []


def get_gerrit_reviews(filter=None, first=False):
    if not filter:
        return GerritReview.query.all()
    if first:
        return GerritReview.query.filter_by(**filter).order_by(
            GerritReview.created.desc()).first()
    return GerritReview.query.filter_by(**filter).filter(
        GerritReview.user is not None).order_by(
        GerritReview.created.desc()).all()


def get_repos(filename):
    if os.path.exists(filename):
        repos = json.load(open(filename))
        return repos.get('repos', [])
    return []


def get_repos_by_module(filename, module):
    LOG.debug('Getting repo by module %s and filename %s' %
              (filename, module.name))
    repos = get_repos(filename)
    _module = module.name
    if '/' in _module:
        _module = _module.split('/')[-1]
    for repo in repos:
        if _module in repo['module']:
            LOG.debug('Repo founded %s' % repo)
            return repo

    # Let's give a try and check if we will be able to download from git
    uri = module.git_url
    LOG.debug('Repo not found, using %s' % uri)
    return {
        'uri': uri, 'module': _module,
        'releases': [{'release_name': 'Mitaka', 'tag_to': 'HEAD'}]}


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


def jsonify_csv(tables):
    return_value = {'tables': []}
    for table in tables:
        dict_to_json = {}
        data_rows = []
        headers = table[0].replace('"', '').split(',')
        headers = table[0].replace('"', '')
        headers = headers.replace('(', '')
        headers = headers.replace(')', '').split(',')
        for row in table[1:]:
            columns = row.replace('"', '').split(',')
            columns = [int(x) if x.isdigit() else x for x in columns]
            data_rows.append(OrderedDict(zip(headers, columns)))

        dict_to_json['rows'] = data_rows
        dict_to_json['headers'] = [{'name': x, 'field': x} for x in headers]
        dict_to_json['title'] = headers[0]
        return_value['tables'].append(dict_to_json)
    return return_value


def get_report_by_id(report_id, username, password):
    from stackquery.models.report import RedHatBugzillaReport

    rhbz_report = RedHatBugzillaReport.query.get(report_id)
    csv_document = get_csv_from_url(rhbz_report.url,
                                    username=username,
                                    password=password)
    if '<!DOCTYPE html PUBLIC' in csv_document:
        return None

    reports = parse_csv(csv_document)
    reports = jsonify_csv(reports)
    return reports
