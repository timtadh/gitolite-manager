#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
gitolite-manager
Author: Tim Henderson
Contact: tim.tadh@gmail.com, tadh@case.edu
Copyright: 2013 All Rights Reserved, see LICENSE
'''


import sys, os
import json
import logging
log = logging.getLogger('gm:tests:validate')

from nose.tools import ok_ as ok, eq_ as eq, nottest, raises, assert_raises

from gitolite_manager.validate import validate_json
from gitolite_manager import validate


def test_one_item_valid():
    schema = {
        "name" : validate.value_checker("value")
    }
    ok, errors = validate_json(schema, {"name":"value"})
    assert ok
    assert len(errors) == 0

def test_non_strict():
    schema = {
        "name" : validate.value_checker("value")
    }
    ok, errors = validate_json(schema, {"name":"value", "color":"blue"})
    assert not ok
    ok, errors = validate_json(schema, {"name":"value", "color":"blue"}, False)
    assert ok
    assert len(errors) == 0

def test_optional():
    schema = {
        'name' : validate.optional(validate.value_checker('value'))
    }
    ok, errors = validate_json(schema, {'name':'value'})
    assert ok and len(errors) == 0
    ok, errors = validate_json(schema, {})
    assert ok and len(errors) == 0
    schema = {
        'name' : validate.value_checker('value')
    }
    ok, errors = validate_json(schema, {'name':'value'})
    assert ok and len(errors) == 0
    ok, errors = validate_json(schema, {})
    assert not ok
    schema = {
        'name' : validate.optional({
            'name2':validate.value_checker('value')
        })
    }
    ok, errors = validate_json(schema, {'name':{'name2':'value'}})
    assert ok and len(errors) == 0
    ok, errors = validate_json(schema, {})
    assert ok and len(errors) == 0
    ok, errors = validate_json(schema, {'name':{}})
    assert not ok
    schema = {
        'name' : validate.optional([
            validate.value_checker('value')
        ])
    }
    ok, errors = validate_json(schema, {'name':['value']})
    assert ok and len(errors) == 0
    ok, errors = validate_json(schema, {})
    assert ok and len(errors) == 0
    ok, errors = validate_json(schema, {'name':['vigour']})
    assert not ok

def test_optional_bad_use_or():
    schema = {
        'name' : validate.optional(validate.null_checker() | validate.value_checker('value'))
    }
    ok, errors = validate_json(schema, {'name':'value'})
    assert ok and len(errors) == 0
    ok, errors = validate_json(schema, {'name':None})
    assert ok and len(errors) == 0
    ok, errors = validate_json(schema, {})
    assert ok and len(errors) == 0
    with assert_raises(SyntaxError):
        schema = {
            'name' : validate.null_checker() | validate.optional(validate.value_checker('value'))
        }
    ok, errors = validate_json(schema, {'name':'value'})




def test_optional_bad_use_and():
    schema = {
        'name' : validate.optional(validate.length_checker(5) & validate.value_checker('value'))
    }
    ok, errors = validate_json(schema, {'name':'value'})
    assert ok and len(errors) == 0
    ok, errors = validate_json(schema, {'name':None})
    assert not ok
    ok, errors = validate_json(schema, {})
    assert ok and len(errors) == 0
    with assert_raises(SyntaxError):
        schema = {
            'name' : validate.length_checker(5) & validate.optional(validate.value_checker('value'))
        }
    ok, errors = validate_json(schema, {'name':'value'})

def test_optional_unsupported_item():
    with assert_raises(RuntimeError):
        validate.optional(True)

def test_set_one_item_valid():
    schema = {
        "name" : validate.set_checker(set(['x', 'y', 'z']))
    }
    ok, errors = validate_json(schema, {"name":"x"})
    assert ok
    assert len(errors) == 0
    ok, errors = validate_json(schema, {"name":"y"})
    assert ok
    assert len(errors) == 0
    ok, errors = validate_json(schema, {"name":"z"})
    assert ok
    assert len(errors) == 0

def test_one_item_invalid():
    schema = {
        "name" : 
          lambda b: (
            (True, list()) 
              if (b == 'value') 
              else (False, ["'%s' is not equal to 'value'" % b]))
    }
    ok, errors = validate_json(schema, {"name":"vsdalue"})
    assert not ok
    assert len(errors) == 1
    assert errors[0] == "'vsdalue' is not equal to 'value'"

def test_set_one_item_invalid():
    schema = {
        "name" : validate.set_checker(set(['x', 'y', 'z']))
    }
    ok, errors = validate_json(schema, {"name":"xy"})
    assert not ok
    assert len(errors) == 1
    assert errors[0] == "'xy' is not in ['x', 'y', 'z']"

def test_null_checker():
    schema = {
        "name" : validate.null_checker()
    }
    ok, errors = validate_json(schema, {"name":None})
    assert ok
    assert len(errors) == 0
    ok, errors = validate_json(schema, {"name":'asdf'})
    assert not ok
    assert len(errors) == 1
    assert errors[0] == "'asdf' is not equal to None"

def test_one_item_no_validator():
    schema = {
        "name" : "value"
    }
    ok, errors = validate_json(schema, {"name":"vsdalue"})
    assert not ok
    assert len(errors) == 1
    assert errors[0] == 'Expected schema item to be a callable got value'

def test_one_item_validator_returns_one_item():
    schema = {
        "name" : 
          lambda b: (True if (b == 'value') else False)
    }
    ok, errors = validate_json(schema, {"name":"vsdalue"})
    assert not ok
    assert len(errors) == 1
    assert errors[0] == 'Expected item validator to return a tuple got False'

def test_one_item_validator_returns_three_items():
    schema = {
        "name" : 
          lambda b: ((True, None, None) if (b == 'value') else (False, "asdf",
          "adfs"))
    }
    ok, errors = validate_json(schema, {"name":"vsdalue"})
    assert not ok
    assert len(errors) == 1
    assert errors[0] == "Expected item validator to return 2 items got (False, 'asdf', 'adfs')"

def test_list_one_item_valid():
    schema = [
      {
        "name" : validate.value_checker("value")
      }
    ]
    ok, errors = validate_json(schema, [{"name":"value"}])
    assert ok
    assert len(errors) == 0

def test_list_three_items_valid():
    schema = [
      {
        "name" : validate.value_checker("value")
      }
    ]
    ok, errors = validate_json(schema, [{"name":"value"}, {"name":"value"},
      {"name":"value"}])
    assert ok
    assert len(errors) == 0

def test_list_three_items_invalid():
    schema = [
      {
        "name" : validate.value_checker("value")
      }
    ]
    ok, errors = validate_json(schema, [{"name":"vaque"}, {"name":"valqe"},
      {"name":"vqlue"}])
    assert not ok
    assert len(errors) == 3
    assert errors == ["'vaque' is not equal to 'value'", 
                      "'valqe' is not equal to 'value'", 
                      "'vqlue' is not equal to 'value'"]

def test_list_three_bare_items_valid():
    schema = [
        validate.value_checker("value")
    ]
    ok, errors = validate_json(schema, ["value", "value", "value"])
    assert ok
    assert len(errors) == 0

def test_list_bare_multiple_checkers_invalid():
    schema = [
        validate.value_checker("value"),
        validate.value_checker("seahorse"),
    ]
    ok, errors = validate_json(schema, ["value", "seahorse"])
    assert not ok

def test_list_incompatible_type():
    schema = [
        validate.value_checker("value")
    ]
    ok, errors = validate_json(schema, {"value": "seahorse"})
    assert not ok

def test_dict_incompatible_type():
    schema = {
        "value": validate.value_checker("seahorse")
    }
    ok, errors = validate_json(schema, ["value", "seahorse"])
    assert not ok

def test_dict_dunder_undefinedkeys():
    schema = {
        "__undefinedkeys__": validate.value_checker("value")
    }
    ok, errors = validate_json(schema, {"a":  "value", "b": "value"})
    assert ok
    assert len(errors) == 0

def test_length_checker():
    schema = [
          validate.length_checker(5)
    ]
    ok, errors = validate_json(schema, ["value", "value", "value"])
    assert ok
    assert len(errors) == 0

def test_type_checker():
    schema = [
          validate.type_checker(basestring)
    ]
    ok, errors = validate_json(schema, ["value", "value", "value"])
    assert ok
    assert len(errors) == 0

def test_max_length_checker():
    schema = [
          validate.max_length_checker(5)
    ]
    ok, errors = validate_json(schema, ["value", "value", "value"])
    assert ok
    assert len(errors) == 0

def test_max_length_checker_incompatible_type():
    schema = {
          "name": validate.max_length_checker(5)
    }
    ok, errors = validate_json(schema, {"name": True})
    assert not ok

def test_max_length_checker_under():
    schema = [
          validate.max_length_checker(5)
    ]
    ok, errors = validate_json(schema, ["valu"])
    assert ok
    assert len(errors) == 0

def test_max_length_checker_over():
    schema = [
          validate.max_length_checker(5)
    ]
    ok, errors = validate_json(schema, ["values"])
    assert not ok
    assert len(errors) == 1
    assert errors == ["Sequence, 'values', greater than 5 items long"]

def test_min_length_checker():
    schema = [
          validate.min_length_checker(5)
    ]
    ok, errors = validate_json(schema, ["value", "value", "value"])
    assert ok
    assert len(errors) == 0

def test_min_length_checker_incompatible_type():
    schema = {
          "name": validate.min_length_checker(5)
    }
    ok, errors = validate_json(schema, {"name": True})
    assert not ok

def test_min_length_checker_under():
    schema = [
          validate.min_length_checker(5)
    ]
    ok, errors = validate_json(schema, ["valu"])
    assert not ok
    assert len(errors) == 1
    assert errors == ["Sequence, 'valu', less than 5 items long"]

def test_min_length_checker_over():
    schema = [
          validate.min_length_checker(5)
    ]
    ok, errors = validate_json(schema, ["values"])
    assert ok
    assert len(errors) == 0

def test_length_checker_incompatible_type():
    schema = {
          "name": validate.length_checker(5)
    }
    ok, errors = validate_json(schema, {"name": True})
    assert not ok

def test_type_or_type_checker():
    schema = [
          validate.type_checker(int) | validate.type_checker(float)
    ]
    ok, errors = validate_json(schema, ["value", "value", "value"])
    assert not ok
    assert len(errors) == 6

def test_combine_checkers_or_bad_use():
    with assert_raises(TypeError):
        validate.type_checker(int) | True

def test_combine_checkers_and_bad_use():
    with assert_raises(TypeError):
        validate.type_checker(int) & True

def test_type_and_type_checker():
    schema = [
          validate.type_checker(int) & validate.type_checker(float)
    ]
    ok, errors = validate_json(schema, ["value", "value", "value"])
    assert not ok
    assert len(errors) == 6
    assert errors == [
        "Object, ''value'', not of type <type 'int'>", 
        "Object, ''value'', not of type <type 'float'>", 
        "Object, ''value'', not of type <type 'int'>", 
        "Object, ''value'', not of type <type 'float'>", 
        "Object, ''value'', not of type <type 'int'>", 
        "Object, ''value'', not of type <type 'float'>"]

def test_type_and_length_checker():
    schema = [
          validate.type_checker(basestring) & validate.length_checker(4)
    ]
    ok, errors = validate_json(schema, ["value"])
    assert not ok
    assert len(errors) == 1
    assert errors == ["Sequence, 'value', is not 4 items long"]

def test_type_or_length_checker():
    schema = [
          validate.type_checker(basestring) | validate.length_checker(4)
    ]
    ok, errors = validate_json(schema, ["value"])
    assert ok
    assert len(errors) == 0

def test_type_and_length_checker_both_true():
    schema = [
          validate.type_checker(basestring) & validate.length_checker(5)
    ]
    ok, errors = validate_json(schema, ["value"])
    assert ok
    assert len(errors) == 0

