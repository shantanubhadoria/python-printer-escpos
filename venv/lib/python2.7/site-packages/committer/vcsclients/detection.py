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
    Provides function "detect_vcs_client" which detects the corresponding
    version control system client for the current working directory.
"""

__author__ = 'Michael Gruber'

from committer import errors
from committer.vcsclients.git import GitClient
from committer.vcsclients.mercurial import MercurialClient
from committer.vcsclients.subversion import SubversionClient


def detect_vcs_client():
    """
        runs vcs client detection on the current directory.

        @raise CommitterException: when no or more than one vcs client detected.
        @return: the vcs client for the current working directory.
    """
    detected_vcs_clients = _detect_all_vcs_clients()

    if not detected_vcs_clients:
        raise errors.NoRepositoryDetectedError()

    if len(detected_vcs_clients) > 1:
        raise errors.TooManyRepositoriesError(detected_vcs_clients)

    vcs_client = detected_vcs_clients[0]
    return _ensure_executable(vcs_client)


def _ensure_executable(vcs_client):
    """
        ensures the given vcs client is executable.

        @raise CommiterException: when the command line client is not executable.
        @return: the given vcs client
    """
    if not vcs_client.is_executable():
        raise errors.NotExecutableError(vcs_client)

    return vcs_client


def _detect_all_vcs_clients():
    """
        runs detection on all available vcs clients.

        @return: list of vcs clients
    """
    vcs_clients = _list_available_vcs_clients()

    return [vcs_client for vcs_client in vcs_clients if vcs_client.detect()]


def _list_available_vcs_clients():
    """
        @return: list of all available vcs clients.
    """
    return [GitClient(), MercurialClient(), SubversionClient()]
