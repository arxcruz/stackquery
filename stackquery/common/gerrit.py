import json
import requests

import datetime

from oslo.config import cfg

from stackquery.db.database import db_session
from stackquery.db.models import User
from stackquery.db.models import GerritReview
import stackquery.common.utils
import stackquery.common.vcs

GERRIT_URL = 'https://review.openstack.org/%s&o=' \
    'CURRENT_REVISION&o=DETAILED_ACCOUNTS&n=%d'


def get_changes_by_filter(search_filter, size=300, sort_key=None):

    gerrit_url = GERRIT_URL % ('changes/?q=' + search_filter, size)

    if sort_key:
        gerrit_url = gerrit_url + '&N=%s' % sort_key

    gerrit_url = gerrit_url.replace(' ', '+')
    result = _gerrit_rest_api_call(gerrit_url)

    if result[-1].get('_more_changes', None):
        result += get_changes_by_filter(search_filter, size,
                                        result[-1]['_sortkey'])

    return result


def insert_review_if_needed(review, version=None):
    commit = review.get('current_revision', None)
    project = review['project']
    user_id = review['owner'].get('username', None)
    email = review['owner'].get('email', None)

    user = None
    if user_id:
        user = User.query.filter_by(user_id=user_id).first()
    elif email:
        user = User.query.filter_by(email=email).first()

    gerrit_review = GerritReview.query.filter_by(commit_id=commit,
                                                 project=project).first()
    if not gerrit_review:
        gerrit_review = GerritReview()
        gerrit_review.user = user
        gerrit_review.commit_id = commit
        gerrit_review.project = project
        gerrit_review.version = version
        gerrit_review.sortkey = review['_sortkey']
        gerrit_review.owner = user.user_id if user else None
        db_session.add(gerrit_review)
        db_session.commit()


def _get_all_reviews_from_database(filters):
    return GerritReview.query.filter_by(**filters).order_by(
        GerritReview.created.desc()).all()


def _reviews_to_dict(gerrit_reviews):
    if gerrit_reviews:
        return [{'project': review.project,
                 'current_revision': review.commit_id,
                 'owner': {'username': review.user.user_id if review.user else
                           review.owner},
                 'date_time': review.created,
                 '_sortkey': review.sortkey,
                 'in_database': True
                 } for review in gerrit_reviews]
    return []


def get_all_reviews_from_database(filters):
    gerrit_reviews = _get_all_reviews_from_database(filters)
    return _reviews_to_dict(gerrit_reviews)


def get_filters(search_filter):
    return_filter = {}
    valid_filters = ['owner', 'project']
    filters = search_filter.split(' ')
    for _filter in filters:
        value = _filter.split(':')
        if type(value) == list:
            if value[0] in valid_filters:
                return_filter[value[0]] = value[1]

    return return_filter


def _check_users_and_update_database(users):
    for user in users:
        modified = user.modified
        now = datetime.datetime.now()
        if abs(modified - now).days >= 0:
            gerrit_results = get_changes_by_filter('owner:' + user.user_id + '+status:merged')
            for result in gerrit_results:
                db_results = _get_all_reviews_from_database({
                    'project': result['project'],
                    'commit_id': result['current_revision']
                    })
                for db_result in db_results:
                    if not db_result.user:
                        db_result.user = user
                        db_result.owner = user.user_id
    db_session.commit()

def get_report_by_filter(search_filter):

    users = User.query.all()
    _check_users_and_update_database(users)
    filters = get_filters(search_filter)
    if 'file:' in search_filter:
        gerrit_results = []
    else:
        gerrit_results = get_all_reviews_from_database(filters)


    sort_key = None

    if len(gerrit_results) > 0:
        last_created = gerrit_results[0]['date_time']
        now = datetime.datetime.now()
        if abs(last_created - now).days >= 0:
            sort_key = gerrit_results[1]['_sortkey']

    list_users = [user.user_id for user in users]
    list_emails = [user.email for user in users]

    gerrit_results += get_changes_by_filter(search_filter,
                                            sort_key=sort_key)
    tmp = get_changes_by_filter(search_filter,
                                sort_key=sort_key)

    list_changes = []
    releases = {}

    for result in gerrit_results:
        username = result['owner'].get('username', '')
        email = result['owner'].get('email')
        if not result.get('in_database', None):
            insert_review_if_needed(result)
        if username in list_users or email in list_emails:
            list_changes.append(result)
            releases[username if username != '' else email] = {
                'releases': {}
            }

    projects = {}
    version_table = []
    for change in list_changes:
        filename = cfg.CONF.data_json
        if not projects.get(change['project'], None):
            repos = utils.get_repos_by_module(filename, change['project'])
            repo_git = vcs.get_vcs(repos, cfg.CONF.sources_root)
            commit_index = repo_git.fetch()
            projects[change['project']] = commit_index

        commit_id = change['current_revision']
        user_id = change['owner'].get('username') or change['owner']['email']
        version = projects[change['project']].get(commit_id, None)

        if version:
            if not releases[user_id]['releases'].get(version, None):
                releases[user_id]['releases'][version] = 0
            releases[user_id]['releases'][version] += 1
            if version not in version_table:
                version_table.append(version)

    releases['_versions'] = sorted(version_table)

    return releases


def _gerrit_rest_api_call(uri):
    ret_val = requests.get(uri)
    ret_val.raise_for_status()
    text = ret_val.text
    text = text.replace(')]}\'', '')
    return json.loads(text)


def get_all_projects():
    return _gerrit_rest_api_call('https://review.openstack.org/projects/')
