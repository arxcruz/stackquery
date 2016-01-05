# Copyright (c) 2014 Red Hat, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#           http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import absolute_import, print_function, unicode_literals
import requests
import requests_futures.sessions
import logging


LOG = logging.getLogger('stackquery')


STACKALYTICS_URL = 'http://stackalytics.com/'


def get_stats(params):
    """Query Stackalytics 'contribution' module with `params`.
        :param params: a dictionary of data passed to the 'contribution'
        module,
        e.g. 'user_id', 'release', 'company'.  The values can contain more
        items seprated by commas, e.g.  `{'user_id': 'user1,user2,user3'}`.
    """
    MODULE = 'api/1.0/contribution'
    params = dict(params)
    LOG.info("Using parameters: %s", params)
    r = requests.get(STACKALYTICS_URL + MODULE, params=params)
    LOG.info(r.url)
    try:
        r.raise_for_status()
    except requests.HTTPError:
        # return {
        #     u'contribution':
        #     {
        #         u'loc': 0, u'email_count': 0, u'commit_count': 0,
        #         u'drafted_blueprint_count': 0,
        #         u'abandoned_change_requests_count': 0,
        #         u'filed_bug_count': 0, u'patch_set_count': 0,
        #         u'completed_blueprint_count': 0, u'marks':
        #             {
        #                 u'A': 0, u'WIP': 0, u'1': 0, u'0': 0, u's': 0,
        #                 u'2': 0, u'-1': 0, u'-2': 0, u'x': 0
        #             },
        #         u'resolved_bug_count': 0, u'change_request_count': 0
        #     }
        # }
        return None

    return r.json()


def get_registered_users(user_ids):
    """Filter users that exist in Stackalytics (and therefore in Launchpad).
    :param user_ids: list of user_id items
    :returns: list of user_ids which are registered in Launchpad/Stackalytics.
    """
    session = requests_futures.sessions.FuturesSession(max_workers=10)
    requests = list()
    for user in user_ids:
        req = session.get(STACKALYTICS_URL, params={'user_id': user})
        requests.append(req)

    assert(len(user_ids) == len(requests))
    result = list()
    for user, req in zip(user_ids, requests):
        r = req.result()
        if r.status_code == 200:
            result.append(user)
        else:
            LOG.warning("User_id '%s' is not registered in Launchpad", user)
    return result


def get_status_from_users(users, company, project_type,
                          release, module=None):
    """Return list of users from stackalytics"""
    parameters = {
        'project_type': project_type,
        'company': company,
        'metric': 'commits',
        'release': release
    }

    user_list = []
    if module:
        parameters['module'] = module
    for user in users:
        parameters['user_id'] = user
        user_info = get_stats(parameters)
        if user_info:
            user_info['contribution']['user'] = user
            user_list.append(user_info['contribution'])

    return user_list


def get_all_users_by_company(company):
    MODULE = 'api/1.0/stats/engineers'
    params = dict(company)
    LOG.info("Using parameters: %s", params)
    r = requests.get(STACKALYTICS_URL + MODULE, params=params)
    LOG.info(r.url)
    r.raise_for_status()
    return r.json()
