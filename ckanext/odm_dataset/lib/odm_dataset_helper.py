#!/usr/bin/env python
# -*- coding: utf-8 -*-

DEBUG = True

import pylons
import json
import ckan
import logging
import urlparse

log = logging.getLogger(__name__)

def create_default_issue_dataset(pkg_info):
  ''' Uses CKAN API to add a default Issue as part of the vetting workflow for datasets'''
  try:

    extra_vars = {
      't0': ckan.plugins.toolkit._("Thank you for uploading this item. Instructions about vetting system available on https://wiki.opendevelopmentmekong.net/partners:content_review#instructions_for_default_issue_on_datasets")
    }

    issue_message = render('messages/default_issue_dataset.txt',extra_vars=extra_vars,loader_class=NewTextTemplate)

    params = {'title':'User Dataset Upload Checklist','description':issue_message,'dataset_id':pkg_info['id']}
    ckan.plugins.toolkit.get_action('issue_create')(data_dict=params)

  except KeyError:

    log.error("Action 'issue_create' not found. Please make sure that ckanext-issues plugin is installed.")

def last_dataset():
  ''' Returns the last dataset info stored in session'''
  if 'last_dataset' in session:
    return session['last_dataset']

  return None

def clean_taxonomy_tags(value):
  '''Cleans taxonomy field before storing it'''

  if isinstance(value, basestring):
    return json.dumps([value])

  tags = list(value)
  return json.dumps([tag for tag in tags])

def get_localized_tag(tag):
  '''Looks for a term translation for the specified tag. Returns the tag untranslated if no term found'''

  if DEBUG:
    log.debug('odm_dataset_get_localized_tag: %s', tag)

  desired_lang_code = pylons.request.environ['CKAN_LANG']

  translations = ckan.logic.action.get.term_translation_show(
          {'model': ckan.model},
          {'terms': (tag)})

  # Transform the translations into a more convenient structure.
  for translation in translations:
    if translation['lang_code'] == desired_lang_code:
      return translation['term_translation']

  return str(tag)

def get_current_language():
  '''Returns the current language code'''

  if DEBUG:
    log.debug('get_current_language')

  return pylons.request.environ['CKAN_LANG']

def get_value_for_current_language(value):
  '''Returns the corresponding value on the current language'''

  if DEBUG:
    log.debug('get_value_for_current_language')

  try:
    value = json.loads(value);

    if isinstance(value, basestring):
      return value

    return value[get_current_language()] or ""
  except:

    return ""

def get_localized_tags_string(tags_string):
  '''Returns a comma separated string with the translation of the tags specified. Calls get_localized_tag'''

  if DEBUG:
    log.debug('get_localized_tags_string: %s', tags_string)

  translated_array = []
  for tag in tags_string.split(', '):
    translated_array.append(get_localized_tag(tag))

  if len(translated_array)==0:
    return ''

  return ','.join(translated_array)

def convert_to_multilingual(value):
  '''Converts strings to multilingual with the current language set'''

  multilingual_value = {}

  try:
    json_value = json.loads(value);
    multilingual_value = json_value
  except ValueError:
    multilingual_value[get_current_language()] = value;

  return multilingual_value

session = {}
