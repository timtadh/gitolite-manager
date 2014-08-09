#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
gitolite-manager
Author: Tim Henderson
Contact: tim.tadh@gmail.com, tadh@case.edu
Copyright: 2013 All Rights Reserved, see LICENSE
'''

import os
import subprocess, tempfile
from logging import getLogger
log = getLogger('gm:ctl:repo')

import sqlalchemy as sa
from pyramid.renderers import render
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest

from gitolite_manager.models.user import User
from gitolite_manager.controllers.config import ROOT, ADMIN, REPOS_DIR
from gitolite_manager.controllers.git import (
    git_add, git_rm, git_commit, git_push
)


def add_user(db, user_name):
    email = '%s@case.edu' % user_name
    user = User(email)
    db.add(user)
    db.commit()

    conf = render('templates/users_repo.conf.jinja2', {
      'user_name': user.name(),
    })

    path = os.path.join(REPOS_DIR, "%s.conf" % user.name())
    try:
        with open(path, 'w') as f:
            f.write(conf)

        git_add()
        git_commit('added user, %s, conf' % user.name())
        git_push()
    except Exception, e:
        log.exception(e)
        db.delete(user)
        db.commit()
        raise
    return user

