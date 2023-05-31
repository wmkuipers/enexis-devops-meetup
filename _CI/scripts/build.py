#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: build.py
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
import json
from base64 import b64encode
from bootstrap import bootstrap
from library import execute_command, clean_up, save_requirements
from configuration import ( BUILD_WITH_KANIKO,
                            KANIKO_IMAGE,
                            VAULT_URL,
                            VAULT_TOKEN,
                            DOCKER_CREDS_VAULT_LOCATION,
                            VIRTUAL_REPO,
                            BUILD_ARGS_FILE)
from hashivaultlib import Vault

# This is the main prefix used for logging
LOGGER_BASENAME = '''_CI.build'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


def _build():
    from library.utils import get_variables_from_build_env
    registry_name = os.environ.get('DOCKER_REGISTRY_URL', "ERROR: registry not specified on environment as DOCKER_REGISTRY_URL")
    image_name = os.environ.get('DOCKER_IMAGE_NAME', "ERROR: docker-image name not specified on environment as DOCKER_IMAGE_NAME")

    LOGGER.info("Setting up build arguments")
    arguments = get_variables_from_build_env(BUILD_ARGS_FILE)
    cli_arguments = " ".join([f"--build-arg {arg}={value}" for arg, value in arguments.items()]) or ''
    if 'PIP_EXTRA_INDEX_URL' in os.environ:
        LOGGER.info("PIP_EXTRA_INDEX_URL is specified on environment, injecting into build")
        cli_arguments = " ".join([cli_arguments, f' --build-arg PIP_EXTRA_INDEX_URL={os.environ.get("PIP_EXTRA_INDEX_URL")} '])
    LOGGER.info("Initializing a Vault connection")
    try:
        LOGGER.info("Initializing a Vault connection")
        vault = Vault(VAULT_URL, VAULT_TOKEN)
        LOGGER.info(f"Trying to read docker credentials from Vault path: {DOCKER_CREDS_VAULT_LOCATION} ")
        docker_creds = vault.retrieve_secrets_from_path(DOCKER_CREDS_VAULT_LOCATION)[0].get("data",{})
        execute_command(f'docker login  -u {docker_creds.get("username","")} -p {docker_creds.get("password","")} {VIRTUAL_REPO}')
    except Exception as err:
        LOGGER.error("Could not get Read Only credentials for the repository specified. Invalid vault token OR no route over vpn found")
        LOGGER.error(err)
        return False

    if BUILD_WITH_KANIKO:
        current_directory = os.getcwd()
        auth_file = { "auths":
                        { VIRTUAL_REPO:{
                            "username": docker_creds.get("username",""),
                            "password": docker_creds.get("password","")
                        }}}
        if not os.path.exists('./.docker/'):
            os.mkdir(f"{current_directory}/.docker/")
        open(f"{current_directory}/.docker/config.json", "w").write(json.dumps(auth_file))
        LOGGER.info(f"Starting build with kaniko image {KANIKO_IMAGE}")
        command = " ".join([    "docker run -it",
                                "--entrypoint=executor",
                                f"-v {current_directory}:{current_directory}:ro",
                                f"-v {current_directory}/.docker/:/kaniko/.docker/:ro",
                                f"{KANIKO_IMAGE}",
                                f"--dockerfile {current_directory}/Dockerfile",
                                f"--context {current_directory}/",
                                f"{cli_arguments}",
                                "--no-push",
                                "--single-snapshot "])
        LOGGER.info(f"Executing command:\n{command}")
        success = execute_command(command)
        if os.path.exists(f"{current_directory}/.docker/config.json"):
            os.remove(f"{current_directory}/.docker/config.json")
            if len(os.listdir(f"{current_directory}/.docker/")) == 0:
                os.rmdir(f"{current_directory}/.docker/")
    else:
        build_command = f'docker build {cli_arguments} -t {registry_name}/{image_name}:latest .'
        success = execute_command(build_command)

    return success


def build():
    emojize = bootstrap()
    success = _build()
    if success:
        LOGGER.info('%s Successfully built artifact %s',
                    emojize(':white_check_mark:', language='alias'),
                    emojize(':thumbs_up:'))
    else:
        LOGGER.error('%s Errors building artifact! %s',
                     emojize(':cross_mark:'),
                     emojize(':crying_face:'))
    return emojize if success else None


if __name__ == '__main__':
    raise SystemExit(0 if build() else 1)
