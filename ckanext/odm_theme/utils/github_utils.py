# -*- coding: utf-8 -*-
''' Module containing classes and methods for interaction with ODM's github repo

'''
import ckan.plugins as p
import ckan.new_tests.helpers as helpers
import urllib2
import urllib
import httplib
import json
import base64
import sys
import os
import traceback


# Interface definition
class IGithubApi:

  def get_taxonomy_for_locale(self,locale):
    raise NotImplementedError

  def get_library_records(self):
    raise NotImplementedError

  def get_cover_image_for_library_record(self,name):
    raise NotImplementedError

  def get_odc_ontology(self,name):
    raise NotImplementedError

# Mock implementation
class TestGithubApi (IGithubApi):

  def __init__(self):

    return

  def get_taxonomy_for_locale(self,locale):

    pathToFile = os.path.join(os.path.dirname(__file__), "test/taxonomy.json")
    with open(pathToFile, 'rb') as f:
      return json.loads(f.read())

  def get_library_records(self):

    pathToFile = os.path.join(os.path.dirname(__file__), "test/library.mrc")
    with open(pathToFile, 'rb') as f:
      return f.read()

  def get_cover_image_for_library_record(self,name):

    pathToFile = os.path.join(os.path.dirname(__file__), "test/cover.jpg")
    with open(pathToFile, 'r') as f:
      return f.read()

  def get_odc_ontology(self,name):

    pathToFile = os.path.join(os.path.dirname(__file__), "test/export.xml")
    with open(pathToFile, 'r') as f:
      return f.read()


# Real implementation
class RealGithubApi (IGithubApi):

  def __init__(self):

    return

  def get_taxonomy_for_locale(self,locale):

    if locale is 'en':

      request = urllib2.Request('https://raw.githubusercontent.com/OpenDevelopmentMekong/odm-localization/master/taxonomy/taxonomy_en.json')

    elif locale is 'km':

      request = urllib2.Request('https://raw.githubusercontent.com/OpenDevelopmentMekong/odm-localization/master/taxonomy/taxonomy_km.json')

    elif locale is 'lo':

      request = urllib2.Request('https://raw.githubusercontent.com/OpenDevelopmentMekong/odm-localization/master/taxonomy/taxonomy_lo.json')

    elif locale is 'vi':

      request = urllib2.Request('https://raw.githubusercontent.com/OpenDevelopmentMekong/odm-localization/master/taxonomy/taxonomy_vi.json')

    elif locale is 'my':

      request = urllib2.Request('https://raw.githubusercontent.com/OpenDevelopmentMekong/odm-localization/master/taxonomy/taxonomy_my.json')

    elif locale is 'th':

      request = urllib2.Request('https://raw.githubusercontent.com/OpenDevelopmentMekong/odm-localization/master/taxonomy/taxonomy_th.json')

    response = urllib2.urlopen(request)
    return json.loads(response.read())

  def get_library_records(self):

    try:
      request = urllib2.Request('https://raw.githubusercontent.com/OpenDevelopmentMekong/odm-library/master/records.mrc')
      response = urllib2.urlopen(request)
      return response.read()
    except (urllib2.HTTPError, urllib2.URLError, httplib.BadStatusLine) as e:
      traceback.print_exc()
      return None

  def get_cover_image_for_library_record(self,name):

    try:
      request = urllib2.Request('https://raw.githubusercontent.com/OpenDevelopmentMekong/odm-library/master/covers/'+name+'.jpg')
      response = urllib2.urlopen(request)
      return response.read()
    except (urllib2.HTTPError, urllib2.URLError, httplib.BadStatusLine) as e:
      traceback.print_exc()
      return None

  def get_odc_ontology(self,name):

    try:
      request = urllib2.Request('https://raw.githubusercontent.com/OpenDevelopmentMekong/odm-migration/master/'+name+'.xml')
      response = urllib2.urlopen(request)
      return response.read()
    except (urllib2.HTTPError, urllib2.URLError, httplib.BadStatusLine) as e:
      traceback.print_exc()
      return None
