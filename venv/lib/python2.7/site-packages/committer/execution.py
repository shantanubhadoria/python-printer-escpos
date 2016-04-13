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
    This module offers utility functions for execution within sub processes.
"""

__author__ = 'Michael Gruber'

from sys import exit
from logging import getLogger
from subprocess import PIPE, CalledProcessError, Popen, check_call

LOGGER = getLogger(__name__)

LINE_BUFFERED = 1


def check_if_is_executable(command, *arguments):
    """
        Executes the given command with the given arguments.

        @return: True if the given command is executable with the given arguments,
                 False otherwise.
    """
    try:
        command_with_arguments = [command] + list(arguments)
        check_call(command_with_arguments)

    except CalledProcessError:
        return False

    except OSError:
        return False

    return True


def execute_command(command, *arguments):
    """
        Executes command using the given arguments.
    """
    command_with_arguments = [command] + list(arguments)
    LOGGER.debug('Executing command with arguments: %s', command_with_arguments)

    try:
        process = Popen(command_with_arguments,
                        bufsize=LINE_BUFFERED,
                        stdout=PIPE,
                        stderr=PIPE,
                        stdin=PIPE)  # because sometimes we need to enter something during execution (e.g. credentials)

        stdout = ''

        for line in process.stdout:
            if line.endswith('\n'):
                LOGGER.info(line[:-1])
            else:
                LOGGER.info(line)
            stdout += line

        _, stderr = process.communicate()
    except OSError as os_error:
        LOGGER.error('Execution of "%s" failed: %s', " ".join(command_with_arguments), str(os_error))
        return exit(1)

    if stderr != '':
        LOGGER.error(stderr)

    returncode = process.returncode

    if returncode != 0:
        return exit(1)

    return {'stdout': stdout, 'stderr': stderr, 'returncode': returncode}
