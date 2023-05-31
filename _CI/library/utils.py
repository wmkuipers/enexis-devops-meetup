#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: utils.py
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


def get_arguments_from_docker_file(docker_file):
    return [line.split()[1].strip() for
            line in open(docker_file, 'r').read().splitlines()
            if line.strip().startswith('ARG')]


def get_variables_from_build_env(build_env):
    try:
        args = {line.split('=', 1)[0]: line.split('=', 1)[1]
                for line in open(build_env, 'r').read().splitlines()
                if not line.strip().startswith('#') and line.strip()}
    except IOError:
        args = {}
    return args


def get_version():
    from library.library import get_version_file_path
    with open(get_version_file_path(), 'r') as version_file:
        version = version_file.read().strip()
        version_file.close()
    return version