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
import ckan.logic as logic
from ckan.plugins.toolkit import Invalid

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
		log.info('odm_dataset_get_localized_tag: %s', tag)

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
		log.info('get_current_language')

	return pylons.request.environ['CKAN_LANG']

def get_value_for_current_language(value):
	'''Returns the corresponding value on the current language or the string if non-multilingual'''

	if DEBUG:
		log.info('get_value_for_current_language')

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
		log.info('get_localized_tags_string: %s', tags_string)

	translated_array = []
	for tag in tags_string.split(', '):
		translated_array.append(get_localized_tag(tag))

	if len(translated_array)==0:
		return ''

	return ','.join(translated_array)

def convert_to_multilingual(data):
	'''Converts strings to multilingual with the current language set'''

	if DEBUG:
		log.info('convert_to_multilingual: %s', data)

	if isinstance(data, basestring):
		multilingual_data = {}
		multilingual_data[get_current_language()] = data;
	else:
		multilingual_data = data

	return multilingual_data

def sanitize_list(value):
	'''Converts strings to list'''

	if DEBUG:
		log.info('sanitize_list: %s', value)

	result = []

	if isinstance(value, list):
		for item in value:
			result.append(str(item))

	if isinstance(value, set):
		for item in value:
			result.append(item)

	if isinstance(value, basestring):
		new_value = value.encode("ascii")
		new_value = new_value.replace("[u'","")
		new_value = new_value.replace(" u'","")
		new_value = new_value.replace("']","")
		new_value = new_value.replace("'","")
		new_value = new_value.replace("{","")
		new_value = new_value.replace("}","")
		result = new_value.split(",")

	return json.dumps(result)

def fluent_required(value):
	'''Checks that the value inputed is a json object with at least "en" among its keys'''

	if DEBUG:
		log.info('fluent_required: %s', value)

	value_json = {}

	try:
		value_json = json.loads(value);
	except:
		raise Invalid("This multilingual field is mandatory. Please specify a value")

	if not value_json[get_current_language()]:
		raise Invalid("This multilingual field is mandatory. Please specify a value")

	return value

def record_does_not_exist_yet(value, context):
	'''Checks whether the value corresponds to an existing record name, if so raises Invalid'''

	found = True

	if DEBUG:
		log.info('record_does_not_exist_yet: %s', value)

	try:
		package = logic.get_action('package_show')(context, {"id":value})

	except logic.NotFound:
		found = False

	if found:
		raise Invalid("There is a record already with tha name, please adapt URL.")

	return value

def retrieve_taxonomy_from_tags(tags_array):
	'''Looks into the dataset's tags and set the taxonomy array out of their display_name property'''

	if DEBUG:
		log.info('map_odm_language: %s', tags_array)

	if type(tags_array) is not list:
		return []

	taxonomy = []
	for tag in tags_array:
		taxonomy.append(tag['display_name'])

	return taxonomy

def get_current_time():

	return datetime.datetime.utcnow().isoformat()

def urlencode(value):

	if DEBUG:
		log.info('urlencode: %s', value)

	value = re.sub(' ','-',value)
	pattern = re.compile('[^a-zA-Z0-9_-]', re.UNICODE)
	value = re.sub(pattern, '', value)
	return value.lower()[0:99]

def if_empty_new_id(value):

	if DEBUG:
		log.info('if_empty_new_id: %s', value)

	if not value:
		value = str(uuid.uuid4());
	return value

def get_resource_from_datatable(resource_id):
	''' pulls tabular data from datastore '''

	result = toolkit.get_action('datastore_search')(data_dict={'resource_id': resource_id,'limit':1000})

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
