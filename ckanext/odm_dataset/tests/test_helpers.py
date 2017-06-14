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
sys.modules['ckan.model'] = mock.MagicMock()
sys.modules['ckan.logic'] = mock.MagicMock()
sys.modules['ckan.plugins.toolkit'] = mock.MagicMock()
sys.modules['genshi'] = mock.MagicMock()
sys.modules['ckan.lib'] = mock.MagicMock()
sys.modules['ckan.lib.navl'] = mock.MagicMock()
sys.modules['ckan.lib.navl.dictization_functions'] = mock.MagicMock()

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

	def test_convert_csv_to_array(self):
		"should output a json string with an array of tags passed as csv string"
		json_array_from_csv = odm_dataset_helper.convert_csv_to_array('tag1, tag2')
		assert json_array_from_csv == ["tag1", "tag2"]

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
		"should trim anything besides alphanum chars, hypens and underscores"
		value = odm_dataset_helper.urlencode('sub-decree-no-157-on-establishment-of-neang-kok-koh-kong-sez')
		assert value == 'sub-decree-no-157-on-establishment-of-neang-kok-koh-kong-sez'

		value = odm_dataset_helper.urlencode('Hectare forest cover by province in Cambodia (1973 - 2014)')
		assert value == 'hectare-forest-cover-by-province-in-cambodia-1973---2014'

		value = odm_dataset_helper.urlencode('Lessons learnt of communal land titling for indigenous community in La In Village Ratanakiri province, northeast cambodai')
		assert value == 'lessons-learnt-of-communal-land-titling-for-indigenous-community-in-la-in-village-ratanakiri-provin'

	def test_sanitize_list(self):
		"should handle a single-value string"
		value = odm_dataset_helper.sanitize_list('en')
		assert value == '["en"]'

		"should remove brackets from a single-value string"
		value = odm_dataset_helper.sanitize_list('{value}')
		assert value == '["value"]'

		"should remove brackets from a multiple-value string"
		value = odm_dataset_helper.sanitize_list("{fr,ja}")
		assert value == '["fr", "ja"]'

		"should handle 'json' objects as well"
		value = odm_dataset_helper.sanitize_list({'value','value2'})
		assert value == '["value2", "value"]'

		"should handle 'json' objects as well"
		value = odm_dataset_helper.sanitize_list('{value}')
		assert value == '["value"]'

		"should handle lists as well"
		value = odm_dataset_helper.sanitize_list(['value','value2'])
		assert value == '["value", "value2"]'

		"should handle unicode lists as well"
		value = odm_dataset_helper.sanitize_list([u'value',u'value2'])
		assert value == '["value", "value2"]'

		"should handle lists as well"
		value = odm_dataset_helper.sanitize_list("{de,en}")
		assert value == '["de", "en"]'

		"should handle list of unicode strings"
		value = odm_dataset_helper.sanitize_list("[u'de', u'ja']")
		assert value == '["de", "ja"]'

		"should handle list of unicode strings"
		value = odm_dataset_helper.sanitize_list("[u'de']")
		assert value == '["de"]'

	def test_fluent_required_no_json(self):
		"should throw an error if value is not a json object"
		exception = False;
		try:
			value = odm_dataset_helper.fluent_required('en')
		except Exception:
			exception = True;
		assert exception

	def test_fluent_required_no_en_object(self):
		"should throw an error if key 'en' is not on the object"
		sys.modules['pylons'].request.environ = {'CKAN_LANG':'en'}
		exception = False;
		try:
			value = odm_dataset_helper.fluent_required('{"km":"some km value"}')
		except Exception:
			exception = True;
		assert exception

	def test_fluent_required_empty_en_object(self):
		"should throw an error if key 'en' is nempty"
		sys.modules['pylons'].request.environ = {'CKAN_LANG':'en'}
		exception = False;
		try:
			value = odm_dataset_helper.fluent_required('{"km":"some km value","en":""}')
		except Exception:
			exception = True;
		assert exception

	def test_fluent_required_no_string(self):
		"should throw an error if value is not passed as string"
		sys.modules['pylons'].request.environ = {'CKAN_LANG':'en'}
		exception = False;
		try:
			value = odm_dataset_helper.fluent_required({"en":"some en value"})
		except Exception:
			exception = True;
		assert exception == True

	def test_fluent_required_valid(self):
		"should not throw an error if value is right"
		sys.modules['pylons'].request.environ = {'CKAN_LANG':'en'}
		exception = False;
		try:
			value = odm_dataset_helper.fluent_required('{"en":"some en value"}')
		except Exception:
			exception = True;
		assert exception == False

	def test_date_to_iso(self):
		"should not throw an error and return the date in the wished format YYYY-mm-dd"
		value = odm_dataset_helper.date_to_iso('08/05/2016')
		assert value == '2016-08-05'

	def test_date_to_iso_2(self):
		"should not throw an error and return the date in the wished format YYYY-mm-dd"
		value = odm_dataset_helper.date_to_iso('06/12/2008')
		assert value == '2008-06-12'

	def test_date_to_iso_3(self):
		"should not throw an error and return the date in the wished format YYYY-mm-dd"
		value = odm_dataset_helper.date_to_iso('01/12/2016')
		assert value == '2016-01-12'

	def test_date_to_iso_4(self):
		"should not throw an error and return the date in the wished format YYYY-mm-dd"
		value = odm_dataset_helper.date_to_iso('04/26/2016')
		assert value == '2016-04-26'

	def test_date_to_iso_other_entry_format(self):
		"should return same value if date does not comply to expected"
		value = odm_dataset_helper.date_to_iso('08-05-2016')
		assert value == '2016-08-05'

	def test_date_to_iso_entry_isoformat(self):
		"should return same value if date does not comply to expected"
		value = odm_dataset_helper.date_to_iso('2016-08-05')
		assert value == '2016-08-05'

	def test_date_to_iso_entry_isoformat_none(self):
		"should return same value if date is None"
		value = odm_dataset_helper.date_to_iso(None)
		assert value == None

	def test_date_to_iso_entry_isoformat_yy(self):
		"should return same value if date is None"
		value = odm_dataset_helper.date_to_iso('06/12/08')
		assert value == '2008-06-12'

	def test_date_range_to_iso(self):
		"should not throw an error and return the date in the wished format YYYY-mm-dd - YYYY-mm-dd"
		value = odm_dataset_helper.date_range_to_iso('06/12/2008 - 08/14/2018')
		assert value == '2008-06-12 - 2018-08-14'

	def test_date_range_to_iso_2(self):
		"should not throw an error and return the date in the wished format YYYY-mm-dd - YYYY-mm-dd"
		value = odm_dataset_helper.date_range_to_iso('01/01/2001 - 12/25/2018')
		assert value == '2001-01-01 - 2018-12-25'

	def test_date_range_to_iso_3(self):
		"should not throw an error and return the date in the wished format YYYY-mm-dd - YYYY-mm-dd"
		value = odm_dataset_helper.date_range_to_iso('01/01/1930 - 07/12/2009')
		assert value == '1930-01-01 - 2009-07-12'

	def test_date_range_to_iso_other_format(self):
		"should not throw an error and return the same date range as inputted"
		value = odm_dataset_helper.date_range_to_iso('2001-01-01 - 2018-12-25')
		assert value == '2001-01-01 - 2018-12-25'
