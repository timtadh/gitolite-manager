#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
gitolite-manager
Author: Tim Henderson
Contact: tim.tadh@gmail.com, tadh@case.edu
Copyright: 2013 All Rights Reserved, see LICENSE
'''

import os, sys, time, datetime
from logging import getLogger
log = getLogger('gitolite-manger')

import sqlalchemy as sa
from pyramid.config import Configurator
from pyramid.response import Response
from pyramid.request import Request
import pyramid_jinja2
from sqlalchemy import engine_from_config

from gitolite_manager.models import Base, DBSessionFactory
from gitolite_manager.models.session import Session
from gitolite_manager.models.user import User

ROOT = os.environ['GITOLITE_MANAGER_ROOT']

def config_ware(app, config):
    def ware(environ, start_response):
        environ['config'] = config
        return app(environ, start_response)
    return ware


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



def cookie_session(app):

    COOKIE_NAME = 'gm_session'

    def open_session(db, request):
        engine = db.connection().engine

        log.info('----------- OPEN SESSION -------------------')

        timeout = 45

        def clear_old_sessions():

            if engine.name == 'sqlite':
                log.warn('USING BAD DELETE')
                for s in db.query(Session).all():
                    last_update = time.mktime(s.last_update.timetuple())
                    curtime = time.mktime(datetime.datetime.utcnow().timetuple())
                    if (last_update + int(60*timeout) <= curtime):
                        db.delete(s)
            elif engine.name == 'mysql':
                db.query(Session).filter(
                            func.timestampdiff(text('MINUTE'),
                                Session.last_update,
                                datetime.datetime.utcnow()) > timeout
                            ).delete(False)
            else:
                raise RuntimeError, "Unsupported engine " + engine.name
            db.commit()


        def newsession():
            log.info('New Session')
            session = Session(request.remote_addr, str(request.user_agent))
            log.info('New Session Key %s ' % session.key)
            db.add(session)
            db.commit()
            return session

        def loadsession():
            log.info('Try Load Session')
            if COOKIE_NAME in request.cookies:
                key = request.cookies[COOKIE_NAME]
                s = db.query(Session).filter_by(key=key).first()
                log.info('db session -> %s' % str(s))
                if s is not None:
                    s.ipaddr = request.remote_addr
                    s.useragent = str(request.user_agent)
                    if s.authentic(key):
                        log.info('is authentic')
                        return s
                    else:
                        log.info('is not authentic')
            return None

        def getsession():
            clear_old_sessions()
            session = loadsession()
            if session is None: session = newsession()
            return session

        return getsession()

    def save_session(db, session, request, response):
        log.info('----------- SAVE SESSION -------------------')
        if request.scheme == 'https':
            response.set_cookie(COOKIE_NAME, session.key, httponly=True,
                secure=True)
        else:
            response.set_cookie(COOKIE_NAME, session.key, httponly=True,
                secure=False)
        session.update_time()
        db.add(session)
        db.commit()

    def ware(environ, start_response):
        request = Request(environ)
        db = environ['db.session']
        session = open_session(db, request)
        request.environ['gm_session'] = session
        response = request.get_response(app)
        save_session(db, session, request, response)
        return response(environ, start_response)

    return ware

def routes(config):
    config.add_route(r'root', r'/')
    config.add_route(r'login', r'/login')
    config.add_route(r'user', r'/user')
    config.add_route(r'user/keys', r'/user/keys')
    config.add_route(r'user/addkey', r'/user/addkey')
    config.add_route(r'user/rmkey', r'user/rmkey/{keyid:[0-9]+}',)
    config.add_route(r'user/partners', r'/user/partners')
    config.add_route(r'user/add-partner', r'user/add-partner')
    config.add_route(r'user/rm-partner', r'user/rm-partner/{repo_id:[0-9]+}')

    config.add_static_view(name='static', path=os.path.join(ROOT, 'static', ''))

    config.scan()

def main(global_config, **settings):
    log.info(settings)
    log.info(global_config)
    engine = engine_from_config(settings, 'sqlalchemy.')
    Base.metadata.bind = engine
    config = Configurator(settings=settings)
    config.include('pyramid_jinja2')
    config.add_jinja2_renderer('.html')
    routes(config)
    app = config.make_wsgi_app()
    app = cookie_session(app)
    app = db_session_adder(app, engine)
    app = config_ware(app, config)
    return app

