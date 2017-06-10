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
import os
import ckan.model as model
import ckan.plugins.toolkit as toolkit
import ckan.logic as logic
from ckan.plugins.toolkit import Invalid

import ckan.lib.navl.dictization_functions as df
missing = df.missing

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

def convert_csv_to_array(value):
	'''Splits elements of a csv string'''

	return list(value.replace(" ", "").split(','))

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
		log.info('get_current_language %s', pylons.request.environ['CKAN_LANG'])

	return pylons.request.environ['CKAN_LANG']

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

def if_empty_same_as_name_if_not_empty(key, data, errors, context):

	if DEBUG:
		log.info('if_empty_same_as_name_if_not_empty: %s', key)

	value = data.get(key)
	if not value or value is missing:
		value_replacement = data[key[:-1] + ("name",)]
		if value_replacement:
			data[key] = value_replacement

def if_empty_same_as_description_if_not_empty(key, data, errors, context):

	if DEBUG:
		log.info('if_empty_same_as_description_if_not_empty: %s', key)

	value = data.get(key)
	if not value or value is missing:
		value_replacement = data[key[:-1] + ("description",)]
		if value_replacement:
			data[key] = value_replacement

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
		raise Invalid("This multilingual field is mandatory. Please specify a value, at least in English.")

	if "en" not in value_json or not value_json["en"]:
		raise Invalid("This multilingual field is mandatory. Please specify a value, at least in English.")

	return value

def validate_fields(package):
	'''Checks that the package has all fields marked with validate = true on schema'''

	if DEBUG:
		log.info('validate_fields: %s', package)

	missing = dict({"package" : [], "resources": [] })

	schema_path = os.path.abspath(os.path.join(__file__, '../../','odm_dataset_schema.json'))
	with open(schema_path) as f:
		try:
			schema_json = json.loads(f.read())

			for field in schema_json['dataset_fields']:
				if "validate" in field and field["validate"] == "true":
					if field["field_name"] not in package or not package[field["field_name"]]:
						missing["package"].append(field["field_name"])
					elif "multilingual" in field and field["multilingual"] == "true":
						json_field = package[field["field_name"]];
						if json_field and "en" not in json_field or json_field["en"] == "":
							missing["package"].append(field["field_name"])

			for resource_field in schema_json['resource_fields']:
				for resource in package["resources"]:
					if "validate" in resource_field and resource_field["validate"] == "true":
					 	if resource_field["field_name"] not in resource or not resource[resource_field["field_name"]]:
							missing["resources"].append(resource_field["field_name"])
						elif "multilingual" in resource_field and resource_field["multilingual"] == "true":
							json_resource_field = resource[resource_field["field_name"]];
							if json_resource_field and "en" not in json_resource_field or json_resource_field["en"] == "":
								missing["resources"].append(resource_field["field_name"])

		except ValueError as e:
			log.info('invalid json: %s' % e)

	return missing

def record_does_not_exist_yet(value, context):
	'''Checks whether the value corresponds to an existing record name, if so raises Invalid'''

	found = True

	if DEBUG:
		log.info('record_does_not_exist_yet: %s %s', value, context)

	if 'package' in context:
		current_package = context['package']
		if current_package.name == value:
			return value

	s = """SELECT * FROM package p
					WHERE p.name = '%(name)s'""" % {'name': value}
	count = model.Session.execute(s).rowcount

	if count > 0:
		raise Invalid("There is a record already with that name, please adapt URL.")

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

def date_to_iso(value):
	''' Converts the date format from MM/DD/YYYY to YYYY-mm-dd,
			if the entered format does not correspond, it returns the same value'''

	# if DEBUG:
	# 	log.info('date_to_iso: %s', value)
	# 
	# try:
	# 	new_date = datetime.datetime.strptime(value,"%m/%d/%Y")
	# except ValueError:
	# 	return value
	# 
	# return new_date.isoformat()
	
	return "01/01/2001"

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
