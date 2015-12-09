'''plugin.py

'''
import ckan
import pylons
import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as h
from pylons import config
from beaker.middleware import SessionMiddleware
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import odm_theme_helper
import datetime
import time
from urlparse import urlparse
import json
import collections
from genshi.template.text import NewTextTemplate
from ckan.lib.base import render

log = logging.getLogger(__name__)

DEBUG = False

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
  if 'last_dataset' in odm_theme_helper.session:
    return odm_theme_helper.session['last_dataset']

  return None

def localize_resource_url(url):
  '''Converts a absolute URL in a relative, chopping out the domain'''

  parsed = urlparse(url)
  str_index = url.index(parsed.netloc)
  str_length = len(parsed.netloc)

  localized = url[str_index+str_length:]

  return localized

def get_tag_dictionaries(vocab_id):
  '''Returns the tag dictionary for the specified vocab_id'''

  try:

    tag_dictionaries = toolkit.get_action('tag_list')(data_dict={'vocabulary_id': vocab_id})
    return tag_dictionaries

  except toolkit.ObjectNotFound:

    return []

def get_taxonomy_dictionary():
  '''Returns the tag dictionary for the taxonomy'''

  return get_tag_dictionaries(odm_theme_helper.taxonomy_dictionary)

def clean_taxonomy_tags(value):
  '''Cleans taxonomy field before storing it'''

  tags = list(value);

  return map(lambda x: x.encode('ascii'), tags)

def jsonify_countries():
  '''Returns the tag dictionary for the countries'''

  if DEBUG:
    log.debug('jsonify_countries')

  items = []
  for country in countries():
    items.append({'id':country[0],'text':country[0]})

  return json.dumps(items)

def jsonify_languages():
  '''Returns the tag dictionary for the languages'''

  if DEBUG:
    log.debug('jsonify_languages')

  items = []
  for language in languages():
    items.append({'id':language[0],'text':language[1]})

  return json.dumps(items)

def get_localized_tag(tag):
  '''Looks for a term translation for the specified tag. Returns the tag untranslated if no term found'''

  if DEBUG:
    log.debug('odm_theme_get_localized_tag: %s', tag)

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

def tag_for_topic(topic):
  '''Return the name of the tag corresponding to a top topic'''

  if DEBUG:
    log.debug('tag_for_topic')

  tag_name = ''.join(ch for ch in topic if (ch.isalnum() or ch == '_' or ch == '-' or ch == ' ' ))
  return tag_name if len(tag_name)<=100 else tag_name[0:99]

def top_topics():
  '''Return a list of top_topics'''

  if DEBUG:
    log.debug('top_topics')

  return odm_theme_helper.top_topics

def countries():
  '''Return a list of countries'''

  if DEBUG:
    log.debug('countries')

  return odm_theme_helper.countries

def languages():
  '''Return a list of languages'''

  if DEBUG:
    log.debug('languages')

  return odm_theme_helper.languages

def odc_fields():
  '''Return a list of odc fields'''

  if DEBUG:
    log.debug('odc_fields')

  return odm_theme_helper.odc_fields

def ckan_fields():
  '''Return a list of ckan fields'''

  if DEBUG:
    log.debug('ckan_fields')

  return odm_theme_helper.ckan_fields

def metadata_fields():
  '''Return a list of metadata fields'''

  if DEBUG:
    log.debug('metadata_fields')

  return odm_theme_helper.metadata_fields

def metadata_fields_combined():
  '''Return a list of metadata fields, combined with metadata_fields_combined'''

  if DEBUG:
    log.debug('metadata_fields_combined')

  return list(set(odm_theme_helper.metadata_fields + odm_theme_helper.metadata_fields_compact))

def popular_groups():
  '''Return a sorted list of the groups with the most datasets.'''

  # Get a list of all the site's groups from CKAN, sorted by number of
  # datasets.
  groups = toolkit.get_action('group_list')(data_dict={'sort': 'packages desc', 'all_fields': True})

  # Truncate the list to the 10 most popular groups only.
  groups = groups[:10]

  return groups

def recent_datasets():
  '''Return a sorted list of the datasets updated recently.'''

  # Get a list of all the site's groups from CKAN, sorted by number of
  # datasets.
  dataset = toolkit.get_action('current_package_list_with_resources')(data_dict={'limit': 10})

  return dataset

def popular_datasets(limit):
  '''Return a sorted list of the most popular datasets.'''

  # Get a list of all the site's groups from CKAN, sorted by number of
  # datasets.
  result_dict = toolkit.get_action('package_search')(data_dict={'sort': 'views_recent desc', 'rows': limit})

  return result_dict['results']

def get_orga_or_group(orga_id,group_id):
  '''Returns orga or group'''

  if orga_id is not None:
    return orga_id
  elif group_id is not None:
    return group_id

  return None

class OdmThemePlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
  '''OD Mekong theme plugin.'''

  plugins.implements(plugins.IValidators, inherit=True)
  plugins.implements(plugins.IConfigurer)
  plugins.implements(plugins.ITemplateHelpers)
  plugins.implements(plugins.IRoutes, inherit=True)
  plugins.implements(plugins.IFacets)
  plugins.implements(plugins.IPackageController, inherit=True)

  def __init__(self, *args, **kwargs):

    log.debug('OdmThemePlugin init')
    wsgi_app = SessionMiddleware(None, None)
    odm_theme_helper.session = wsgi_app.session

  # IFacets
  def dataset_facets(self, facets_dict, package_type):

    facets_dict = {
              'license_id': toolkit._('License'),
              'tags': toolkit._('Topics'),
              'organization': toolkit._('Organizations'),
              'groups': toolkit._('Groups'),
              'res_format': toolkit._('Formats'),
              'odm_language': toolkit._('Language'),
              'odm_spatial_range': toolkit._('Country')
              }

    return facets_dict

  def group_facets(self, facets_dict, group_type, package_type):

    group_facets = {
              'license_id': toolkit._('License'),
              'tags': toolkit._('Topics'),
              'organization': toolkit._('Organizations'),
              'res_format': toolkit._('Formats'),
              'odm_language': toolkit._('Language'),
              'odm_spatial_range': toolkit._('Country')
              }

    return group_facets

  def organization_facets(self, facets_dict, organization_type, package_type):

    organization_facets = {
              'license_id': toolkit._('License'),
              'tags': toolkit._('Topics'),
              'groups': toolkit._('Groups'),
              'res_format': toolkit._('Formats'),
              'odm_language': toolkit._('Language'),
              'odm_spatial_range': toolkit._('Country')
              }

    return organization_facets

  # IRoutes
  def before_map(self, m):
    #m.connect('dataset_read', '/dataset/{id}',controller='package', action='read', ckan_icon='table')
    return m

  # IConfigurer
  def update_config(self, config):
    '''Update plugin config'''

    toolkit.add_template_directory(config, 'templates')
    toolkit.add_resource('fanstatic', 'odm_theme')
    toolkit.add_public_directory(config, 'public')

  # IValidators
  def get_validators(self):
    '''Register the plugin's functions above as validators.'''

    return {
      'odm_theme_clean_taxonomy_tags': clean_taxonomy_tags
      }

  # ITemplateHelpers
  def get_helpers(self):
    '''Register the plugin's functions below as template helper functions.'''

    return {
      'odm_theme_last_dataset': last_dataset,
      'odm_theme_localize_resource_url': localize_resource_url,
      'odm_theme_get_localized_tags_string': get_localized_tags_string,
      'odm_theme_get_localized_tag': get_localized_tag,
      'odm_theme_popular_groups': popular_groups,
      'odm_theme_recent_datasets': recent_datasets,
      'odm_theme_popular_datasets': popular_datasets,
      'odm_theme_tag_for_topic': tag_for_topic,
      'odm_theme_top_topics': top_topics,
      'odm_theme_languages': languages,
      'odm_theme_countries': countries,
      'odm_theme_odc_fields': odc_fields,
      'odm_theme_ckan_fields': ckan_fields,
      'odm_theme_metadata_fields': metadata_fields,
      'odm_theme_metadata_fields_combined': metadata_fields_combined,
      'odm_theme_get_orga_or_group': get_orga_or_group,
      'odm_theme_tag_dictionaries': get_tag_dictionaries,
      'odm_theme_taxonomy_dictionary': get_taxonomy_dictionary,
      'odm_theme_jsonify_countries': jsonify_countries,
      'odm_theme_jsonify_languages': jsonify_languages
    }

  def is_fallback(self):
    return True

  def package_types(self):
    return []

  # IPackageController
  def before_create(self, context, resource):
    log.info('before_create')

    odm_theme_helper.session['last_dataset'] = None
    odm_theme_helper.session.save()

  def after_create(self, context, pkg_dict):
    log.info('after_create: %s', pkg_dict['name'])

    odm_theme_helper.session['last_dataset'] = pkg_dict
    odm_theme_helper.session.save()

    # Create default Issue
    review_system = h.asbool(config.get("ckanext.issues.review_system", False))
    if review_system:
      if pkg_dict['type'] == 'library_record':
        create_default_issue_library_record(pkg_dict)
      else:
        create_default_issue_dataset(pkg_dict)

  def after_update(self, context, pkg_dict):
    log.info('after_update: %s', pkg_dict['name'])

    odm_theme_helper.session['last_dataset'] = pkg_dict
    odm_theme_helper.session.save()
