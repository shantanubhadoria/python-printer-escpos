#   committer
#   Copyright 2012-2014 Michael Gruber
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""
    Git command line client wrapper.
"""

__author__ = 'Michael Gruber'

from os import path

from committer.vcsclients import AbstractVcsClient
from committer.execution import check_if_is_executable, execute_command
ALREADY_UP_TO_DATE = 'Already up-to-date.\n'


class GitClient(AbstractVcsClient):
    """
        Git dvcs client.
    """

    def __init__(self):
        super(GitClient, self).__init__(name='Git', command='git')

    def commit(self, message):
        """
            commits all files by calling: git commit -a -m "message"
            followed by a "git push"
        """
        self._git('commit', '-a', '-m', message)
        self._git('push')

    def detect(self):
        """
            Checks if the current directory represents a git repository.

            @return: True if the ".git" directory exists,
                     False otherwise.
        """
        return path.isdir('.git')

    @property
    def everything_was_up_to_date(self):
        """
            Checks if the last update found changes or not.

            @return: True if no changes have been found,
                     False otherwise.
        """
        stdout = self._update_result['stdout']
        return stdout == ALREADY_UP_TO_DATE

    def is_executable(self):
        """
            Checks if the git command line client is executable.

            @return: True if "git --version" is executable,
                     False otherwise.
        """
        return check_if_is_executable(self.command, '--version')

    def status(self):
        """
            Shows changes in current directory using "git status -sb".
        """
        self._git('status', '-sb')

    def update(self):
        """
            Updates files by executing "git pull".
        """
        self._update_result = self._git('pull')

    def _git(self, *arguments):
        """
            Executes git using the given arguments.
        """
        return execute_command(self.command, *arguments)
