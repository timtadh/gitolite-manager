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
log = getLogger('gm:ctl:keys')

import sqlalchemy as sa
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest

from gitolite_manager.models.keys import Key


def add_key(db, user, key):
    key = key.strip()
    try:
        with tempfile.NamedTemporaryFile() as t:
            t.write(key)
            t.flush()
            path = t.name
            subprocess.check_call(['ssh-keygen', '-lf', path])
    except subprocess.CalledProcessError, e:
        print user, key, path
        raise HTTPBadRequest("That key was not in the correct format")
    except Exception, e:
        raise HTTPBadRequest("There was a problem adding that key: "+ str(e) + " " + str(type(e)))
    key = Key(user, key)
    db.add(key)
    db.commit()

def rm_key(db, user, key_id):
    db.query(Key).filter(Key.id==key_id, Key.user_id==user.id).delete()
    db.commit()

