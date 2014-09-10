'''Tests for the ckanext.odm_theme extension.

   Tests should be run within the python environment:
   . /usr/lib/ckan/default/bin/activate
   
   http://docs.ckan.org/en/latest/extensions/testing-extensions.html
'''
import paste.fixture
import pylons.test
import pylons.config as config
import webtest
import ckan.model as model
import ckan.tests as tests
import ckan.plugins
#import ckan.new_tests.factories as factories

class TestOdmThemePlugin(object):
    '''Tests for the ckanext.odm_theme.plugin module.

    '''
    @classmethod
    def setup_class(cls):
        '''Nose runs this method once to setup our test class.'''

        # Make the Paste TestApp that we'll use to simulate HTTP requests to
        # CKAN.
        cls.app = paste.fixture.TestApp(pylons.test.pylonsapp)

        # Test code should use CKAN's plugins.load() function to load plugins
        # to be tested.
        ckan.plugins.load('odm_theme')

    def teardown(self):
        '''Nose runs this method after each test method in our test class.'''

        # Rebuild CKAN's database after each test method, so that each test
        # method runs with a clean slate.
        model.repo.rebuild_db()

    @classmethod
    def teardown_class(cls):
        '''Nose runs this method once after all the test methods in our class
        have been run.

        '''
        # We have to unload the plugin we loaded, so it doesn't affect any
        # tests that run after ours.
        ckan.plugins.unload('odm_theme')

    def test_dummy(self):
        '''A dummy test

        '''    
        assert True
