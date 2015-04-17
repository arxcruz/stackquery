import json
import requests

from stackquery.database import db_session
from stackquery.models.gerritreview import GerritReview
from stackquery.models.gerritreviewfile import GerritReviewFile
from stackquery.models.user import User

from stackquery.libs import utils
from stackquery.libs import vcs

import re

from datetime import datetime
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
    valid_filters = ['owner', 'project', 'status', 'file']
    filters = search_filter.split(' ')
    for _filter in filters:
        value = _filter.split(':')
        if type(value) == list:
            if value[0] in valid_filters:
                return_filter[value[0]] = value[1]

    return return_filter


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
    return reviews


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
        if review.get('revisions', None) and current_revision:
            if review['revisions'].get(current_revision):
                files = review['revisions'][current_revision].get('files')
                for f in files.keys():
                    gerrit_file = GerritReviewFile()
                    gerrit_file.filename = f
                    gerrit_review.files.append(gerrit_file)

    db_session.add(gerrit_review)
    db_session.commit()


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


def update_gerrit_review(gerrit_review):
    review = utils.get_gerrit_reviews(
        filter={'change_id': gerrit_review['change_id']}, first=True)

    if review:
        db_session.commit()

        current_revision = gerrit_review.get('current_revision', None)
        if gerrit_review.get('status', None) == 'MERGED':
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
        LOG.debug(
            'Review found in database. Change id: %s and commit id %s' %
            (review.change_id, review.commit_id))

        review.commit_id = gerrit_review.get('current_revision', None)

        user_id = gerrit_review['owner'].get('username', None)
        email = gerrit_review['owner'].get('email', None)

        user = (utils.get_users(filter={'user_id': user_id}, first=True) or
                utils.get_users(filter={'email': email}, first=True))
        review.user = user
        review.user_id = user.id if user else None
        review.status = gerrit_review['status']
        db_session.commit()


def process_reviews(project, last_run=datetime.now()):
    change_ids = load_change_id(project)

    LOG.debug('Fetching all review for project %s upstream' % project)
    gerrit_results = get_changes_by_filter('project:' + project)

    from stackquery import app

    filename = app.config['DATA_JSON']
    LOG.debug('Fetching the commits')
    repos = utils.get_repos_by_module(filename, project)
    repo_git = vcs.get_vcs(repos, app.config['SOURCE_ROOT'])
    commit_index = repo_git.fetch()

    for gerrit_result in gerrit_results:
        version = commit_index.get(
            gerrit_result.get('current_revision', None), 'unknow')
        gerrit_result['version'] = version
        if gerrit_result['change_id'] in change_ids:
            update_gerrit_review(gerrit_result)
        else:
            insert_gerrit_review(gerrit_result)
