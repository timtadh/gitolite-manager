#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
gitolite-manager
Author: Tim Henderson
Contact: tim.tadh@gmail.com, tadh@case.edu
Copyright: 2013 All Rights Reserved, see LICENSE
'''

import os, sys
from logging import getLogger
log = getLogger('gitolite-manger')

from pyramid.config import Configurator
from pyramid.response import Response
from sqlalchemy import engine_from_config

from gitolite_manager.models import Base, DBSessionFactory


def hello_world(request):
    return Response('Hello')

MAX_REQUEST_RETRY = 5
def db_session_adder(app, engine):
    def ware(environ, start_response):
        DBSessionFactory.configure(bind=engine)
        retry = True
        retry_count = 0
        while retry and retry_count < MAX_REQUEST_RETRY:
            retry = False
            session = DBSessionFactory()
            environ['db.session'] = session
            try:
                ret = app(environ, start_response)
            except sa.exc.OperationalError, e:
                session.rollback()
                log.exception('retrying request') 
                retry = True
                retry_count += 1
                if retry_count >= MAX_REQUEST_RETRY:
                    raise
            except:
                session.rollback()
                raise
            finally:
                session.flush()
                session.close()
                try: session.connection().close()
                except: pass
        return ret
    return ware

def routes(config):
    config.add_route('hello', '/')
    config.add_view(hello_world, route_name='hello')
    config.scan()

def main(global_config, **settings):
    log.info(settings)
    log.info(global_config)
    engine = engine_from_config(settings, 'sqlalchemy.')
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    routes(config)
    app = config.make_wsgi_app()
    app = db_session_adder(app, engine)
    return app

