#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
gitolite-manager
Author: Tim Henderson
Contact: tim.tadh@gmail.com, tadh@case.edu
Copyright: 2013 All Rights Reserved, see LICENSE
'''


import os, datetime, hashlib, hmac, logging
log = logging.getLogger('gm:models:session')

import sqlalchemy as sa

from gitolite_manager.models import Base, user


class Session(Base):
    __tablename__ = 'session'
    __table_args__ = {'mysql_engine':'InnoDB'}

    id = sa.Column(sa.Integer, primary_key=True, index=True, unique=True)
    key = sa.Column(sa.String(64), index=True, unique=True)
    sig = sa.Column(sa.LargeBinary(32))
    sigkey = sa.Column(sa.LargeBinary(32))
    micro = sa.Column(sa.LargeBinary(3))
    csrf = sa.Column(sa.LargeBinary(32))
    user_id = sa.Column(sa.Integer, sa.ForeignKey('user.id'))
    last_update = sa.Column(sa.DateTime, index=True)

    user = sa.orm.relationship(user.User, backref=sa.orm.backref('sessions', order_by=id, ))


    def __init__(self, ipaddr, useragent):
        self.last_update = datetime.datetime.utcnow()
        self.sigkey = os.urandom(32)
        self.ipaddr = ipaddr
        self.useragent = useragent
        self.newkey()
        self.newcsrf()
        self.authenticated = None

    def newcsrf(self):
        ## interesting finds. the flask-csrf uses uuid.uuid4() function to get
        ## its random token. that function in turn uses os.urandom(16) to gets
        ## randomness unless libuuid (a c lib) is available on the system.
        ## libuuid.uuid_generate_random() uses os.urandom(16) (or rather
        ## /dev/urandom) if available. If /dev/urandom is DNE then it uses the
        ## current mac address and system time. If /dev/urandom is not available
        ## we are fucked anyway for this whole library so we might as well just
        ## use it straight away and make it work like the rest of the session
        ## library.
        self.csrf = os.urandom(32)
        log.debug('new csrf secret %s' % self.csrf.encode('hex'))

    def csrf_token(self, url):
        log.debug('csrf token url', url)
        log.debug('csrf secret', self.csrf.encode('hex'))
        h = hmac.new('', digestmod=hashlib.sha256)
        h.update(self.csrf)
        h.update(url)
        h.update(self.key.decode('hex')) ## in case the session key gets changed mid request. (logout)
        h.update(self.sigkey)
        for x in xrange(10000): h.update(h.digest())
        return h.hexdigest()

    def valid_csrf(self, token, url):
        current = self.csrf_token(url)
        return current == token

    def newkey(self):
        #print 'making a new key'
        self.key = os.urandom(32).encode('hex')
        self.sig = self.sign(self.key, self.ipaddr, self.useragent)

    def resign(self):
        #print 'resigning the key'
        self.sig = self.sign(self.key, self.ipaddr, self.useragent)

    def sign(self, msg, ipaddr, useragent, update=True):

        if self.micro is None:
            self.micro = '000'
        def micro():
            c = hex(self.last_update.microsecond)[2:]
            return (len(c)%2*'0'+c).decode('hex')
        if update == True:
            self.last_update = datetime.datetime.utcnow()
            self.micro = micro()
        h = hmac.new('', digestmod=hashlib.sha256)
        h.update(msg)
        h.update(''.join([chr(int(i)) for i in ipaddr.split('.')]))
        h.update(useragent)
        h.update(self.micro)
        h.update(self.sigkey)
        for x in xrange(10000): h.update(h.digest())
        digest = h.digest()
        if update == True: self.sig = digest
        return digest

    def authentic(self, msg):
        sig = self.sign(msg, self.ipaddr, self.useragent, update=False)
        self.authenticated = (sig == self.sig)
        return self.authenticated

    def update_time(self):
        if not self.authenticated: return False
        self.last_update = datetime.datetime.utcnow()
        self.resign()
        return True

    def update_user(self, cuser):
        if not self.authenticated: return False
        self.user_id = cuser.id
        self.newkey()
        log.debug('user set and new key issued', self.key)
        return True

    def logout(self):
        if not self.authenticated: return False
        self.user_id = None
        self.newkey()
        return True

    def __repr__(self):
        if self.user_id is not None:
            return '<Session %r %s>' % (self.key, self.user.email)
        return '<Session %r>' % self.key

