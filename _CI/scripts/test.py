#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: test.py
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

# this needs to be imported first as it manipulates the path
from bootstrap import bootstrap

# This is the main prefix used for logging
LOGGER_BASENAME = '''_CI.test'''
LOGGER = logging.getLogger(LOGGER_BASENAME)
LOGGER.addHandler(logging.NullHandler())


def _test(docker_file_path, build_env_file_path):
    from library.utils import get_arguments_from_docker_file, get_variables_from_build_env

    arguments = get_arguments_from_docker_file(docker_file_path)
    try:
        variables = get_variables_from_build_env(build_env_file_path)
    except IOError:
        print('No build-env file found!')
        variables = {}
    missing = [argument for argument in arguments
               if argument not in variables.keys()]
    if missing:
        for argument in missing:
            print(f'Argument "{argument}" required in Dockerfile is not provided!')
        result = False
    else:
        print('All required arguments are supplied!')
        result = True
    return result


def test():
    emojize = bootstrap()
    success = _test('Dockerfile', 'build-env')
    if success:
        LOGGER.info('%s No testing errors found! %s',
                    emojize(':white_check_mark:', language='alias'),
                    emojize(':thumbs_up:'))
    else:
        LOGGER.error('%s Testing errors found! %s',
                     emojize(':cross_mark:'),
                     emojize(':crying_face:'))
    raise SystemExit(0 if success else 1)


if __name__ == '__main__':
    test()
