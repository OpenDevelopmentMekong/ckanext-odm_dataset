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
import odm_dataset_config
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

  def get_validators(self):
    '''Register the plugin's functions above as validators.'''

    log.debug("get_validators")

    return {
      'odm_dataset_if_empty_new_id': odm_dataset_helper.if_empty_new_id,
      'odm_dataset_urlencode': odm_dataset_helper.urlencode,
      'odm_dataset_clean_taxonomy_tags': odm_dataset_helper.clean_taxonomy_tags,
      'odm_dataset_sanitize_list': odm_dataset_helper.sanitize_list,
			'odm_dataset_convert_to_multilingual': odm_dataset_helper.convert_to_multilingual,
      'odm_dataset_fluent_required': odm_dataset_helper.fluent_required,
			'odm_dataset_record_does_not_exist_yet': odm_dataset_helper.record_does_not_exist_yet
    }

  # ITemplateHelpers
  def get_helpers(self):
    '''Register the plugin's functions below as template helper functions.'''

    return {
      'odm_dataset_get_current_time': odm_dataset_helper.get_current_time,
      'odm_dataset_get_localized_tag': odm_dataset_helper.get_localized_tag,
      'odm_dataset_last_dataset': odm_dataset_helper.last_dataset,
      'odm_dataset_get_current_language': odm_dataset_helper.get_current_language,
      'odm_dataset_get_value_for_current_language': odm_dataset_helper.get_value_for_current_language,
      'odm_dataset_retrieve_taxonomy_from_tags': odm_dataset_helper.retrieve_taxonomy_from_tags,
      'odm_dataset_convert_to_multilingual': odm_dataset_helper.convert_to_multilingual,
      'odm_dataset_clean_taxonomy_tags': odm_dataset_helper.clean_taxonomy_tags,
      'odm_dataset_get_resource_from_datatable': odm_dataset_helper.get_resource_from_datatable,
      'odm_dataset_get_dataset_name': odm_dataset_helper.get_dataset_name,
      'odm_dataset_get_dataset_notes': odm_dataset_helper.get_dataset_notes,
      'odm_dataset_get_resource_id_for_field' : odm_dataset_config.get_resource_id_for_field,
      'odm_dataset_validate_fields' : odm_dataset_helper.validate_fields
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
