#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
gitolite-manager
Author: Tim Henderson
Contact: tim.tadh@gmail.com, tadh@case.edu
Copyright: 2013 All Rights Reserved, see LICENSE
'''


import urllib, re
import xml.etree.ElementTree as ET
from logging import getLogger
log = getLogger('gm:view:login')

import requests
from pyramid.view import view_config
from pyramid import httpexceptions as httpexc
from pyramid.httpexceptions import HTTPFound, HTTPBadRequest
from pyramid.response import Response

from gitolite_manager import validate as v
from gitolite_manager.controllers import user_controller
from gitolite_manager.models.session import Session
from gitolite_manager.models.user import User


@view_config(
    route_name='root',
    request_method=['GET'],
    )
def get_root(request):
    config = request.environ['config']
    db = request.environ['db.session']
    cas_url = config.get_settings()['cas_url']
    session = request.environ['gm_session']
    if session.user is None:
        return HTTPFound(cas_url + 'login?service=' +
            urllib.quote(request.route_url("login")))
    return HTTPFound(request.route_url("user"))


login_schema = {
  'ticket':
    v.type_checker(basestring) &
    v.format_checker(re.compile(r'^ST-[0-9A-Fr]{29}$')),
}

@view_config(
    route_name='login',
    request_method=['GET'],
    )
def login(request):
    config = request.environ['config']
    db = request.environ['db.session']
    session = request.environ['gm_session']
    cas_url = config.get_settings()['cas_url']

    err, get = v.validate_dictionary(dict(request.GET), login_schema)
    if err:
        raise HTTPBadRequest(str(err))
    cas_response = requests.get(
       cas_url + 'serviceValidate?ticket=' +
      urllib.quote(get['ticket']) +
      '&service=' +
      urllib.quote(request.route_url("login"))
    )

    case_id = None
    if 'cas:authenticationSuccess' in cas_response.text:
        try:
            root = ET.fromstring(cas_response.text)
            case_id = root.getchildren()[0].getchildren()[0].text
        except Exception, e:
            log.error(e)
            raise HTTPBadRequest("CAS auth failure")
    elif 'cas:authenticationFailure' in cas_response.text:
        return HTTPFound(cas_url + 'login?service=' +
            urllib.quote(request.route_url("login")))
    else:
        raise HTTPBadRequest("Unexpected result from CAS")

    email = '%s@case.edu' % case_id
    user = db.query(User).filter_by(email=email).first()
    if user is None:
        user = user_controller.add_user(db, case_id)
    if not session.update_user(db, user):
        raise HTTPBadRequest("Bad session")

    return HTTPFound(request.application_url)

