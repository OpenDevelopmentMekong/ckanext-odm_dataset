#!/usr/bin/env python
# -*- coding: utf-8 -*-

DEBUG = True

import pylons
import json
import ckan
import logging
import urlparse
import ckan.plugins.toolkit as toolkit
from genshi.template.text import NewTextTemplate
from ckan.lib.base import render

log = logging.getLogger(__name__)

def create_default_issue_dataset(pkg_info):
  ''' Uses CKAN API to add a default Issue as part of the vetting workflow for datasets'''
  try:

    extra_vars = {
        't0': toolkit._("Thank you for uploading the dataset. You should have received a confirmation email from OD Mekong Datahub. This dataset is still unpublished. Your item can only be published after you review this form and after our administrators approve your entry."),
        't1': toolkit._("It is important that you have entered the correct information in your dataset form. We also ask that all contributors complete as many fields as possible."),
        't2': toolkit._("Please take this opportunity to review your dataset record. If you would like to make any changes please select your dataset record and then click on the Manage button on the top right corner."),
        't3': toolkit._("Please CHECK YOUR SPELLING against the original item to ensure the item is recorded correctly."),
        't4': toolkit._("Please review your dataset record form again for the mandatory fields:"),
        't5': toolkit._("Title (Please use Associated Press style title where the first letter is capitalized and the rest of the title is not, i.e. 'Study of Cambodian forests and lakes from 1992 to 1994')"),
        't6': toolkit._("Language"),
        't7': toolkit._("Version"),
        't8': toolkit._("Geographical area"),
        't9': toolkit._("Source"),
        't10': toolkit._("Processes"),
        't11': toolkit._("Date uploaded"),
        't12': toolkit._("Date created"),
        't13': toolkit._("Please review again the following information, vital to other users who may search for your record:"),
        't14': toolkit._("Description(Make sure this is a concise description of the record in your own words, please do not just 'copy' and 'paste' an abstract by the original author)"),
        't15': toolkit._("Topics"),
        't16': toolkit._("License (Make sure you indicated the correct license. Additional information on creative commons is found here http://opendefinition.org/licenses/. If there is no license, please indicate 'license unspecified')"),
        't17': toolkit._("Copyright"),
        't18': toolkit._("Access and Use Constraints"),
        't19': toolkit._("Contact"),
        't20': toolkit._("Date modified"),
        't21': toolkit._("Temporal Range"),
        't22': toolkit._("Accuracy"),
        't23': toolkit._("Logical Consistency"),
        't24': toolkit._("Completeness"),
        't25': toolkit._("Metadata Reference Information"),
        't26': toolkit._("Attributes"),
        't27': toolkit._("Our administrators need to review the dataset record as well. They will close fixed issues or open new issues if there are any other inconsistencies. Once all issues have been resolved, the item will be published."),
        't28': toolkit._("Thank you for sharing,"),
        't29': toolkit._("Open Development Team")
    }

    issue_message = render('messages/default_issue_dataset.txt',extra_vars=extra_vars,loader_class=NewTextTemplate)

    params = {'title':'User Dataset Upload Checklist','description':issue_message,'dataset_id':pkg_info['id']}
    toolkit.get_action('issue_create')(data_dict=params)

  except KeyError:

    log.error("Action 'issue_create' not found. Please make sure that ckanext-issues plugin is installed.")

def last_dataset():
  ''' Returns the last dataset info stored in session'''
  if 'last_dataset' in session:
    return session['last_dataset']

  return None

def localize_resource_url(url):
  '''Converts a absolute URL in a relative, chopping out the domain'''

  try:
    parsed = urlparse(url)
    str_index = url.index(parsed.netloc)
    str_length = len(parsed.netloc)
    localized = url[str_index+str_length:]
    return localized

  except:
    return url

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

    if isinstance(value, basestring):
      return value

  return value[get_current_language()] or ""

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

session = {}
