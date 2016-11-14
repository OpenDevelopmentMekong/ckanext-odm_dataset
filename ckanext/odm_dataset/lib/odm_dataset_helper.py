#!/usr/bin/env python
# -*- coding: utf-8 -*-

DEBUG = True

import pylons
import json
import ckan
import logging
import urlparse
import genshi
import datetime
import re
import uuid
import ckan.plugins.toolkit as toolkit

log = logging.getLogger(__name__)

def create_default_issue_dataset(pkg_info):
	''' Uses CKAN API to add a default Issue as part of the vetting workflow for datasets'''
	try:

		extra_vars = {
			't0': toolkit._("Thank you for uploading this item. Instructions about vetting system available on https://wiki.opendevelopmentmekong.net/partners:content_review#instructions_for_default_issue_on_datasets")
		}

		issue_message = ckan.lib.base.render('messages/default_issue_dataset.txt',extra_vars=extra_vars,loader_class=genshi.template.text.NewTextTemplate)

		params = {'title':'User Dataset Upload Checklist','description':issue_message,'dataset_id':pkg_info['id']}
		toolkit.get_action('issue_create')(data_dict=params)

	except KeyError:

		log.error("Action 'issue_create' not found. Please make sure that ckanext-issues plugin is installed.")

def last_dataset():
	''' Returns the last dataset info stored in session'''
	if 'last_dataset' in session:
		return session['last_dataset']

	return None

def clean_taxonomy_tags(value):
	'''Cleans taxonomy field before storing it'''

	if isinstance(value, basestring):
		 return json.dumps([value])

	return json.dumps(list(value))

def get_localized_tag(tag):
	'''Looks for a term translation for the specified tag. Returns the tag untranslated if no term found'''

	if DEBUG:
		log.debug('odm_dataset_get_localized_tag: %s', tag)

	desired_lang_code = pylons.request.environ['CKAN_LANG']

	translations = ckan.logic.action.get.term_translation_show(
					{'model': ckan.model},
					{'terms': (tag)})

	# Transform the translations into a more convenient structure.
	for translation in translations:
		if translation['lang_code'] == desired_lang_code:
			return translation['term_translation']

	return str(tag)

def get_current_language():
	'''Returns the current language code'''

	if DEBUG:
		log.debug('get_current_language')

	return pylons.request.environ['CKAN_LANG']

def get_value_for_current_language(value):
	'''Returns the corresponding value on the current language or the string if non-multilingual'''

	if DEBUG:
		log.debug('get_value_for_current_language')

	try:
		value = json.loads(value);

		if isinstance(value, basestring):
			return value

		return value[get_current_language()] or ""
	except:

		return ""

def get_localized_tags_string(tags_string):
	'''Returns a comma separated string with the translation of the tags specified. Calls get_localized_tag'''

	if DEBUG:
		log.debug('get_localized_tags_string: %s', tags_string)

	translated_array = []
	for tag in tags_string.split(', '):
		translated_array.append(get_localized_tag(tag))

	if len(translated_array)==0:
		return ''

	return ','.join(translated_array)

def convert_to_multilingual(data):
	'''Converts strings to multilingual with the current language set'''

	if DEBUG:
		log.debug('convert_to_multilingual: %s', data)

	if isinstance(data, basestring):
		multilingual_data = {}
		multilingual_data[get_current_language()] = data;
	else:
		multilingual_data = data

	return multilingual_data

def convert_to_list(value):
	'''Converts strings to list'''

	if DEBUG:
		log.debug('convert_to_list: %s', value)

	if isinstance(value, basestring):
		new_value = value.replace("{","")
		new_value = new_value.replace("}","")
		new_value = new_value.split(",")
		return new_value

	return value

def map_odm_spatial_range(value):

	if DEBUG:
		log.debug('map_odm_spatial_range: %s', value)

	if not value:
		return value

	if type(value) is list and len(value) == 1:
		value = value[0]

	if type(value) is list and len(value) > 1:
		return value

	odm_spatial_range = []

	if value.lower().find('laos') > -1 or value.lower().find('la') > -1:
		odm_spatial_range.append('la')
	if value.lower().find('vietnam') > -1 or value.lower().find('vn') > -1:
		odm_spatial_range.append('vn')
	if value.lower().find('thailand') > -1 or value.lower().find('th') > -1:
		odm_spatial_range.append('th')
	if value.lower().find('myanmar') > -1 or value.lower().find('mm') > -1:
		odm_spatial_range.append('mm')
	if value.lower().find('cambodia') > -1 or value.lower().find('kh') > -1:
		odm_spatial_range.append('kh')
	if value.lower().find('global') > -1:
		odm_spatial_range.append('global')
	if value.lower().find('asean') > -1:
		odm_spatial_range.append('asean')
	if value.lower().find('greater mekong subregion (gms)') > -1 or value.lower().find('gms') > -1:
		odm_spatial_range.append('gms')
	if value.lower().find('lower mekong basin') > -1 or value.lower().find('lmb') > -1:
		odm_spatial_range.append('lmb')
	if value.lower().find('lower mekong countries') > -1 or value.lower().find('lmc') > -1:
		odm_spatial_range.append('lmc')

	return odm_spatial_range

def map_odm_language(value):

	if DEBUG:
		log.debug('map_odm_language: %s', value)

	if not value:
		return value

	if type(value) is list and len(value) == 1:
		value = value[0]

	if type(value) is list and len(value) > 1:
		return value

	odm_language = []

	if value.lower().find('km') > -1 or value.lower().find('khmer') > -1:
		odm_language.append('km')
	if value.lower().find('vi') > -1 or value.lower().find('vietnamese') > -1:
		odm_language.append('vi')
	if value.lower().find('en') > -1 or value.lower().find('english') > -1:
		odm_language.append('en')
	if value.lower().find('lo') > -1 or value.lower().find('lao') > -1:
		odm_language.append('lo')
	if value.lower().find('th') > -1 or value.lower().find('thai') > -1:
		odm_language.append('th')
	if value.lower().find('my') > -1 or value.lower().find('burmese') > -1:
		odm_language.append('my')
	if value.lower().find('zh') > -1 or value.lower().find('chinese') > -1:
		odm_language.append('zh')
	if value.lower().find('fr') > -1 or value.lower().find('french') > -1:
		odm_language.append('fr')
	if value.lower().find('de') > -1 or value.lower().find('german') > -1:
		odm_language.append('de')
	if value.lower().find('jp') > -1 or value.lower().find('japanese') > -1:
		odm_language.append('jp')
	if value.lower().find('ko') > -1 or value.lower().find('korean') > -1:
		odm_language.append('ko')
	if value.lower().find('other') > -1:
		odm_language.append('other')

	return odm_language

def retrieve_taxonomy_from_tags(tags_array):
	'''Looks into the dataset's tags and set the taxonomy array out of their display_name property'''

	if DEBUG:
		log.debug('map_odm_language: %s', tags_array)

	if type(tags_array) is not list:
		return []

	taxonomy = []
	for tag in tags_array:
		taxonomy.append(tag['display_name'])

	return taxonomy

def get_current_time():

	return datetime.datetime.utcnow().isoformat()

def urlencode(value):
	value = re.sub(' ','-',value)
	pattern = re.compile('[^a-zA-Z0-9_-]', re.UNICODE)
	value = re.sub(pattern, '', value)
	return value.lower()[0:99]

def if_empty_new_id(value):

	if DEBUG:
		log.debug('if_empty_new_id: %s', value)

	if not value:
		value = str(uuid.uuid4());
	return value

def get_resource_from_datatable(resource_id):
	''' pulls tabular data from datastore '''

	result = toolkit.get_action('datastore_search')(data_dict={'resource_id': resource_id})

	return result['records']

def get_dataset_name(dataset_id):

	dataset_dict = toolkit.get_action('package_show')(data_dict={'id':dataset_id})
	return dataset_dict['name']

def get_dataset_notes(dataset_id, truncate):

	notes = None
	dataset_dict = toolkit.get_action('package_show')(data_dict={'id':dataset_id})

	if 'notes_translated' in dataset_dict :
		lang = pylons.request.environ['CKAN_LANG']
		if lang in dataset_dict['notes_translated']:
			notes = dataset_dict['notes_translated'][lang]
			if truncate == True and notes:
				notes = notes[0:99]

	return notes

session = {}
