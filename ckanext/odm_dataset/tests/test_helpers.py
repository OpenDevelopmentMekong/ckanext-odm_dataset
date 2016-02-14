import os
import sys
import json
from nose.tools import assert_equal, assert_in, with_setup
import logging
import unittest
from unittest.case import SkipTest
sys.path.append(os.path.join(os.path.dirname(__file__), "../lib"))
import mock
import sys
sys.modules['pylons'] = mock.MagicMock()
sys.modules['ckan'] = mock.MagicMock()
sys.modules['plugins.toolkit'] = mock.MagicMock()
sys.modules['genshi'] = mock.MagicMock()
import odm_dataset_helper


log = logging.getLogger(__name__)

class TestHelpers(unittest.TestCase):

  @classmethod
  def setup_class(self):
    "set up test fixtures"

  @classmethod
  def teardown_class(self):
    "tear down test fixtures"

  def test_create_default_issue_dataset(self):
    "should create an issue with default text"
    raise SkipTest

  def test_clean_taxonomy_tags(self):
    "should output a json string with an array of tags if a single tag is passed"
    json_array_from_string = odm_dataset_helper.clean_taxonomy_tags('tag1')
    assert json_array_from_string == '["tag1"]'
    "should output a json string with an array of tags if an array is passed"
    json_array_from_csv = odm_dataset_helper.clean_taxonomy_tags(["tag1","tag2","tag3"])
    assert json_array_from_csv == json.dumps(["tag1","tag2","tag3"])

  def test_get_localized_tag_found_translation(self):
    "should return the translated tag if translation found"
    sys.modules['pylons'].request.environ = {'CKAN_LANG':'en'}
    sys.modules['ckan'].logic.action.get.term_translation_show.return_value = [{'lang_code': 'en','term_translation': 'tag1_translated'}]

    tag = odm_dataset_helper.get_localized_tag('tag1')
    assert tag == 'tag1_translated'
    assert sys.modules['ckan'].logic.action.get.term_translation_show.called

  def test_get_localized_tag_default(self):
    "should return the untranslated tag if no translation is found"
    sys.modules['pylons'].request.environ = {'CKAN_LANG':'en'}
    sys.modules['ckan'].logic.action.get.term_translation_show.return_value = []

    tag = odm_dataset_helper.get_localized_tag('non-translated')
    assert tag == 'non-translated'
    assert sys.modules['ckan'].logic.action.get.term_translation_show.called

  def test_get_localized_tags_string(self):
    "should return a comma-sepparated list of translated tags"
    sys.modules['pylons'].request.environ = {'CKAN_LANG':'en'}
    sys.modules['ckan'].logic.action.get.term_translation_show.return_value = [{'lang_code': 'en','term_translation': 'tag_translated'}]

    tags = odm_dataset_helper.get_localized_tags_string('tag1,tag2')
    assert tags == 'tag_translated'
    assert sys.modules['ckan'].logic.action.get.term_translation_show.called

  def test_get_current_language(self):
    "should return the current language"
    sys.modules['pylons'].request.environ = {'CKAN_LANG':'en'}

    lang = odm_dataset_helper.get_current_language()
    assert lang == 'en'

  def test_get_value_for_current_language(self):
    "should return the corresponding value to the current language from a json object (multilingual)"
    sys.modules['pylons'].request.environ = {'CKAN_LANG':'en'}

    value = odm_dataset_helper.get_value_for_current_language('{"en": "en_text", "km": "km_text"}')
    assert value == 'en_text'

  def test_convert_to_multilingual(self):
    "should return a multilingual compliant dict out of a non-multilingual compliant one"
    sys.modules['pylons'].request.environ = {'CKAN_LANG':'en'}

    value = odm_dataset_helper.convert_to_multilingual('value for field')
    assert json.dumps(value) == json.dumps({'en': 'value for field'})

    "should return a multilingual compliant dict out of multilingual compliant one"
    sys.modules['pylons'].request.environ = {'CKAN_LANG':'en'}

    value = odm_dataset_helper.convert_to_multilingual('{"en": "value for field"}')
    assert json.dumps(value) == json.dumps({'en': 'value for field'})
