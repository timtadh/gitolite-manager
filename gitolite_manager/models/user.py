#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
gitolite-manager
Author: Tim Henderson
Contact: tim.tadh@gmail.com, tadh@case.edu
Copyright: 2013 All Rights Reserved, see LICENSE
'''


import os, datetime, logging
log = logging.getLogger('gm:models:user')

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base

from gitolite_manager.models import Base


DEBUG = True


class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'mysql_engine':'InnoDB'}
    id = sa.Column(sa.Integer, primary_key=True, index=True, unique=True)
    email = sa.Column(sa.String(120), unique=True, index=True)
    created = sa.Column(sa.DateTime())
    access = sa.Column(sa.DateTime())

    def __init__(self, email):
        self.email = email
        self.created = datetime.datetime.utcnow()
        self.access = datetime.datetime.utcnow()

    def __repr__(self):
        return '<User %r, %s, %s>' % (self.email, self.created, self.access)

    def name(self):
        return self.email[:self.email.index('@')]
