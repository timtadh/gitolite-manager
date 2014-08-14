#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
gitolite-manager
Author: Tim Henderson
Contact: tim.tadh@gmail.com, tadh@case.edu
Copyright: 2013 All Rights Reserved, see LICENSE
'''

import os, subprocess, tempfile
import contextlib
from logging import getLogger
log = getLogger('gm:ctl:keys')

import sqlalchemy as sa
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest

from gitolite_manager.models.keys import Key
from gitolite_manager.controllers.git import (
    git_add, git_rm, git_commit, git_push
)

PREFIXES = set([
  'ssh-ed25519', 'ssh-rsa', 'ssh-dss', 'ecdsa-sha2-nistp256',
  'ecdsa-sha2-nistp384', 'ecdsa-sha2-nistp521',

])


def validate_prefix(key):
    split = key.split(' ', 1)
    if len(split) == 2:
        prefix, rest = split
        if prefix in PREFIXES:
            return
    raise Exception, "key was not in the correct format"


def add_key(db, user, key):
    key = key.strip()
    if 'PRIVATE' in key:
        raise Exception('You must submit the public key not the private')
    validate_prefix(key)
    try:
        with tempfile.NamedTemporaryFile(suffix=".pub") as t:
            t.write(key + "\n")
            t.flush()
            path = t.name
            subprocess.check_call(['ssh-keygen', '-lf', path])
    except subprocess.CalledProcessError, e:
        print user, key, path
        raise Exception("That key was not in the correct format")
    except Exception, e:
        raise Exception("There was a problem adding that key: "+ str(e) + " " + str(type(e)))
    key = Key(user, key)
    db.add(key)
    db.commit()

    try:
        with open(key.path(), 'w') as f:
            f.write(key.key)

        git_add()
        git_commit('added %s key %d' % (user.name(), key.id))
        git_push()
    except Exception, e:
        log.exception(e)
        db.delete(key)
        db.commit()


def rm_key(db, user, key_id):
    key = db.query(Key).filter(Key.id==key_id, Key.user_id==user.id).first()
    try:
        git_rm(key.path())
    except Exception, e:
        log.exception(e)
        db.add(key)
        db.commit()
        return
    db.delete(key)
    db.commit()
    git_commit('rm %s key %d' % (user.name(), key_id))
    git_push()

