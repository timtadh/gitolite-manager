#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
gitolite-manager
Author: Tim Henderson
Contact: tim.tadh@gmail.com, tadh@case.edu
Copyright: 2013 All Rights Reserved, see LICENSE
'''

import os, subprocess
import contextlib

from gitolite_manager.controllers.config import ROOT, ADMIN, KEY_DIR


@contextlib.contextmanager
def chdir(directory):
    pwd = os.getcwd()
    try:
        os.chdir(directory)
        yield
    finally:
        os.chdir(pwd)


def git_add():
    with chdir(ADMIN):
        subprocess.check_call([
          'git', 'add', '--all', '.'
        ])


def git_rm(path):
    with chdir(ADMIN):
        subprocess.check_call([
          'git', 'rm', '-f', path
        ])


def git_commit(msg):
    with chdir(ADMIN):
        subprocess.check_call([
          'git', 'commit', '-sm', msg
        ])


def git_push():
    with chdir(ADMIN):
        subprocess.check_call([
          'git', 'push'
        ])


