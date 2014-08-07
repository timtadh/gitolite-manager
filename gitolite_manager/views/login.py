#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
gitolite-manager
Author: Tim Henderson
Contact: tim.tadh@gmail.com, tadh@case.edu
Copyright: 2013 All Rights Reserved, see LICENSE
'''


from logging import getLogger
log = getLogger('gm:view:login')

from pyramid.view import view_config
from pyramid import httpexceptions as httpexc
from pyramid.httpexceptions import HTTPFound

from reportservice.util import validate as v






@view_config(
    route_name='template/language/rule_name/role/fallthrough',
    request_method=['GET'],
    renderer='json')
def get_template_lang_rule_role_with_fallthrough(request):
    db = request.environ['db.session']
    matchdict = validate_template_matchdict(request)
    lang = matchdict['language']
    rule_name = matchdict['rule_name']
    role = matchdict['role']
    t = Template.get(db, lang=lang, role=role, rule=rule_name)
    if t is None:
        raise httpexc.HTTPNotFound("could not find template")
    return {
        'ok' : True,
        'template': t.json,
    }

