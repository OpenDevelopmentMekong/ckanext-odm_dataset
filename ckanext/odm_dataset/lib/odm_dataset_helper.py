#!/usr/bin/env python
# -*- coding: utf-8 -*-

DEBUG = True

import pylons
import json
import ckan
import logging
import urlparse
import genshi

log = logging.getLogger(__name__)

def create_default_issue_dataset(pkg_info):
  ''' Uses CKAN API to add a default Issue as part of the vetting workflow for datasets'''
  try:

    extra_vars = {
        't0': ckan.plugins.toolkit._("Thank you for uploading the dataset. You should have received a confirmation email from OD Mekong Datahub. This dataset is still unpublished. Your item can only be published after you review this form and after our administrators approve your entry."),
        't1': ckan.plugins.toolkit._("It is important that you have entered the correct information in your dataset form. We also ask that all contributors complete as many fields as possible."),
        't2': ckan.plugins.toolkit._("Please take this opportunity to review your dataset record. If you would like to make any changes please select your dataset record and then click on the Manage button on the top right corner."),
        't3': ckan.plugins.toolkit._("Please CHECK YOUR SPELLING against the original item to ensure the item is recorded correctly."),
        't4': ckan.plugins.toolkit._("Please review your dataset record form again for the mandatory fields:"),
        't5': ckan.plugins.toolkit._("Title (Please use Associated Press style title where the first letter is capitalized and the rest of the title is not, i.e. 'Study of Cambodian forests and lakes from 1992 to 1994')"),
        't6': ckan.plugins.toolkit._("Language"),
        't7': ckan.plugins.toolkit._("Version"),
        't8': ckan.plugins.toolkit._("Geographical area"),
        't9': ckan.plugins.toolkit._("Source"),
        't10': ckan.plugins.toolkit._("Processes"),
        't11': ckan.plugins.toolkit._("Date uploaded"),
        't12': ckan.plugins.toolkit._("Date created"),
        't13': ckan.plugins.toolkit._("Please review again the following information, vital to other users who may search for your record:"),
        't14': ckan.plugins.toolkit._("Description(Make sure this is a concise description of the record in your own words, please do not just 'copy' and 'paste' an abstract by the original author)"),
        't15': ckan.plugins.toolkit._("Topics"),
        't16': ckan.plugins.toolkit._("License (Make sure you indicated the correct license. Additional information on creative commons is found here http://opendefinition.org/licenses/. If there is no license, please indicate 'license unspecified')"),
        't17': ckan.plugins.toolkit._("Copyright"),
        't18': ckan.plugins.toolkit._("Access and Use Constraints"),
        't19': ckan.plugins.toolkit._("Contact"),
        't20': ckan.plugins.toolkit._("Date modified"),
        't21': ckan.plugins.toolkit._("Temporal Range"),
        't22': ckan.plugins.toolkit._("Accuracy"),
        't23': ckan.plugins.toolkit._("Logical Consistency"),
        't24': ckan.plugins.toolkit._("Completeness"),
        't25': ckan.plugins.toolkit._("Metadata Reference Information"),
        't26': ckan.plugins.toolkit._("Attributes"),
        't27': ckan.plugins.toolkit._("Our administrators need to review the dataset record as well. They will close fixed issues or open new issues if there are any other inconsistencies. Once all issues have been resolved, the item will be published."),
        't28': ckan.plugins.toolkit._("Thank you for sharing,"),
        't29': ckan.plugins.toolkit._("Open Development Team")
    }

    issue_message = ckan.lib.base.render('messages/default_issue_dataset.txt',extra_vars=extra_vars,loader_class=genshi.template.text.NewTextTemplate)

    params = {'title':'User Dataset Upload Checklist','description':issue_message,'dataset_id':pkg_info['id']}
    ckan.plugins.toolkit.get_action('issue_create')(data_dict=params)

  except KeyError:

    log.error("Action 'issue_create' not found. Please make sure that ckanext-issues plugin is installed.")

def last_dataset():
  ''' Returns the last dataset info stored in session'''
  if 'last_dataset' in session:
    return session['last_dataset']

  return None

def convert_to_multilingual(value):
  '''Converts strings to multilingual with the current language set'''

  multilingual_value = {}

  try:
    json_value = json.loads(value);
    multilingual_value = json_value
  except ValueError:
    multilingual_value[get_current_language()] = value;

  return multilingual_value

def map_odm_spatial_range(value):

  if type(value) is list:
    return value

  odm_spatial_range = []

  if value.lower().find('laos') > -1:
    odm_spatial_range.append('la')
  if value.lower().find('vietnam') > -1:
    odm_spatial_range.append('vn')
  if value.lower().find('thailand') > -1:
    odm_spatial_range.append('th')
  if value.lower().find('myanmar') > -1:
    odm_spatial_range.append('mm')
  if value.lower().find('cambodia') > -1:
    odm_spatial_range.append('kh')
  if value.lower().find('global') > -1:
    odm_spatial_range.append('global')
  if value.lower().find('asean') > -1:
    odm_spatial_range.append('asean')
  if value.lower().find('greater mekong subregion (gms)') > -1:
    odm_spatial_range.append('gms')
  if value.lower().find('lower mekong basin') > -1:
    odm_spatial_range.append('lmb')
  if value.lower().find('lower mekong countries') > -1:
    odm_spatial_range.append('lmc')

  return odm_spatial_range

def map_odm_language(value):

  if type(value) is list:
    return value

  odm_language = []

  if value.lower().find('km') > -1 or value.lower().find('khmer') > -1:
    odm_language.append('km')
  if value.lower().find('vi') > -1 or value.lower().find('vietnamese') > -1:
    odm_language.append('vi')
  if value.lower().find('en') > -1 or value.lower().find('english') > -1:
    odm_language.append('en')
  if value.lower().find('lo') > -1 or value.lower().find('lao') > -1:
    odm_language.append('lo')
  if value.lower().find('th') > -1 or value.lower().find('thai') > -1:
    odm_language.append('th')
  if value.lower().find('my') > -1 or value.lower().find('burmese') > -1:
    odm_language.append('my')
  if value.lower().find('zh') > -1 or value.lower().find('chinese') > -1:
    odm_language.append('zh')
  if value.lower().find('fr') > -1 or value.lower().find('french') > -1:
    odm_language.append('fr')
  if value.lower().find('de') > -1 or value.lower().find('german') > -1:
    odm_language.append('de')
  if value.lower().find('jp') > -1 or value.lower().find('japanese') > -1:
    odm_language.append('jp')
  if value.lower().find('ko') > -1 or value.lower().find('korean') > -1:
    odm_language.append('ko')
  if value.lower().find('other') > -1:
    odm_language.append('other')

  return odm_language

def clean_taxonomy_tags(value):
  '''Cleans taxonomy field before storing it'''

  if isinstance(value, basestring):
    return json.dumps([value])

  return json.dumps(list(value))

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

def get_current_language():
  '''Returns the current language code'''

  if DEBUG:
    log.debug('get_current_language')

  return pylons.request.environ['CKAN_LANG']

def get_value_for_current_language(value):
  '''Returns the corresponding value on the current language or the string if non-multilingual'''

  if DEBUG:
    log.debug('get_value_for_current_language')

  try:
    value = json.loads(value);

    if isinstance(value, basestring):
      return value

    return value[get_current_language()] or ""
  except:

    return ""

session = {}
