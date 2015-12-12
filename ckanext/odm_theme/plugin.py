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
      'odm_theme_clean_taxonomy_tags': odm_theme_helper.clean_taxonomy_tags
      }

  # ITemplateHelpers
  def get_helpers(self):
    '''Register the plugin's functions below as template helper functions.'''

    return {
      'odm_theme_last_dataset': odm_theme_helper.last_dataset,
      'odm_theme_localize_resource_url': odm_theme_helper.localize_resource_url,
      'odm_theme_get_localized_tags_string': odm_theme_helper.get_localized_tags_string,
      'odm_theme_get_localized_tag': odm_theme_helper.get_localized_tag,
      'odm_theme_popular_groups': odm_theme_helper.popular_groups,
      'odm_theme_recent_datasets': odm_theme_helper.recent_datasets,
      'odm_theme_popular_datasets': odm_theme_helper.popular_datasets,
      'odm_theme_tag_for_topic': odm_theme_helper.tag_for_topic,
      'odm_theme_top_topics': odm_theme_helper.top_topics,
      'odm_theme_taxonomy_dictionary': odm_theme_helper.get_taxonomy_dictionary,
      'odm_theme_get_current_language': odm_theme_helper.get_current_language,
      'odm_theme_get_value_for_current_language': odm_theme_helper.get_value_for_current_language
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
