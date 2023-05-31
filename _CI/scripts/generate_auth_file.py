#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: build.py
#
# Copyright 2021 Willem Kuipers.
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
                            VIRTUAL_REPO)
from hashivaultlib import Vault


def generate_auth():
    emojize = bootstrap()
    vault = Vault(VAULT_URL, VAULT_TOKEN)
    docker_creds = vault.retrieve_secrets_from_path(DOCKER_CREDS_VAULT_LOCATION)[0].get("data",{})
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
    return True


if __name__ == '__main__':
    raise SystemExit(0 if generate_auth() else 1)