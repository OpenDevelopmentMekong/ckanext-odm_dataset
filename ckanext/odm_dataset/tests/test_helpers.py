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
sys.modules['ckan.plugins'] = mock.MagicMock()
sys.modules['ckan.plugins.toolkit'] = mock.MagicMock()
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
    assert json.dumps(value) == json.dumps({"en": "value for field"})

    "should return a multilingual compliant dict out of a non-multilingual compliant one, using non default language"
    sys.modules['pylons'].request.environ = {'CKAN_LANG':'km'}

    value = odm_dataset_helper.convert_to_multilingual('value for field')
    assert json.dumps(value) == json.dumps({"km": "value for field"})

    "should return a multilingual compliant dict out of multilingual compliant one"
    sys.modules['pylons'].request.environ = {'CKAN_LANG':'en'}

    value = odm_dataset_helper.convert_to_multilingual({"en": "value for field"})
    assert json.dumps(value) == json.dumps({"en": "value for field"})

    "should return an empty multilingual compliant dict out of an empty one"
    sys.modules['pylons'].request.environ = {'CKAN_LANG':'en'}

    value = odm_dataset_helper.convert_to_multilingual('')
    assert json.dumps(value) == json.dumps({"en": ''})

  def test_map_odm_language(self):
    "should return an array with valid language values when old values are passed"
    value = odm_dataset_helper.map_odm_language(['Vietnamese'])
    assert value == ['vi']
    value = odm_dataset_helper.map_odm_language(['Khmer'])
    assert value == ['km']
    value = odm_dataset_helper.map_odm_language(['Khmer Lao'])
    assert value == ['km','lo']

    "should return the same value if a valid array with 2+ items is passed"
    value = odm_dataset_helper.map_odm_language(['km','lo'])
    assert value == ['km','lo']

    "should ignore separation characters"
    value = odm_dataset_helper.map_odm_language(['Khmer; Lao; German'])
    assert value == ['km','lo','de']

  def test_map_odm_spatial_range(self):
    "should return an array with valid spatial range values when old values are passed"
    value = odm_dataset_helper.map_odm_spatial_range(['Cambodia'])
    assert value == ['kh']
    value = odm_dataset_helper.map_odm_spatial_range(['Vietnam'])
    assert value == ['vn']
    value = odm_dataset_helper.map_odm_spatial_range(['Vietnam Global'])
    assert value == ['vn','global']

    "should return the same value if a valid array with 2+ is passed"
    value = odm_dataset_helper.map_odm_spatial_range(['kh','asean'])
    assert value == ['kh','asean']

    "should ignore separation characters"
    value = odm_dataset_helper.map_odm_spatial_range(['Cambodia; greater mekong subregion (gms); lower mekong countries'])
    assert value == ['kh','gms','lmc']

  def test_retrieve_taxonomy_from_tags(self):
    "should return an array of taxonomic terms from an array of CKAN tags"
    value = odm_dataset_helper.retrieve_taxonomy_from_tags([{
      "vocabulary_id": "f3ff3686-c121-4b2e-87ae-6b52e084ca0e",
      "state": "active",
      "display_name": "Forest cover",
      "id": "e5c65074-ea5f-4af6-b91e-45c63b85264f",
      "name": "Forest cover"
    }])
    assert value == ['Forest cover']

    "should return an empty array if argument is not array"
    value = odm_dataset_helper.retrieve_taxonomy_from_tags(None)
    assert value == []

    "should return an empty array if argument is not array"
    value = odm_dataset_helper.retrieve_taxonomy_from_tags("test")
    assert value == []

  def test_urlencode(self):
    "should strim anything besides alphanum chars, hypens and underscores"
    value = odm_dataset_helper.urlencode('sub-decree-no-157-on-establishment-of-neang-kok-koh-kong-sez')
    assert value == 'sub-decree-no-157-on-establishment-of-neang-kok-koh-kong-sez'

    value = odm_dataset_helper.urlencode('Hectare forest cover by province in Cambodia (1973 - 2014)')
    assert value == 'hectare-forest-cover-by-province-in-cambodia-1973---2014'

    value = odm_dataset_helper.urlencode('Lessons learnt of communal land titling for indigenous community in La In Village Ratanakiri province, northeast cambodai')
    assert value == 'lessons-learnt-of-communal-land-titling-for-indigenous-community-in-la-in-village-ratanakiri-provin'
