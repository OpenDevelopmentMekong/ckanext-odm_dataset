#!/usr/bin/env python
# -*- coding: utf-8 -*-

DEBUG = True

import pylons
import json
import ckan
import logging
import urlparse
import ckan.plugins.toolkit as toolkit

log = logging.getLogger(__name__)

def create_default_issue_library_record(pkg_info):
  ''' Uses CKAN API to add a default Issue as part of the vetting workflow for library records'''
  try:

    extra_vars = {
        't0': toolkit._("Thank you for uploading the library item. You should have received a confirmation email from OD Mekong Datahub. This library item is still unpublished. Your item can only be published after you review this form and after our administrators approve your entry."),
        't1': toolkit._("It is important that you have entered the correct information in your library record form. We also ask that all contributors complete as many fields as possible."),
        't2': toolkit._("Please take this opportunity to review your library record. If you would like to make any changes please select your library record and then click on the Manage button on the top right corner."),
        't3': toolkit._("Please CHECK YOUR SPELLING against the original item to ensure the item is recorded correctly."),
        't4': toolkit._("Please review your library record form again for the mandatory fields:"),
        't5': toolkit._("Title (Please use Associated Press style title where the first letter is capitalized and the rest of the title is not, i.e. 'Study of Cambodian forests and lakes from 1992 to 1994')"),
        't6': toolkit._("Language"),
        't7': toolkit._("Edition / Version"),
        't8': toolkit._("Geographical area"),
        't9': toolkit._("Date uploaded"),
        't10': toolkit._("Please review again the following information, vital to other users who may search for your record:"),
        't11': toolkit._("Summary (Make sure this is a concise description of the record in your own words, please do not just 'copy' and 'paste' an abstract by the original author)"),
        't12': toolkit._("Topics"),
        't13': toolkit._("License (Make sure you indicated the correct license. Additional information on creative commons is found here http://opendefinition.org/licenses/. If there is no license, please indicate 'license unspecified')"),
        't14': toolkit._("Copyright"),
        't15': toolkit._("Access and Use Constraints"),
        't16': toolkit._("Author"),
        't17': toolkit._("Co-author"),
        't18': toolkit._("Corporate Author"),
        't19': toolkit._("Publisher"),
        't20': toolkit._("Lastly, please check again for the following information on the library record you entered. If the information is available, please include it in the appropriate field. This will greatly improve the searchability of your library record item or provide information that a user will find useful:"),
        't21': toolkit._("ISSN or ISBN numbers"),
        't22': toolkit._("Publication Place"),
        't23': toolkit._("Publication Date"),
        't24': toolkit._("Pagination"),
        't25': toolkit._("Our administrators need to review the library record as well. They will close fixed issues or open new issues if there are any other inconsistencies. Once all issues have been closed, the item will be published."),
        't26': toolkit._("Thank you for sharing,"),
        't27': toolkit._("Open Development Team")
    }

    issue_message = render('messages/default_issue_library_record.txt',extra_vars=extra_vars,loader_class=NewTextTemplate)

    params = {'title':'User Library record Upload Checklist','description':issue_message,'dataset_id':pkg_info['id']}
    toolkit.get_action('issue_create')(data_dict=params)

  except KeyError:

    log.error("Action 'issue_create' not found. Please make sure that ckanext-issues plugin is installed.")

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

def get_taxonomy_dictionary():
  '''Returns the tag dictionary for the taxonomy'''

  try:
    tag_dictionaries = toolkit.get_action('tag_list')(data_dict={'vocabulary_id': 'taxonomy'})
    return tag_dictionaries
  except toolkit.ObjectNotFound:
    return []

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

def tag_for_topic(topic):
  '''Return the name of the tag corresponding to a top topic'''

  if DEBUG:
    log.debug('tag_for_topic')

  tag_name = ''.join(ch for ch in topic if (ch.isalnum() or ch == '_' or ch == '-' or ch == ' ' ))
  return tag_name if len(tag_name)<=100 else tag_name[0:99]

def top_topics():
  '''Return a list of top_topics'''

  return list([
    ('Agriculture and fishing'),
    ('Aid and development'),
    ('Disasters and emergency response'),
    ('Economy and commerce'),
    ('Energy'),
    ('Environment and natural resources'),
    ('Extractive industries'),
    ('Government'),
    ('Industries'),
    ('Infrastructure'),
    ('Labor'),
    ('Land'),
    ('Law and judiciary'),
    ('Population and censuses'),
    ('Social development'),
    ('Urban administration and development'),
    ('Science and technology')
  ])

def popular_groups():
  '''Return a sorted list of the groups with the most datasets.'''

  groups = toolkit.get_action('group_list')(data_dict={'sort': 'packages desc', 'all_fields': True})
  groups = groups[:10]
  return groups

def recent_datasets():
  '''Return a sorted list of the datasets updated recently.'''

  dataset = toolkit.get_action('current_package_list_with_resources')(data_dict={'limit': 10})
  return dataset

def popular_datasets(limit):
  '''Return a sorted list of the most popular datasets.'''

  result_dict = toolkit.get_action('package_search')(data_dict={'sort': 'views_recent desc', 'rows': limit})
  return result_dict['results']

session = {}