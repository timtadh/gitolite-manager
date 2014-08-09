#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
gitolite-manager
Author: Tim Henderson
Contact: tim.tadh@gmail.com, tadh@case.edu
Copyright: 2013 All Rights Reserved, see LICENSE
'''


import os
import logging
log = logging.getLogger('gm:models:keys')

import sqlalchemy as sa

from gitolite_manager.models import Base, user
from gitolite_manager.controllers.config import ROOT, ADMIN, KEY_DIR


class Key(Base):
    __tablename__ = 'key'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = sa.Column(sa.Integer, primary_key=True, index=True, unique=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), index=True)
    key = sa.Column(sa.String(1000))

    user = sa.orm.relationship(user.User, backref=sa.orm.backref('keys', order_by=id, ))


    def __init__(self, user, key):
        self.user = user
        self.key = key

    def path(self):
        return os.path.join(KEY_DIR, '%s@%d.pub' % (self.user.name(), self.id))
