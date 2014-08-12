#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
gitolite-manager
Author: Tim Henderson
Contact: tim.tadh@gmail.com, tadh@case.edu
Copyright: 2013 All Rights Reserved, see LICENSE
'''

import subprocess, tempfile
from logging import getLogger
log = getLogger('gm:ctl:repo')

import sqlalchemy as sa
from pyramid.renderers import render
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest

from gitolite_manager.models.user import User
from gitolite_manager.models.repo import Repo
from gitolite_manager.controllers.git import (
    git_add, git_rm, git_commit, git_push
)


def add_partner(db, user, partner_case_id, repo_name):
    partner_email = "%s@case.edu" % partner_case_id
    partner = db.query(User).filter_by(email=partner_email).first()
    if partner is None:
        raise Exception, "Partner has not yet made an account"

    has = db.query(Repo).filter((Repo.user_id==user.id) &
                                (Repo.partner_id==partner.id) &
                                (Repo.name == repo_name)).first()
    if has:
        raise Exception, "You have already associated your partner with that repository"
    repo = Repo(user, partner, repo_name)
    db.add(repo)
    db.commit()

    conf = render('templates/repo.conf.jinja2', {
      'user_name': repo.user.name(),
      'partner_name': repo.partner.name(),
      'repo_name': repo.name,
    })

    try:
        with open(repo.path(), 'w') as f:
            f.write(conf)

        git_add()
        git_commit('added %s to %s/%s' % (repo.partner.name(), repo.user.name(),
          repo.name))
        git_push()
    except Exception, e:
        log.exception(e)
        db.delete(repo)
        db.commit()

def rm_partner(db, user, repo_id):
    repo = db.query(Repo).filter(Repo.id==repo_id, Repo.user_id==user.id).first()
    try:
        git_rm(repo.path())
    except Exception, e:
        log.exception(e)
        db.add(repo)
        db.commit()
        return
    git_commit('removed %s from %s/%s' % (repo.partner.name(), repo.user.name(),
      repo.name))
    db.delete(repo)
    db.commit()
    git_push()


