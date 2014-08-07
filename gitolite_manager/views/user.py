#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
gitolite-manager
Author: Tim Henderson
Contact: tim.tadh@gmail.com, tadh@case.edu
Copyright: 2013 All Rights Reserved, see LICENSE
'''


import urllib, re
from logging import getLogger
log = getLogger('gm:view:user')

from pyramid.view import view_config
from pyramid import httpexceptions as httpexc
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from pyramid.response import Response

from gitolite_manager import validate as v
from gitolite_manager.models.session import Session
from gitolite_manager.models.user import User
from gitolite_manager.controllers import key_controller


def tvars(request, extras):
    session = request.environ['gm_session']
    defaults = {
        'SITENAME' : '337 Key Manager',
        'SITEURL' : request.application_url,
        'request' : request,
        'session' : session,
    }
    defaults.update(extras)
    return defaults

@view_config(
    route_name='user',
    request_method=['GET'],
    renderer='templates/user.html'
)
def user(request):
    db = request.environ['db.session']
    session = request.environ['gm_session']
    if session.user is None:
        return HTTPFound(request.application_url + "/login")

    email = session.user.email
    user = email[:email.index('@')]
    return tvars(request, {
        'TITLE' : user + ' user',
        'keys_url': request.route_url('user/keys'),
        'add_key_url': request.route_url('user/addkey'),
        'partners_url': request.route_url('user/partners'),
    })


@view_config(
    route_name='user/keys',
    request_method=['GET'],
    renderer='templates/keys.html'
)
def keys(request):
    db = request.environ['db.session']
    session = request.environ['gm_session']
    if session.user is None:
        return HTTPFound(request.application_url + "/login")

    email = session.user.email
    user = email[:email.index('@')]
    return tvars(request, {
        'TITLE' : 'keys for %s' % user,
    })


@view_config(
    route_name='user/addkey',
    request_method=['GET'],
    renderer='templates/addkey.html'
)
def addkey(request):
    db = request.environ['db.session']
    session = request.environ['gm_session']
    if session.user is None:
        return HTTPFound(request.application_url + "/login")

    email = session.user.email
    user = email[:email.index('@')]
    return tvars(request, {
        'TITLE' : 'add key for %s' % user,
    })

addkey_schema = {
    'key': v.type_checker(basestring) & v.min_length_checker(1),
    'csrf': v.type_checker(basestring)
}

@view_config(
    route_name='user/addkey',
    request_method=['POST'],
    renderer='templates/addkey.html'
)
def addkey_post(request):
    db = request.environ['db.session']
    session = request.environ['gm_session']
    if session.user is None:
        return HTTPFound(request.route_url("login"))

    email = session.user.email
    user = email[:email.index('@')]

    err, post = v.validate_dictionary(dict(request.POST), addkey_schema)
    if err:
        return tvars(request, {
            'TITLE' : 'add key for %s' % user,
            'errors': err,
        })
    elif not session.valid_csrf(post['csrf'], request.route_url('user/addkey')):
        return HTTPFound(request.route_url('root'))
    else:
        key_controller.add_key(db, session.user, post['key'])
        return HTTPFound(request.route_url('user/keys'))

rmkey_schema = {
    'keyid': v.type_checker(basestring) &
             v.format_checker(re.compile(r'[0-9]+')),
}

@view_config(
    route_name='user/rmkey',
    request_method=['GET'],
    renderer='templates/rmkey.html'
)
def rmkey(request):
    db = request.environ['db.session']
    session = request.environ['gm_session']
    if session.user is None:
        return HTTPFound(request.application_url + "/login")

    email = session.user.email
    user = email[:email.index('@')]

    err, match = v.validate_dictionary(dict(request.matchdict), rmkey_schema)
    if err:
        return tvars(request, {
            'TITLE' : 'remove key for %s' % user,
            'errors': err,
        })
    key_controller.rm_key(db, session.user, int(match['keyid']))
    return HTTPFound(request.route_url('user/keys'))

