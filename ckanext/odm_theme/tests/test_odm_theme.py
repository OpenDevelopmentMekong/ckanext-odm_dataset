'''Tests for the ckanext.odm_theme extension.

   Tests should be run within the python environment:
   . /usr/lib/ckan/default/bin/activate

   Requires ODMImporter

   http://docs.ckan.org/en/latest/extensions/testing-extensions.html
'''
import paste.fixture
import pylons.test
import webtest
import ckan
import ckan.model as model
import ckan.tests as tests
import ckan.new_tests.factories as factories
import ckan.plugins as p
import logging
import ckanapi
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
import geoserver_utils
import ckanapi_utils
import github_utils
import ngl_utils
from odm_importer import ODMImporter
import odm_theme_config_test as config

class TestOdmThemePlugin(object):
  '''Tests for the ckanext.odm_theme.plugin module.

  '''
  @classmethod
  def setup_class(self):
    '''Nose runs this method once to setup our test class.'''

    self.log = logging.getLogger(__name__)
    self.log.debug('setup_class')

    self._loadPlugin()

    tests.CreateTestData.create()

    print("test data created")

  def teardown(self):
    '''Nose runs this method after each test method in our test class.'''

    self.log.debug('teardown')

    # Rebuild CKAN's database after each test method, so that each test
    # method runs with a clean slate.
    model.repo.rebuild_db()

  @classmethod
  def teardown_class(self):
    '''Nose runs this method once after all the test methods in our class
    have been run.

    '''
    self.log.debug('teardown_class')

    # We have to unload the plugin we loaded, so it doesn't affect any
    # tests that run after ours.
    self._unloadPlugin()

  @classmethod
  def _initContext(self):
    '''_initContext

    '''

    self.log.debug('Configuring: _initContext')

    self.app = paste.fixture.TestApp(pylons.test.pylonsapp)

    sysadmin = factories.Sysadmin()

    self.context = {
      'model': model,
      'session': model.Session,
      'user': sysadmin['name'],
      'apikey': sysadmin['apikey']
    }

  @classmethod
  def _loadPlugin(self):
    '''loads the plugin

    '''
    try:
      p.load('odm_theme')
    except Exception as e:
      print('odm_theme plugin already loaded')

  @classmethod
  def _unloadPlugin(self):
    '''unloads the plugin

    '''

    p.unload('odm_theme')

  @classmethod
  def _createOrganizationsAndGroups(self,ckanapiutils):
    '''_createOrganizationsAndGroups

    '''

    self.log.debug('Configuring: _createOrganizationsAndGroups')

    orgas = []
    orgas.append(config.GEOSERVER_MAP['organization'])
    orgas.append(config.NGL_MAP['organization'])
    orgas.append(config.DELETE_MAP['organization'])
    for item in config.ODC_MAP:
      orgas.append(item['organization'])

    for orga in orgas:
      try:
        ckanapiutils.add_organization(orga,orga,orga)
      except Exception as e:
        print("Organization "+ orga + " already exists.")

    groups = []
    for item in config.ODC_MAP:
      for group in item['groups']:
        groups.append(group['name'])

    for group in groups:
      try:
        ckanapiutils.add_group(group,group,group)
      except Exception as e:
        print("Group "+ group + " already exists.")

  def _initTaxonomyTagVocabulary(self,ckanapiutils,githubutils):
    '''_createOrganizationsAndGroups

    '''

    self.log.debug('Configuring: _initTaxonomyTagVocabulary')

    importer = ODMImporter()
    importer.import_taxonomy_tag_dictionaries(githubutils,ckanapiutils,config)

  def test_delete_datasets_in_group(self):
    '''test_delete_datasets_in_group

    '''

    self.log.debug('Running test: test_delete_datasets_in_group')

    self._initContext()
    githubutils = github_utils.TestGithubApi()
    ckanapiutils = ckanapi_utils.TestCkanApi(self.app,self.context)
    self._createOrganizationsAndGroups(ckanapiutils)
    self._initTaxonomyTagVocabulary(ckanapiutils,githubutils)

    organization = config.DELETE_MAP['organization']
    orga = ckanapiutils.get_organization_id_from_name(organization)

    # Add test dataset
    dataset_metadata = {'name':'testdataset','state':'active','owner_org':orga['id'],'notes':'testdataset notes','groups':[{'name':config.DELETE_MAP['group']}]}
    created_dataset = ckanapiutils.create_package(dataset_metadata)
    dataset_id = created_dataset['id']

    # Remove datasets from group
    importer = ODMImporter()
    importer.delete_datasets_in_group(ckanapiutils,config)

    params = {'fq':'+id:'+dataset_id}
    datasets = ckanapiutils.search_packages(params)

    if (config.DEBUG):
      print(datasets)

    if len(datasets['results']) > 0:
      assert False

    assert True

  def test_import_odc_contents(self):
    '''test_import_odc_contents

    '''

    self.log.debug('Running test: test_import_odc_contents')

    self._initContext()
    githubutils = github_utils.TestGithubApi()
    ckanapiutils = ckanapi_utils.TestCkanApi(self.app,self.context)
    self._createOrganizationsAndGroups(ckanapiutils)
    self._initTaxonomyTagVocabulary(ckanapiutils,githubutils)

    importer = ODMImporter()
    assert importer.import_odc_contents(githubutils,ckanapiutils,config)

  def test_import_marc21_library_records(self):
    '''test_import_marc21_library_records

    '''

    self.log.debug('Running test: test_import_marc21_library_records')

    self._initContext()
    githubutils = github_utils.TestGithubApi()
    ckanapiutils = ckanapi_utils.TestCkanApi(self.app,self.context)
    nglutils = ngl_utils.TestNGLApi()
    self._createOrganizationsAndGroups(ckanapiutils)
    self._initTaxonomyTagVocabulary(ckanapiutils,githubutils)

    importer = ODMImporter()
    assert importer.import_marc21_library_records(githubutils,ckanapiutils,nglutils,config)

  def test_import_from_geoserver(self):
    '''test_import_from_geoserver

    '''

    self.log.debug('Running test: test_import_from_geoserver')

    self._initContext()
    githubutils = github_utils.TestGithubApi()
    geoserverutils = geoserver_utils.TestGeoserverRestApi()
    ckanapiutils = ckanapi_utils.TestCkanApi(self.app,self.context)
    self._createOrganizationsAndGroups(ckanapiutils)
    self._initTaxonomyTagVocabulary(ckanapiutils,githubutils)

    importer = ODMImporter()
    assert importer.import_from_geoserver(geoserverutils,ckanapiutils,config)

  def test_import_taxonomy_tag_dictionaries(self):
    '''test_import_taxonomy_tag_dictionaries

    '''

    self.log.debug('Running test: test_import_taxonomy_tag_dictionaries')

    self._initContext()
    githubutils = github_utils.TestGithubApi()
    ckanapiutils = ckanapi_utils.TestCkanApi(self.app,self.context)
    self._createOrganizationsAndGroups(ckanapiutils)

    importer = ODMImporter()
    assert importer.import_taxonomy_tag_dictionaries(githubutils,ckanapiutils,config)

  def test_import_taxonomy_term_translations(self):
    '''test_import_taxonomy_term_translations

    '''

    self.log.debug('Running test: test_import_taxonomy_term_translations')

    self._initContext()
    githubutils = github_utils.TestGithubApi()
    ckanapiutils = ckanapi_utils.TestCkanApi(self.app,self.context)
    self._createOrganizationsAndGroups(ckanapiutils)

    importer = ODMImporter()
    assert importer.import_taxonomy_term_translations(githubutils,ckanapiutils,config)

  def test_import_languages_tag_dictionaries(self):
    '''test_import_languages_tag_dictionaries

    '''

    self.log.debug('Running test: test_import_languages_tag_dictionaries')

    self._initContext()
    githubutils = github_utils.TestGithubApi()
    ckanapiutils = ckanapi_utils.TestCkanApi(self.app,self.context)
    self._createOrganizationsAndGroups(ckanapiutils)

    importer = ODMImporter()
    assert importer.import_languages_tag_dictionaries(githubutils,ckanapiutils,config)

  def test_import_languages_term_translations(self):
    '''test_import_languages_term_translations

    '''

    self.log.debug('Running test: test_import_languages_term_translations')

    self._initContext()
    githubutils = github_utils.TestGithubApi()
    ckanapiutils = ckanapi_utils.TestCkanApi(self.app,self.context)
    self._createOrganizationsAndGroups(ckanapiutils)

    importer = ODMImporter()
    assert importer.import_languages_term_translations(githubutils,ckanapiutils,config)
