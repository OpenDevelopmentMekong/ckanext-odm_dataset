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
sys.modules['pylons'] = mock.Mock()
sys.modules['ckan'] = mock.Mock()
sys.modules['plugins.toolkit'] = mock.Mock()
sys.modules['genshi'] = mock.Mock()
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
    "should output a json string out of a comma-sepparated list of tags"
    json_array_from_string = odm_dataset_helper.clean_taxonomy_tags('tag1')
    assert json_array_from_string == '["tag1"]'
    json_array_from_csv = odm_dataset_helper.clean_taxonomy_tags(["tag1","tag2","tag3"])
    assert json_array_from_csv == json.dumps(["tag1","tag2","tag3"])

  def test_get_localized_tag(self):
    "should return the translated tag"
    raise SkipTest

  def test_get_localized_tag_default(self):
    "should return the untranslated tag if no translation is found"
    raise SkipTest

  def test_get_current_language(self):
    "should return the current language"
    raise SkipTest

  def test_get_value_for_current_language(self):
    "should return the corresponding value to the current language from a json object (multilingual)"
    raise SkipTest

  def test_get_localized_tags_string(self):
    "should return a comma-sepparated list of translated tags"
    raise SkipTest

  def test_convert_to_multilingual(self):
    "should return a multilingual compliant record out of a non-multilingual compliant one"
    raise SkipTest
