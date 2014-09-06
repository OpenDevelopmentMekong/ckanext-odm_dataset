'''plugin.py

'''
import logging
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit

log = logging.getLogger(__name__)

def most_popular_groups():
        '''Return a sorted list of the groups with the most datasets.'''

        # Get a list of all the site's groups from CKAN, sorted by number of
        # datasets.
        groups = toolkit.get_action('group_list')(
            data_dict={'sort': 'packages desc', 'all_fields': True})

        # Truncate the list to the 10 most popular groups only.
        groups = groups[:10]

        return groups

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
        

class OdmThemePlugin(plugins.SingletonPlugin):
    '''ODM theme plugin.

    '''

    # Declare that this class implements IConfigurer.
    plugins.implements(plugins.IConfigurer)

    # Declare that this plugin will implement ITemplateHelpers.
    plugins.implements(plugins.ITemplateHelpers)

    def update_config(self, config):

        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        # 'templates' is the path to the templates dir, relative to this
        # plugin.py file.
        toolkit.add_template_directory(config, 'templates')

        # Register this plugin's fanstatic directory with CKAN.
        # Here, 'fanstatic' is the path to the fanstatic directory
        # (relative to this plugin.py file), and 'example_theme' is the name
        # that we'll use to refer to this fanstatic directory from CKAN
        # templates.
        toolkit.add_resource('fanstatic', 'odm_theme')

    def get_helpers(self):
        '''Register the plugin's functions above as a template
        helper function.

        '''
        # Template helper function names should begin with the name of the
        # extension they belong to, to avoid clashing with functions from
        # other extensions.
        return {
            'odm_theme_most_popular_groups': most_popular_groups,
            'odm_theme_is_user_admin_of_organisation': is_user_admin_of_organisation
        }
