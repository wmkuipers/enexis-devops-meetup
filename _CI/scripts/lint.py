#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: lint.py
#
# Copyright 2018 Costas Tyfoxylos
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
#

import logging
import os
from platform import platform
from bootstrap import bootstrap
from library import execute_command, is_pipeline_context
from configuration import HADOLINT_CONTAINER, VAULT_URL, VAULT_TOKEN, DOCKER_CREDS_VAULT_LOCATION, VIRTUAL_REPO



# This is the main prefix used for logging
LOGGER_BASENAME = '''_CI.lint'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


def lint():
    emojize = bootstrap()
    if os.environ.get("SKIP_LINTING", "False") == "True":
        LOGGER.info("Skipping linting as defined with the environment variable SKIP_LINTING")
        SystemExit(0)

    if is_pipeline_context():
        success = execute_command(f'hadolint --config hadolint.yaml Dockerfile')
    else:
        try:
            from hashivaultlib import Vault
            current_directory = os.getcwd()
            vault = Vault(VAULT_URL, VAULT_TOKEN)
            LOGGER.info(f"Trying to read docker credentials from Vault path: {DOCKER_CREDS_VAULT_LOCATION} ")
            docker_creds = vault.retrieve_secrets_from_path(DOCKER_CREDS_VAULT_LOCATION)[0].get("data",{})
            execute_command(f'docker login  -u {docker_creds.get("username","")} -p {docker_creds.get("password","")} {VIRTUAL_REPO}')
            command = " ".join([    "docker run -it",
                                    f"-v {current_directory}:{current_directory}:ro",
                                    f"{HADOLINT_CONTAINER}",
                                    f"hadolint --config {current_directory}/hadolint.yaml {current_directory}/Dockerfile"])
            success = execute_command(command)
        except Exception as err:
            LOGGER.error(err)
            success = False
    if success:
        LOGGER.info('%s No linting errors found! %s',
                    emojize(':white_check_mark:', language='alias'),
                    emojize(':thumbs_up:'))
    else:
        LOGGER.error('%s Linting errors found! %s',
                     emojize(':cross_mark:'),
                     emojize(':crying_face:'))
    raise SystemExit(0 if success else 1)


if __name__ == '__main__':
    lint()
