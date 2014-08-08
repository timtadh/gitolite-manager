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
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest

from gitolite_manager.models.user import User
from gitolite_manager.models.repo import Repo


def add_partner(db, user, partner_case_id, repo_name):
    partner_email = "%s@case.edu" % partner_case_id
    partner = db.query(User).filter_by(email=partner_email).first()
    print partner_email
    if partner is None:
        raise Exception, "Partner has not yet made an account"

    has = db.query(Repo).filter(Repo.user_id==user.id and
        Repo.partner_id==partner.id and Repo.name == repo_name).first()
    if has:
        raise Exception, "You have already associated your partner with that repository"
    repo = Repo(user, partner, repo_name)
    db.add(repo)
    db.commit()

def rm_partner(db, user, repo_id):
    db.query(Repo).filter(Repo.id==repo_id, Repo.user_id==user.id).delete()
    db.commit()

