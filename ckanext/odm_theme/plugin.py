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

def create_default_issue(pkg_info):
  ''' Uses CKAN API to add a default Issue as part of the vetting workflow'''
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

    issue_message = render('messages/default_issue.txt',extra_vars=extra_vars,loader_class=NewTextTemplate)

    params = {'title':'Vetting process: Please read this','description':issue_message,'dataset_id':pkg_info['id']}
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

def get_tag_dictionaries_json(vocab_id):
  '''Returns the tag dictionary for the specified vocab_id, in json format and adding indexes'''

  return jsonify_list(get_tag_dictionaries(vocab_id))

def jsonify_list(input_list):
  '''Returns the tag dictionary for the specified vocab_id, in json format and adding indexes'''

  log.debug('jsonify_list: %s', input_list)

  items = []

  if not isinstance(input_list, list):
    return items

  for item in input_list:
    items.append({'id':item,'text':get_localized_tag(item)})

  return json.dumps(items)

def jsonify_countries():
  '''Returns the tag dictionary for the countries'''

  log.debug('jsonify_countries')

  items = []
  for country in countries():
    items.append({'id':country[0],'text':country[0]})

  return json.dumps(items)

def jsonify_languages():
  '''Returns the tag dictionary for the languages'''

  log.debug('jsonify_languages')

  items = []
  for language in languages():
    items.append({'id':language[0],'text':language[1]})

  return json.dumps(items)

def validate_not_empty(value,context):
  '''Returns if a string is empty or not'''

  log.debug('validate_not_empty: %s', value)

  if not value or len(value) is None:
    raise toolkit.Invalid('Missing value')
  return value

def get_localized_tag(tag):
  '''Looks for a term translation for the specified tag. Returns the tag untranslated if no term found'''

  log.debug('odm_theme_get_localized_tag: %s', tag)

  desired_lang_code = pylons.request.environ['CKAN_LANG']

  translations = ckan.logic.action.get.term_translation_show(
          {'model': ckan.model},
          {'terms': (tag)})

  # Transform the translations into a more convenient structure.
  for translation in translations:
    if translation['lang_code'] == desired_lang_code:
      return translation['term_translation']

  return tag

def get_localized_tag_string(tags_string):
  '''Returns a comma separated string with the translation of the tags specified. Calls get_localized_tag'''

  log.debug('get_localized_tag_string: %s', tags_string)

  translated_array = []
  for tag in tags_string.split(', '):
    translated_array.append(get_localized_tag(tag))

  if len(translated_array)==0:
    return ''

  return ','.join(translated_array)

def tag_for_topic(topic):
  '''Return the name of the tag corresponding to a top topic'''

  log.debug('tag_for_topic')

  tag_name = ''.join(ch for ch in topic if (ch.isalnum() or ch == '_' or ch == '-' or ch == ' ' ))
  return tag_name if len(tag_name)<=100 else tag_name[0:99]

def top_topics():
  '''Return a list of top_topics'''

  log.debug('top_topics')

  return odm_theme_helper.top_topics

def countries():
  '''Return a list of countries'''

  log.debug('countries')

  return odm_theme_helper.countries

def languages():
  '''Return a list of languages'''

  log.debug('languages')

  return odm_theme_helper.languages

def odc_fields():
  '''Return a list of odc fields'''

  log.debug('odc_fields')

  return odm_theme_helper.odc_fields

def ckan_fields():
  '''Return a list of ckan fields'''

  log.debug('ckan_fields')

  return odm_theme_helper.ckan_fields

def metadata_fields():
  '''Return a list of metadata fields'''

  log.debug('metadata_fields')

  return odm_theme_helper.metadata_fields

def metadata_fields_combined():
  '''Return a list of metadata fields, combined with metadata_fields_combined'''

  log.debug('metadata_fields_combined')

  return list(set(odm_theme_helper.metadata_fields + odm_theme_helper.metadata_fields_compact))

def popular_groups():
  '''Return a sorted list of the groups with the most datasets.'''

  # Get a list of all the site's groups from CKAN, sorted by number of
  # datasets.
  groups = toolkit.get_action('group_list')(
      data_dict={'sort': 'packages desc', 'all_fields': True})

  # Truncate the list to the 10 most popular groups only.
  groups = groups[:10]

  return groups

def recent_datasets():
  '''Return a sorted list of the datasets updated recently.'''

  # Get a list of all the site's groups from CKAN, sorted by number of
  # datasets.
  dataset = toolkit.get_action('current_package_list_with_resources')(
      data_dict={'limit': 10})

  return dataset

def popular_datasets(limit):
  '''Return a sorted list of the most popular datasets.'''

  # Get a list of all the site's groups from CKAN, sorted by number of
  # datasets.
  result_dict = toolkit.get_action('package_search')(
      data_dict={'sort': 'views_recent desc', 'rows': limit})

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

  plugins.implements(plugins.IDatasetForm)
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
                'organization': toolkit._('Organizations'),
                'groups': toolkit._('Groups'),
                'tags': toolkit._('Tags'),
                'res_format': toolkit._('Formats'),
                'odm_language': toolkit._('Language'),
                'odm_spatial_range': toolkit._('Country')
                }

      return facets_dict

  def group_facets(self, facets_dict, group_type, package_type):

      group_facets = {
                'license_id': toolkit._('License'),
                'organization': toolkit._('Organizations'),
                'tags': toolkit._('Tags'),
                'res_format': toolkit._('Formats'),
                'odm_language': toolkit._('Language'),
                'odm_spatial_range': toolkit._('Country')
                }

      return group_facets

  def organization_facets(self, facets_dict, organization_type, package_type):

      organization_facets = {
                'license_id': toolkit._('License'),
                'groups': toolkit._('Groups'),
                'tags': toolkit._('Tags'),
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

  # IConfigurer

  def get_helpers(self):
    '''Register the plugin's functions above as a template helper function.'''

    return {
      'odm_theme_last_dataset': last_dataset,
      'odm_theme_localize_resource_url': localize_resource_url,
      'odm_theme_get_localized_tag_string': get_localized_tag_string,
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
      'odm_theme_jsonify_list': jsonify_list,
      'odm_theme_jsonify_countries': jsonify_countries,
      'odm_theme_jsonify_languages': jsonify_languages
    }

  # IDatasetForm

  def _modify_package_schema_write(self, schema):

    for metadata_field in odm_theme_helper.metadata_fields:
      validators_and_converters = [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_extras'), ]
      if metadata_field[2]:
        validators_and_converters.insert(1,validate_not_empty)
      schema.update({metadata_field[0]: validators_and_converters})

    for odc_field in odm_theme_helper.odc_fields:
      validators_and_converters = [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_extras'), ]
      if odc_field[2]:
        validators_and_converters.insert(1,validate_not_empty)
      schema.update({odc_field[0]: validators_and_converters})

    for ckan_field in odm_theme_helper.ckan_fields:
      validators_and_converters = [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_extras'), ]
      if ckan_field[2]:
        validators_and_converters.insert(1,validate_not_empty)
      schema.update({ckan_field[0]: validators_and_converters})

    for tag_dictionary in odm_theme_helper.tag_dictionaries:
      schema.update({tag_dictionary[0]: [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_tags')(tag_dictionary[0])]})

    return schema

  def _modify_package_schema_read(self, schema):

    for metadata_field in odm_theme_helper.metadata_fields:
      validators_and_converters = [toolkit.get_converter('convert_from_extras'),toolkit.get_validator('ignore_missing')]
      if metadata_field[2]:
        validators_and_converters.append(validate_not_empty)
      schema.update({metadata_field[0]: validators_and_converters})

    for odc_field in odm_theme_helper.odc_fields:
      validators_and_converters = [toolkit.get_converter('convert_from_extras'),toolkit.get_validator('ignore_missing')]
      if odc_field[2]:
        validators_and_converters.append(validate_not_empty)
      schema.update({odc_field[0]: validators_and_converters})

    for ckan_field in odm_theme_helper.ckan_fields:
      validators_and_converters = [toolkit.get_converter('convert_from_extras'),toolkit.get_validator('ignore_missing')]
      if ckan_field[2]:
        validators_and_converters.append(validate_not_empty)
      schema.update({ckan_field[0]: validators_and_converters})

    for tag_dictionary in odm_theme_helper.tag_dictionaries:
      schema.update({tag_dictionary[0]: [toolkit.get_converter('convert_from_tags')(tag_dictionary[0]),toolkit.get_validator('ignore_missing')]})

    return schema

  def create_package_schema(self):
    schema = super(OdmThemePlugin, self).create_package_schema()
    schema = self._modify_package_schema_write(schema)
    return schema

  def update_package_schema(self):
    schema = super(OdmThemePlugin, self).update_package_schema()
    schema = self._modify_package_schema_write(schema)
    return schema

  def show_package_schema(self):
    schema = super(OdmThemePlugin, self).show_package_schema()
    schema = self._modify_package_schema_read(schema)
    return schema

  def is_fallback(self):
    return True

  def package_types(self):
    return []

  def before_create(self, context, resource):
    log.info('before_create')

    odm_theme_helper.session['last_dataset'] = None
    odm_theme_helper.session.save()

  def after_create(self, context, pkg_dict):
    log.debug('after_create: %s', pkg_dict['name'])

    odm_theme_helper.session['last_dataset'] = pkg_dict
    odm_theme_helper.session.save()

    # Create default Issue
    review_system = h.asbool(config.get("ckanext.issues.review_system", False))
    if review_system:
      create_default_issue(pkg_dict)

  def after_update(self, context, pkg_dict):
    log.debug('after_update: %s', pkg_dict['name'])

    odm_theme_helper.session['last_dataset'] = pkg_dict
    odm_theme_helper.session.save()
