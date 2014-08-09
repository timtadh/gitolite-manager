#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
gitolite-manager
Author: Tim Henderson
Contact: tim.tadh@gmail.com, tadh@case.edu
Copyright: 2013 All Rights Reserved, see LICENSE
'''


import urllib, re
import cgi
from logging import getLogger
log = getLogger('gm:view:user')

from pyramid.view import view_config
from pyramid import httpexceptions as httpexc
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from pyramid.response import Response

from gitolite_manager import validate as v
from gitolite_manager.models.session import Session
from gitolite_manager.models.user import User
from gitolite_manager.controllers import key_controller, repo_controller

def get_user_name(user):
    email = user.email
    return email[:email.index('@')]

def tvars(request, extras):
    session = request.environ['gm_session']
    defaults = {
        'SITENAME' : 'Key Czar',
        'SITEURL' : request.application_url,
        'request' : request,
        'session' : session,
        'get_user_name' : get_user_name,
    }
    defaults.update(extras)
    print defaults
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
        return HTTPFound(request.application_url)

    email = session.user.email
    user = email[:email.index('@')]
    return tvars(request, {
        'TITLE' : user + ' user',
        'user_name' : user,
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
        return HTTPFound(request.application_url)

    email = session.user.email
    user = email[:email.index('@')]
    return tvars(request, {
        'TITLE' : 'keys for %s' % user,
        'user_name' : user,
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
        return HTTPFound(request.application_url)

    email = session.user.email
    user = email[:email.index('@')]
    return tvars(request, {
        'TITLE' : 'add key for %s' % user,
        'user_name' : user,
    })

addkey_schema = {
    'key': v.type_checker(cgi.FieldStorage),
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
        return HTTPFound(request.route_url("root"))

    email = session.user.email
    user = email[:email.index('@')]

    err, post = v.validate_dictionary(dict(request.POST), addkey_schema)
    if err:
        return tvars(request, {
            'TITLE' : 'add key for %s' % user,
            'user_name' : user,
            'errors': err,
        })
    elif not session.valid_csrf(post['csrf'], request.route_url('user/addkey')):
        return HTTPFound(request.route_url('root'))
    else:
        try:
            key = post['key'].file.read()
            key_controller.add_key(db, session.user, key)
        except Exception, e:
            log.exception(e)
            return tvars(request, {
                'TITLE' : 'add key for %s' % user,
                'user_name' : user,
                'errors': [e],
            })
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
        return HTTPFound(request.application_url)

    email = session.user.email
    user = email[:email.index('@')]

    err, match = v.validate_dictionary(dict(request.matchdict), rmkey_schema)
    if err:
        return tvars(request, {
            'TITLE' : 'remove key for %s' % user,
            'user_name' : user,
            'errors': err,
        })
    try:
        key_controller.rm_key(db, session.user, int(match['keyid']))
    except Exception, e:
        return tvars(request, {
            'TITLE' : 'remove key for %s' % user,
            'user_name' : user,
            'errors': [str(e)],
        })
    return HTTPFound(request.route_url('user/keys'))

@view_config(
    route_name='user/partners',
    request_method=['GET'],
    renderer='templates/add-partner.html'
)
def partners(request):
    db = request.environ['db.session']
    session = request.environ['gm_session']
    if session.user is None:
        return HTTPFound(request.application_url)

    email = session.user.email
    user = email[:email.index('@')]
    return tvars(request, {
        'TITLE' : 'partners for %s' % user,
        'user_name' : user,
    })

add_partner_schema = {
    'csrf': v.type_checker(basestring),
    'case_id': v.type_checker(basestring) &
               v.format_checker(re.compile(r'[a-z]{3}[0-9]*')),
    'repo_name': v.type_checker(basestring) &
                 v.format_checker(re.compile(r'[a-zA-Z][a-zA-Z0-9_-]*')),
}

@view_config(
    route_name='user/add-partner',
    request_method=['POST'],
    renderer='templates/add-partner.html'
)
def add_partners(request):
    db = request.environ['db.session']
    session = request.environ['gm_session']
    if session.user is None:
        return HTTPFound(request.application_url)

    email = session.user.email
    user = email[:email.index('@')]

    err, post = v.validate_dictionary(dict(request.POST), add_partner_schema)
    if err:
        return tvars(request, {
            'TITLE' : 'add partner for %s' % user,
            'user_name' : user,
            'errors': err,
        })
    elif not session.valid_csrf(post['csrf'], request.route_url('user/add-partner')):
        return HTTPFound(request.route_url('root'))
    else:
        try:
            repo_controller.add_partner(db, session.user, post['case_id'],
                post['repo_name'])
        except Exception, e:
            return tvars(request, {
                'TITLE' : 'add partner for %s' % user,
                'user_name' : user,
                'errors': [e],
            })
        return HTTPFound(request.route_url('user/partners'))

rm_partner_schema = {
    'repo_id': v.type_checker(basestring) &
               v.format_checker(re.compile(r'[0-9]+')),
}

@view_config(
    route_name='user/rm-partner',
    request_method=['GET'],
    renderer='templates/rm-partner.html'
)
def rm_partner(request):
    db = request.environ['db.session']
    session = request.environ['gm_session']
    if session.user is None:
        return HTTPFound(request.application_url)

    email = session.user.email
    user = email[:email.index('@')]

    err, match = v.validate_dictionary(dict(request.matchdict), rm_partner_schema)
    if err:
        return tvars(request, {
            'TITLE' : 'remove partner for %s' % user,
            'user_name' : user,
            'errors': err,
        })
    try:
        repo_controller.rm_partner(db, session.user, int(match['repo_id']))
    except Exception, e:
        return tvars(request, {
            'TITLE' : 'remove partner for %s' % user,
            'user_name' : user,
            'errors': [str(e)],
        })
    return HTTPFound(request.route_url('user/partners'))
