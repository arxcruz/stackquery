import json
import requests

from sqlalchemy.sql import text

from stackquery.database import db_session
from stackquery.models.gerritreview import GerritReview
from stackquery.models.gerritreviewfile import GerritReviewFile
from stackquery.models.user import User
from stackquery.libs import utils
from stackquery.libs import vcs

import re

import logging

LOG = logging.getLogger(__name__)

GERRIT_URL = 'https://review.openstack.org/%s&o=' \
    'CURRENT_REVISION&o=DETAILED_ACCOUNTS&o=CURRENT_FILES&n=%d'


def _gerrit_rest_api_call(uri):
    ret_val = requests.get(uri)
    ret_val.raise_for_status()
    text = ret_val.text
    text = text.replace(')]}\'', '')
    return json.loads(text)


def get_filters(search_filter):
    return_filter = {}
    valid_filters = ['project', 'status', 'file']
    filters = search_filter.split(' ')
    for _filter in filters:
        value = _filter.split(':')
        if type(value) == list:
            if value[0] in valid_filters:
                return_filter[value[0]] = value[1]

    return return_filter


def parse_to_json(reviews):

    result = {}

    result['headers'] = reviews['_versions']

    result['users'] = []
    del reviews['_versions']
    default_values = {}
    for release in result['headers']:
        default_values[release] = 0

    for user in reviews.keys():
        data = {'name': user}
        data.update(default_values)
        for release_name, release_number in (
                reviews[user]['releases'].iteritems()):
            data[release_name] = release_number
        result['users'].append(data)

    return result


def get_reviews_by_filter(filters, users_ids):

    values = ", ".join(map(str, users_ids))

    sql_query = ("select "
                 "user.user_id, "
                 "gerrit_review.version, "
                 "count(distinct gerrit_review.change_id) from "
                 "gerrit_review, "
                 "user ")
    if filters.get('file', None):
        sql_query += ", gerrit_review_file "

    sql_query += "where "

    if filters.get('project', None):
        sql_query += ("gerrit_review.project = '" + filters['project'] +
                      "' and ")

    if filters.get('file', None):
        sql_query += ("gerrit_review_file.gerrit_review_id = "
                      "gerrit_review.id and ")
    sql_query += ("gerrit_review.user_id = user.id "
                  "and gerrit_review.user_id in ( " + values + " ) "
                  "and gerrit_review.status = '" +
                  filters.get('status', 'MERGED') + "' ")

    if filters.get('file', None):
        sql_query += ("and gerrit_review_file.project REGEXP '" +
                      filters['file'] + "' ")

    sql_query += ("group by gerrit_review.version, gerrit_review.user_id "
                  "order by gerrit_review.user_id, gerrit_review.version")

    s = text(sql_query)

    db_result = db_session.execute(s).fetchall()
    result = {}
    result['headers'] = []
    result['users'] = []

    default_values = {}
    for row in db_result:
        if row[1] not in result['headers']:
            result['headers'].append(row[1])
            default_values[row[1]] = 0

    users = {}
    for row in db_result:
        if row[0] not in users.keys():
            users[row[0]] = {}
            users[row[0]].update(default_values)
        users[row[0]][row[1]] += row[2]

    for user in users:
        row = {'name': user}
        for key in users[user]:
            row[key] = users[user][key]
        result['users'].append(row)
    return result


def calculate_reviews(gerrit_reviews, team_id, filters=None):
    users = utils.get_users_by_team(team_id)
    reviews = {user.user_id: {'releases': {}}
               for user in users}
    reviews['_versions'] = []
    if gerrit_reviews:
        for gerrit_review in gerrit_reviews:
            match = False
            user = gerrit_review.user.user_id if gerrit_review.user else None
            if user and user in reviews.keys():
                if filters and 'file' in filters:
                    for f in gerrit_review.files:
                        if re.match(filters['file'], f.filename):
                            match = True
                            continue
                if filters and 'file' in filters and not match:
                    continue
                if reviews[user]['releases'].get(gerrit_review.version, None):
                    reviews[user]['releases'][gerrit_review.version] += 1
                else:
                    reviews[user]['releases'][gerrit_review.version] = 1
                if (gerrit_review.version and gerrit_review.version
                        not in reviews['_versions']):
                    reviews['_versions'].append(gerrit_review.version)
    reviews['_versions'].sort()

    return parse_to_json(reviews)


def reviews_to_dict(gerrit_reviews):
    if gerrit_reviews:
        return [{'project': review.project,
                 'current_revision': review.commit_id,
                 'owner': {'username': review.user.user_id if review.user else
                           None},
                 'date_time': review.created,
                 '_sortkey': review.sortkey,
                 'in_database': True
                 } for review in gerrit_reviews]
    return []


def get_all_gerrit_projects():
    return _gerrit_rest_api_call('https://review.openstack.org/projects/')


def get_changes_by_filter(search_filter, size=300,
                          server='https://review.openstack.org',
                          sort_key=None, n=None):
    LOG.debug('Getting the %s changes' % size)
    server = server[:-2] if server[-1] == '/' else server

    server = (server +
              '/%s&o=CURRENT_REVISION&o=DETAILED_ACCOUNTS'
              '&o=CURRENT_FILES&n=%d')

    gerrit_url = server % ('changes/?q=' + search_filter, size)

    if sort_key:
        if not isinstance(sort_key, bool):
            gerrit_url = gerrit_url + '&N=%s' % sort_key

    if n and sort_key and isinstance(sort_key, bool):
        actual = size * n
        gerrit_url += '&S=%s' % actual

    gerrit_url = gerrit_url.replace(' ', '+')
    result = _gerrit_rest_api_call(gerrit_url)

    if result[-1].get('_more_changes', None):
        _sortkey = result[-1].get('_sortkey', True)
    else:
        _sortkey = None
        LOG.debug('There is no more changes, this is the last iteration')

    return _sortkey or None, result


def insert_gerrit_review(review):
    LOG.debug('Inserting review %s on database' % review['change_id'])

    user = None
    user_id = review['owner'].get('username', None)
    email = review['owner'].get('email', None)
    if user_id:
        LOG.debug('Looking for user with user id %s in database' % user_id)
        user = User.query.filter_by(user_id=user_id).first()
    elif email:
        LOG.debug('Looking for user with email %s in database' % email)
        user = User.query.filter_by(email=email).first()

    LOG.debug('User in database: %s' % user)
    current_revision = review.get('current_revision', None)

    gerrit_review = GerritReview()
    gerrit_review.commit_id = review.get('current_revision', None)
    gerrit_review.change_id = review.get('change_id', None)
    gerrit_review.version = review.get('version', None)
    gerrit_review.user = user
    gerrit_review.user_id = user.id if user else None
    gerrit_review.project = review.get('project', None)
    gerrit_review.status = review.get('status')

    # We only add the files when it's merged, so it's more easy to
    # track down and don't overload the database
    if review.get('status', None) == 'MERGED':
        LOG.debug('Change is merged, inserting the changed files in database')
        if review.get('revisions', None) and current_revision:
            if review['revisions'].get(current_revision):
                files = review['revisions'][current_revision].get('files')
                for f in files.keys():
                    gerrit_file = GerritReviewFile()
                    gerrit_file.filename = f
                    gerrit_review.files.append(gerrit_file)

    db_session.add(gerrit_review)
    db_session.commit()
    LOG.debug('Change %s inserted successfully' % review['change_id'])


def get_all_reviews_from_database(filters, team_id):
    files = None
    # This is ugly, but I don't think a better solution for now
    if 'file' in filters:
        files = {'file': filters['file']}
        del filters['file']
    gerrit_reviews = utils.get_gerrit_reviews(filter=filters)
    return calculate_reviews(gerrit_reviews, team_id, files)


def load_change_id(project):
    changes = utils.get_gerrit_reviews()
    return {change.change_id: (change.modified, change.status)
            for change in changes}


def load_change_id_from_project_change(project, changes):
    values = ", ".join('\'' + str(c) + '\'' for c in changes)
    sql_query = ('select change_id from gerrit_review '
                 'where project = \'%s\' and change_id in (%s)'
                 % (project['name'], values))
    select = text(sql_query)

    db_result = db_session.execute(select).fetchall()
    return list(zip(*db_result)[0]) if len(db_result) > 0 else []


def get_projects_in_use(project=None):
    sql_query = ('select distinct projects.name, projects.git_url, '
                 'projects.gerrit_server from projects, '
                 'project_team_association where '
                 'project_team_association.project_id = projects.id')
    if project:
        sql_query += ' and projects.name = \'%s\'' % project

    select = text(sql_query)
    db_result = db_session.execute(select).fetchall()
    return [
        {
            'name': x[0],
            'git_url': x[1],
            'gerrit_server': x[2]
        } for x in db_result]


def update_gerrit_review(gerrit_review):
    LOG.debug('Updating review %s' % gerrit_review['change_id'])
    review = utils.get_gerrit_reviews(
        filter={'change_id': gerrit_review['change_id']}, first=True)

    if review:
        LOG.debug(
            'Review found in database. Change id: %s and commit id %s' %
            (review.change_id, review.commit_id))
        current_revision = gerrit_review.get('current_revision', None)
        if gerrit_review.get('status', None) == 'MERGED':
            LOG.debug('Review %s was merged, inserting modified files '
                      'in database' % gerrit_review['change_id'])
            if gerrit_review.get('revisions', None) and current_revision:
                if gerrit_review['revisions'].get(current_revision):
                    files = gerrit_review['revisions'][current_revision].get(
                        'files')
                    files_in_database = [f.filename for f in review.files]
                    files_in_gerrit = files.keys() if files else []
                    files_to_delete = list(set(files_in_database) - set(
                        files_in_gerrit))
                    for f in review.files:
                        if f.filename in files_to_delete:
                            review.files.remove(f)

                    for f in files.keys():
                        if f not in files_in_database:
                            gerrit_file = GerritReviewFile()
                            gerrit_file.filename = f
                            review.files.append(gerrit_file)

        review.commit_id = current_revision
        review.version = gerrit_review.get('version')

        user_id = gerrit_review['owner'].get('username', None)
        email = gerrit_review['owner'].get('email', None)

        user = (utils.get_users(filter={'user_id': user_id}, first=True) or
                utils.get_users(filter={'email': email}, first=True))
        review.user = user
        review.user_id = user.id if user else None
        review.status = gerrit_review['status']
        db_session.commit()


def process_reviews(project):
    LOG.debug('Processing changes for project %s' % project)
    counter = 1
    sort_key, gerrit_results = get_changes_by_filter(
        'project:' + project['name'], server=project['gerrit_server'],
        n=counter)

    change_ids = [gerrit_result['change_id'] for
                  gerrit_result in gerrit_results]

    change_results = load_change_id_from_project_change(project,
                                                        change_ids)

    from stackquery import app

    filename = app.config['DATA_JSON']
    repos = utils.get_repos_by_module(filename, project)
    repo_git = vcs.get_vcs(repos, app.config['SOURCE_ROOT'])
    commit_index = repo_git.fetch()

    while sort_key or gerrit_results:
        LOG.debug('Calculating results to insert')
        to_insert = [gerrit for gerrit in gerrit_results if
                     gerrit_result['change_id'] not in change_results]
        LOG.debug('Number of insertions: %s' % len(to_insert))
        LOG.debug('Calculating results to update')
        to_update = [gerrit for gerrit in gerrit_results if
                     gerrit_result['change_id'] in change_results]
        LOG.debug('Number of updades: %s' % len(to_update))

        LOG.debug('Inserting reviews if exist')
        for gerrit_result in to_insert:
            version = commit_index.get(
                gerrit_result.get('current_revision', None), 'unknow')
            gerrit_result['version'] = version
            insert_gerrit_review(gerrit_result)

        LOG.debug('Updating reviews if exist')
        for gerrit_result in to_update:
            version = commit_index.get(
                gerrit_result.get('current_revision', None), 'unknow')
            gerrit_result['version'] = version
            update_gerrit_review(gerrit_result)

        LOG.debug('Looking for more changes')
        if not sort_key and not gerrit_results[-1].get('_more_changes', None):
            LOG.debug('No more changes for project %s' % project['name'])
            break

        sort_key, gerrit_results = get_changes_by_filter(
            'project:' + project['name'], server=project['gerrit_server'],
            sort_key=sort_key, n=counter)
        change_ids = [gerrit_result['change_id'] for
                      gerrit_result in gerrit_results]
        counter += 1
        change_results = load_change_id_from_project_change(project,
                                                            change_ids)
    LOG.debug('Ending processing project %s' % project['name'])
