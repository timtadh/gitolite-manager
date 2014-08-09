#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
gitolite-manager
Author: Tim Henderson
Contact: tim.tadh@gmail.com, tadh@case.edu
Copyright: 2013 All Rights Reserved, see LICENSE
'''

import os


ROOT = os.environ['GITOLITE_MANAGER_ROOT']
ADMIN = os.path.join(ROOT, 'gitolite-admin')
KEY_DIR = os.path.join(ADMIN, 'keydir')
CONF_DIR = os.path.join(ADMIN, 'conf')
REPOS_DIR = os.path.join(CONF_DIR, 'repos')

