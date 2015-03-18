# Copyright (c) 2013 Mirantis Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import re
import sh
import shutil

import logging

LOG = logging.getLogger(__name__)


class Vcs(object):
    def __init__(self, repo, sources_root):
        self.repo = repo
        self.sources_root = sources_root
        if not os.path.exists(sources_root):
            os.mkdir(sources_root)
        else:
            if not os.access(sources_root, os.W_OK):
                raise Exception('Sources root folder %s is not writable' %
                                sources_root)

    def fetch(self):
        pass

    def log(self, branch, head_commit_id):
        pass

    def get_last_id(self, branch):
        pass


class Git(Vcs):

    def __init__(self, repo, sources_root):
        super(Git, self).__init__(repo, sources_root)
        uri = self.repo['uri']
        match = re.search(r'([^/]+)\.git$', uri)
        if match:
            self.folder = os.path.normpath(self.sources_root + '/' +
                                           match.group(1))
        else:
            raise Exception('Unexpected uri %s for git' % uri)
        self.release_index = {}

    def _checkout(self, branch):
        try:
            sh.git('clean', '-d', '--force')
            sh.git('reset', '--hard')
            sh.git('checkout', 'origin/' + branch)
            return True
        except sh.ErrorReturnCode as e:
            LOG.error('Unable to checkout branch %(branch)s from repo '
                      '%(uri)s. Ignore it',
                      {'branch': branch, 'uri': self.repo['uri']})
            LOG.exception(e)
            return False

    def fetch(self):
        LOG.debug('Fetching repo uri %s', self.repo['uri'])

        if os.path.exists(self.folder):
            os.chdir(self.folder)
            try:
                uri = str(
                    sh.git('config', '--get', 'remote.origin.url')).strip()
            except sh.ErrorReturnCode as e:
                LOG.error('Unable to get config for git repo %s. Ignore it',
                          self.repo['uri'])
                LOG.exception(e)
                return {}

            if uri != self.repo['uri']:
                LOG.warn('Repo uri %(uri)s differs from cloned %(old)s',
                         {'uri': self.repo['uri'], 'old': uri})
                os.chdir('..')
                shutil.rmtree(self.folder)

        if not os.path.exists(self.folder):
            os.chdir(self.sources_root)
            try:
                sh.git('clone', self.repo['uri'])
            except sh.ErrorReturnCode as e:
                LOG.error('Unable to clone git repo %s. Ignore it',
                          self.repo['uri'])
                LOG.exception(e)
            os.chdir(self.folder)
        else:
            os.chdir(self.folder)
            try:
                sh.git('fetch')
            except sh.ErrorReturnCode as e:
                LOG.error('Unable to fetch git repo %s. Ignore it',
                          self.repo['uri'])
                LOG.exception(e)

        return self._get_release_index()

    def _get_release_index(self):
        if not os.path.exists(self.folder):
            return {}

        LOG.debug('Get release index for repo uri: %s', self.repo['uri'])
        os.chdir(self.folder)
        if not self.release_index:
            for release in self.repo.get('releases', []):
                release_name = release['release_name'].lower()

                if 'branch' in release:
                    branch = release['branch']
                else:
                    branch = 'master'
                if not self._checkout(branch):
                    continue

                if 'tag_from' in release:
                    tag_range = release['tag_from'] + '..' + release['tag_to']
                else:
                    tag_range = release['tag_to']

                try:
                    git_log_iterator = sh.git('log', '--pretty=%H', tag_range,
                                              _tty_out=False)
                    for commit_id in git_log_iterator:
                        self.release_index[commit_id.strip()] = release_name
                except sh.ErrorReturnCode as e:
                    LOG.error('Unable to get log of git repo %s. Ignore it',
                              self.repo['uri'])
                    LOG.exception(e)
        return self.release_index


def get_vcs(repo, sources_root):
    uri = repo['uri']
    LOG.debug('Factory is asked for VCS uri: %s', uri)
    match = re.search(r'\.git$', uri)
    if match:
        return Git(repo, sources_root)
    else:
        LOG.warning('Unsupported VCS, fallback to dummy')
        return Vcs(repo, uri)