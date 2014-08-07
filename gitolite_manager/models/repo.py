#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
gitolite-manager
Author: Tim Henderson
Contact: tim.tadh@gmail.com, tadh@case.edu
Copyright: 2013 All Rights Reserved, see LICENSE
'''



import logging
log = logging.getLogger('gm:models:repo')

import sqlalchemy as sa

from gitolite_manager.models import Base
from gitolite_manager.models.user import User


class Repo(Base):
    __tablename__ = 'repo'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = sa.Column(sa.Integer, primary_key=True, index=True, unique=True)
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), index=True)
    partner_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'), index=True)
    name = sa.Column(sa.String(32))

    user = sa.orm.relationship(User,
        backref=sa.orm.backref('repos', order_by=id),
        foreign_keys=[user_id])
    partner = sa.orm.relationship(User,
        backref=sa.orm.backref('partner_repos', order_by=id), 
        foreign_keys=[user_id])


    def __init__(self, user, partner, name):
        self.user = user
        self.partner = partner
        self.name = name


