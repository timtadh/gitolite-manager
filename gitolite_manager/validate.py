#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
gitolite-manager
Author: Tim Henderson
Contact: tim.tadh@gmail.com, tadh@case.edu
Copyright: 2013 All Rights Reserved, see LICENSE
'''


import json, functools, copy, logging
log = logging.getLogger('validate:rules')


class Checker(object):

    def __init__(self, checker):
        self.checker = checker
        self.optional = False
        self.locked = False

    def __call__(self, data):
        return self.checker(data)

    def __and__(a, b):
        if not isinstance(b, Checker): return NotImplemented
        if a.locked or b.locked:
            raise SyntaxError, "Checker is locked"
        def a_and_b(data):
            a_ok, a_err = a(data)
            b_ok, b_err = b(data)
            if a_err is None: a_err = list()
            if b_err is None: b_err = list()
            assert isinstance(a_ok, bool)
            assert isinstance(b_ok, bool)
            return (a_ok and b_ok), (a_err + b_err)
        return Checker(a_and_b)

    def __or__(a, b):
        if not isinstance(b, Checker): return NotImplemented
        if a.locked or b.locked:
            raise SyntaxError, "Checker is locked"
        def a_or_b(data):
            a_ok, a_err = a(data)
            b_ok, b_err = b(data)
            if a_err is None: a_err = list()
            if b_err is None: b_err = list()
            if a_ok: return True, list()
            if b_ok: return True, list()
            return False, (a_err + b_err)
        return Checker(a_or_b)


def _getattribute(self, name):
    I = object.__getattribute__(self, 'I')
    if name in I: return I[name]
    return object.__getattribute__(self, name)
def _make_dict(d, I):
    X = {attr:getattr(d, attr) for attr in dir(d)}
    X.update({ 'I':I, '__getattribute__':_getattribute, })
    return X
opt_dict = type('opt_dict', (dict,), _make_dict(dict, {'optional':True}))
opt_list = type('opt_list', (list,), _make_dict(list, {'optional':True}))


def optional(c):
    '''
    The optional directive must be the outer most thing. Checker go on the
    inside of the call like:

        optional(null_checker | set_checker(['a', 'b' ,'c']))

    the following will not work:

        null_checker | optional(set_checker(['a', 'b', 'c']))
    '''
    if isinstance(c, Checker):
        c.optional = True
        c.locked = True
        return c
    elif isinstance(c, dict):
        return opt_dict(c)
    elif isinstance(c, list):
        return opt_list(c)
    else:
        raise RuntimeError, "Expected a checker"


def checker(f):
    def decorator(*args, **kwargs):
        def wrapper(data):
            return f(data, *args, **kwargs)
        return Checker(wrapper)
    return decorator


@checker
def null_checker(data):
    if data is not None:
        return False, [
            "'%s' is not equal to None" % (str(data),)]
    return True, list()


@checker
def value_checker(data, value):
    if data != value:
        return False, [
            "'%s' is not equal to '%s'" % (str(data), str(value))]
    return True, list()


@checker
def set_checker(data, objs):
    if data not in objs:
        return False, [
            "'%s' is not in %s" % (str(data), str(sorted(list(objs))))]
    return True, list()


@checker
def type_checker(data, type):
    if not isinstance(data, type):
        return False, [
            "Object, '%s', not of type %s" % (repr(data), str(type))]
    return True, list()


@checker
def length_checker(data, length):
    if not hasattr(data, '__len__'):
        return False, ["Object, '%s', doesn't have a length" % (repr(data))]
    if len(data) != length:
        return False, [
            "Sequence, '%s', is not %d items long" % (str(data), int(length))]
    return True, list()


@checker
def max_length_checker(data, length):
    if not hasattr(data, '__len__'):
        return False, ["Object, '%s', doesn't have a length" % (repr(data))]
    if len(data) > length:
        return False, [
            "Sequence, '%s', greater than %d items long" % (str(data), int(length))]
    return True, list()


@checker
def min_length_checker(data, length):
    if not hasattr(data, '__len__'):
        return False, ["Object, '%s', doesn't have a length" % (repr(data))]
    if len(data) < length:
        return False, [
            "Sequence, '%s', less than %d items long" % (str(data), int(length))]
    return True, list()

@checker
def format_checker(data, regex):
    if not regex.match(data):
        return False, [
            "string, '%s', did not match %s" % (str(data), str(regex))]
    return True, list()


def column_checker(column):
    pytype = column.type.python_type
    if pytype == str: pytype = basestring
    elif pytype == unicode: pytype = basestring
    typc = type_checker(pytype)
    c_check = typc
    if pytype == basestring and column.type.length is not None:
        c_check = typc & max_length_checker(column.type.length)
    if column.nullable:
        return null_checker() | c_check
    return c_check


def validate_json(schema, json_data, strict=True):
    ''' Assert that d matches the schema
    @param d = the dictionary
    @param allow_none = allow Nones in d '''

    errors = list()

    def proc(v1, v2):
        '''process 2 values assert they are of the same type'''
        #print 'proc>', v1, v2
        if   isinstance(v1, dict):
            return procdict(v1, v2)
        elif isinstance(v1, list):
            return proclist(v1, v2)
        else:
            validator = v1
            if not hasattr(validator, '__call__'):
                errors.append(
                    "Expected schema item to be a callable got %s" % str(v1))
                return False
            ret = validator(v2)
            if not isinstance(ret, tuple):
                errors.append(
                    "Expected item validator to return a tuple got %s" %
                    str(ret))
                return False
            if len(ret) != 2:
                errors.append(
                    "Expected item validator to return 2 items got %s" %
                    str(ret))
                return False
            ok, err = ret
            #print ok, err
            if not ok:
                errors.extend(err)
                return False
            return True
    def proclist(t, d):
        '''process a list type'''
        if not isinstance(d, list):
            msg = ("Expected a <type 'list'> got %s" % type(d))
            errors.append(msg)
            return False
        if len(t) != 1:
            errors.append(
                "Expected schema item to contain one element got %s" % str(t))
            return False
        v1 = t[0]
        acc = True
        for v2 in d:
            #print v1, v2
            r = proc(v1, v2)
            acc = acc and r
        return acc
    def procdict(t, d):
        '''process a dictionary type'''
        if not isinstance(d, dict):
            msg = "Expected a <type 'dict'> got %s, '%s'"\
                                  % (type(d), str(d))
            errors.append(msg)
            return False
        tkeys = set(t.keys());
        dkeys = set(d.keys());
        acc = True
        if '__undefinedkeys__' in tkeys:
            v1 = t['__undefinedkeys__']
            for v2 in d.values():
                r = proc(v1, v2)
                acc = acc and r
        else:
            for k in tkeys:
                if hasattr(t[k], 'optional') and t[k].optional:
                    continue
                if k not in dkeys:
                    msg = (
                      'Expected name, "%s", in %s'
                    ) % (str(k), str(d))
                    errors.append(msg)
                    acc = False
            for k in dkeys:
                if k not in tkeys:
                    if strict:
                        msg = (
                          'Unexpected name, "%s". The name must be in %s'
                        ) % (str(k), str(tkeys))
                        errors.append(msg)
                        acc = False
                else:
                    v1 = t[k]
                    v2 = d[k]
                    r = proc(v1, v2)
                    acc = acc and r
        return acc
    ok = proc(schema, json_data)
    return ok, errors


def validate_dictionary(dictionary, schema, strict=True):
    ''' validates a dictionary from a schema

    usage pattern::

        errors, rdict = validate_dictionary(d, {
            ## your schema
        })
        if errors:
            pass # handle
        else:
            pass # rdict valid

    :param dictionary: the dict
    :param schema: a schema the decode json must match. Checked using
                   :py:func:`validate_json`.
    :return: errs, rdict
    :rtype: *errors* - an error or None
    :rtype: *rdict* - the validated dictionary or None
    '''
    ok, errs = validate_json(schema, dictionary, strict)
    if not ok:
        return errs, None
    return None, dictionary


def load_json(req, schema, strict=True):
    ''' loads json from the req body

    usage pattern::

        errors, body = load_json(req, schema)
        if errors is not None:
            raise HTTPBadRequest(errors)

    :param req: the request obj
    :param schema: a schema the decode json must match. Checked using
                   :py:func:`validate_json`.
    :return: err, body
    :rtype: *err* - an error or None
    :rtype: *body* - the json loaded body or None

    expects:
         ``req.body`` can be deserialized by ``json.loads``'''
    try:
        if hasattr(req, 'json'):
            body = req.json
        else:
            body = json.loads(req.body)
    except Exception, e:
        log.debug(req.body)
        log.debug('failed to load json')
        return ['json did not decode'] + list(e.args), None
    ok, errs = validate_json(schema, body, strict)
    if not ok:
        return errs, None
    return None, body

