'''plugin.py

'''
import ckan
import pylons
import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import odm_theme_helper

log = logging.getLogger(__name__)

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

def metadata_fields():
    '''Return a list of metadata fields'''

    log.debug('metadata_fields')

    return odm_theme_helper.metadata_fields

def library_fields():
    '''Return a list of library fields'''

    log.debug('library_fields')

    return odm_theme_helper.library_fields

def most_popular_groups():
    '''Return a sorted list of the groups with the most datasets.'''

    # Get a list of all the site's groups from CKAN, sorted by number of
    # datasets.
    groups = toolkit.get_action('group_list')(
        data_dict={'sort': 'packages desc', 'all_fields': True})

    # Truncate the list to the 10 most popular groups only.
    groups = groups[:10]

    return groups

def is_library_group(group_id):

    '''Returns wether the current group is the library group'''

    log.debug('is_library_group: %s', group_id)

    if group_id is 'None':

        return False

    try:

        # Retrieve admin members from the specified organisation
        groups = toolkit.get_action('group_list')(
        data_dict={'groups': 'library-group'})

    except toolkit.ObjectNotFound:

        return False

    return (len(groups) > 0)

def is_user_admin_of_organisation(organization_name):

    '''Returns wether the current user has the Admin role in the specified organisation'''

    user_id = toolkit.c.userobj.id

    log.debug('is_user_admin_of_organisation: %s %s', user_id, organization_name)

    if organization_name is 'None':

        return False

    try:

        # Retrieve admin members from the specified organisation
        members = toolkit.get_action('member_list')(
        data_dict={'id': organization_name, 'object_type': 'user', 'capacity': 'admin'})

    except toolkit.ObjectNotFound:

        return False

    # 'members' is a list of (user_id, object_type, capacity) tuples, we're
    # only interested in the user_ids.
    member_ids = [member_tuple[0] for member_tuple in members]

    try:

        # Finally, we can test whether the user is a member of the curators group.
        if user_id in member_ids:

            return True

    except toolkit.Invalid:

        return False

    return False

class OdmThemePlugin(plugins.SingletonPlugin, toolkit.DefaultDatasetForm):
    '''ODM theme plugin.

    '''

    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config):

        toolkit.add_template_directory(config, 'templates')
        toolkit.add_resource('fanstatic', 'odm_theme')

    def get_helpers(self):
        '''Register the plugin's functions above as a template helper function.

        '''
        return {
          'odm_theme_get_localized_tag_string': get_localized_tag_string,
          'odm_theme_get_localized_tag': get_localized_tag,
          'odm_theme_most_popular_groups': most_popular_groups,
          'odm_theme_metadata_fields': metadata_fields,
          'odm_theme_library_fields': library_fields,
          'odm_theme_is_library_group': is_library_group,
          'odm_theme_is_user_admin_of_organisation': is_user_admin_of_organisation
        }

    def _modify_package_schema_write(self, schema):

        for metadata_field in odm_theme_helper.metadata_fields:
          schema.update({
              metadata_field[0]: [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_extras')]
          })

        for taxonomy in odm_theme_helper.taxonomy_fields:
          schema.update({
              taxonomy[0]: [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_tags')(taxonomy[0])]
          })

        for library_field in odm_theme_helper.library_fields:
          schema.update({
              library_field[0]: [toolkit.get_validator('ignore_missing'),toolkit.get_converter('convert_to_extras')]
          })

        return schema

    def _modify_package_schema_read(self, schema):

        for metadata_field in odm_theme_helper.metadata_fields:
          schema.update({
              metadata_field[0]: [toolkit.get_converter('convert_from_extras'),toolkit.get_validator('ignore_missing')]
          })

        for taxonomy in odm_theme_helper.taxonomy_fields:
          schema.update({
              taxonomy[0]: [toolkit.get_converter('convert_from_tags')(taxonomy[0]),toolkit.get_validator('ignore_missing')]
          })

        for library_field in odm_theme_helper.library_fields:
          schema.update({
              library_field[0]: [toolkit.get_converter('convert_from_extras'),toolkit.get_validator('ignore_missing')]
          })

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
