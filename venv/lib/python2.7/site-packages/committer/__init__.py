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
    committer provides a unified and simplified command line interface to
    the version control systems: git, mercurial, and subverion.
"""

__author__ = 'Michael Gruber'
__version__ = '0.2.7'

try:
    from ConfigParser import ConfigParser
except:
    from configparser import ConfigParser

from logging import DEBUG, INFO, Formatter, StreamHandler, getLogger
from os.path import exists
from sys import exit

from committer import errors
from committer.actions import commit, status, update
from committer.execution import execute_command

LOGGING_FORMAT = '%(message)s'
CONFIGURATION_FILE_NAME = '.committerrc'
SECTION_DEFAULT = "DEFAULT"
SECTION_COMMIT = "COMMIT"
OPTION_EXECUTE_BEFORE = "execute_before"


USAGE_INFORMATION = """
Usage:
    ci "message"     commits all changes
    st               shows all changes
    up               updates the current directory

Options:
    -h --help        show this help screen
    --debug          enable logging of debug messages
    --version        show version information
"""


def initialize_root_logger(log_level=INFO):
    """ Returnes a root_logger which logs to the console using the given log_level. """
    formatter = Formatter(LOGGING_FORMAT)

    console_handler = StreamHandler()
    console_handler.setFormatter(formatter)

    root_logger = getLogger(__name__)
    root_logger.setLevel(log_level)
    root_logger.addHandler(console_handler)

    return root_logger

LOGGER = initialize_root_logger(INFO)


class Configuration():
    """ Committer configration """
    def __init__(self):
        self.execute_before = None
        self.execute_before_commit = None


class ScriptCommand(object):
    """
        Decorator for functions which are called from scripts.
    """
    def __init__(self, function):
        self.function = function

    def _handle_debug_argument(self, arguments):
        """
            Sets the log level to DEBUG, if arguments contains --debug.
        """
        if '--debug' in arguments:
            LOGGER.setLevel(DEBUG)
            LOGGER.debug('Logging of debug messages enabled.')
            return [argument for argument in arguments if argument != '--debug']
        return arguments

    def _handle_version_argument(self, arguments):
        """
            Shows the version and exits the program, if arguments contains --version.
        """
        if '--version' in arguments:
            LOGGER.info('%s version %s', __name__, __version__)
            return exit(0)

    def _handle_help_argument(self, arguments):
        """
            Shows the usage information and exits the program, if arguments contains
            help, --help, or -h.
        """
        for help_option in ['help', '--help', '-h']:
            if help_option in arguments:
                LOGGER.info(USAGE_INFORMATION)
                return exit(0)

    def _filter_unused_argument_dash_m(self, arguments):
        """
            Returns a list which equals the given one, but removes the string '-m' from it.
        """
        return [argument for argument in arguments if argument != '-m']

    def _read_configuration_file(self):
        """
            Returns a configuration object
        """
        configuration = Configuration()
        if not exists(CONFIGURATION_FILE_NAME):
            return configuration

        config_parser = ConfigParser()
        config_parser.read(CONFIGURATION_FILE_NAME)

        if config_parser.has_option(SECTION_DEFAULT, OPTION_EXECUTE_BEFORE):
            configuration.execute_before = config_parser.get(SECTION_DEFAULT, OPTION_EXECUTE_BEFORE)

        if config_parser.has_option(SECTION_COMMIT, OPTION_EXECUTE_BEFORE):
            configuration.execute_before_commit = config_parser.get(SECTION_COMMIT, OPTION_EXECUTE_BEFORE)

        return configuration

    def __call__(self, arguments):
        """
            performs the given command using the given arguments.
        """
        filtered_arguments = self._filter_unused_argument_dash_m(arguments)
        configuration = self._read_configuration_file()

        if len(filtered_arguments) > 1:
            filtered_arguments = self._handle_debug_argument(filtered_arguments)
            self._handle_version_argument(filtered_arguments)
            self._handle_help_argument(filtered_arguments)

        if configuration.execute_before:
            LOGGER.debug('Executing command "%s" before doing anything else.', configuration.execute_before)
            command_and_arguments = configuration.execute_before.split()
            execute_command(command_and_arguments[0], *command_and_arguments[1:])

        try:
            self.function(filtered_arguments, configuration)
            return exit(0)

        except errors.CommitterError as committer_exception:
            LOGGER.error(committer_exception.message)
            return exit(committer_exception.error_code)

        except KeyboardInterrupt:
            LOGGER.error('Interrupted by user.\n')
            return exit(1)


@ScriptCommand
def commit_changes(arguments, configuration=None):
    if configuration.execute_before_commit:
        command_and_arguments = configuration.execute_before_commit.split()
        execute_command(command_and_arguments[0], *command_and_arguments[1:])

    commit(arguments)


@ScriptCommand
def show_status(arguments, configuration=None):
    status(arguments)


@ScriptCommand
def update_files(arguments, configuration=None):
    update(arguments)
