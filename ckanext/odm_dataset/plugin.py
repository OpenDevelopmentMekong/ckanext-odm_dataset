'''plugin.py

'''
import ckan
import pylons
import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as h
from beaker.middleware import SessionMiddleware
import sys
import os
from pylons import config
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import odm_dataset_helper
import datetime
import time
from urlparse import urlparse
import json
import collections

log = logging.getLogger(__name__)

class OdmDatasetPlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
  '''OD Mekong dataset plugin.'''

  plugins.implements(plugins.IValidators, inherit=True)
  plugins.implements(plugins.IConfigurer)
  plugins.implements(plugins.ITemplateHelpers)
  plugins.implements(plugins.IRoutes, inherit=True)
  plugins.implements(plugins.IPackageController, inherit=True)

  def __init__(self, *args, **kwargs):

    log.debug('OdmDatasetPlugin init')
    wsgi_app = SessionMiddleware(None, None)
    odm_dataset_helper.session = wsgi_app.session

  # IRoutes
  def before_map(self, m):
    #m.connect('dataset_read', '/dataset/{id}',controller='package', action='read', ckan_icon='table')
    return m

  # IConfigurer
  def update_config(self, config):
    '''Update plugin config'''

    toolkit.add_template_directory(config, 'templates')
    toolkit.add_resource('fanstatic', 'odm_dataset')
    toolkit.add_public_directory(config, 'public')

  # IValidators
  def get_validators(self):
    '''Register the plugin's functions above as validators.'''

    return {
      'odm_dataset_convert_to_multilingual': odm_dataset_helper.convert_to_multilingual,
      'odm_dataset_clean_taxonomy_tags': odm_dataset_helper.clean_taxonomy_tags
      }

  # ITemplateHelpers
  def get_helpers(self):
    '''Register the plugin's functions below as template helper functions.'''

    return {
      'odm_dataset_last_dataset': odm_dataset_helper.last_dataset,
      'odm_dataset_get_current_language': odm_dataset_helper.get_current_language,
      'odm_dataset_get_value_for_current_language': odm_dataset_helper.get_value_for_current_language
    }

  # IPackageController
  def before_create(self, context, resource):

    dataset_type = context['package'].type if 'package' in context else ''
    if dataset_type == 'dataset':
      log.info('before_create')

      odm_dataset_helper.session['last_dataset'] = None
      odm_dataset_helper.session.save()

  def after_create(self, context, pkg_dict):

    dataset_type = context['package'].type if 'package' in context else pkg_dict['type']
    if dataset_type == 'dataset':
      log.info('after_create: %s', pkg_dict['name'])

      odm_dataset_helper.session['last_dataset'] = pkg_dict
      odm_dataset_helper.session.save()

      # Create default Issue
      review_system = h.asbool(config.get("ckanext.issues.review_system", False))
      if review_system:
        if pkg_dict['type'] == 'dataset':
          odm_dataset_helper.create_default_issue_dataset(pkg_dict)

  def after_update(self, context, pkg_dict):

    dataset_type = context['package'].type if 'package' in context else pkg_dict['type']
    if dataset_type == 'dataset':
      log.info('after_update: %s', pkg_dict['name'])

      odm_dataset_helper.session['last_dataset'] = pkg_dict
      odm_dataset_helper.session.save()
