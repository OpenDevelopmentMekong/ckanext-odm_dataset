#!/usr/bin/env python
# -*- coding: utf-8 -*-

import urllib2
import urllib
import json
import logging
import traceback
import ckan
import ckanapi
import re
import sys
import os
import io
import uuid
import lxml
import urlparse
from pymarc import MARCReader,marcxml
from lxml import etree
sys.path.append(os.path.join(os.path.dirname(__file__), "../lib"))
import odm_theme_helper

# Class containing methods to import data into CKAN
class ODMImporter():

  def __init__(self):

    self.log = logging.getLogger(__name__)
    self.log.debug('init ODMImporter')

    self.temppath = '/var/tmp/'
    return

  # Deletes the datasets of a certain group
  # Collects IDs of datasets belonging to the group specified in the config
  # and calls bulk_update_delete to mark them all for deletion
  def delete_datasets_in_group(self,ckanapi_utils,config):

    try:

      orga_datasets = {}
      datasets = []
      counter = 0
      state_filter = None
      if 'state' in config.DELETE_MAP:
        state_filter = config.DELETE_MAP['state']
      field_filter = None
      if 'field_filter' in config.DELETE_MAP:
        field_filter = config.DELETE_MAP['field_filter']
      if 'organization' in config.DELETE_MAP:
        params = {'id':config.DELETE_MAP['organization']}
        datasets = ckanapi_utils.get_packages_in_organization(params)
      elif 'group' in config.DELETE_MAP:
        params = {'id':config.DELETE_MAP['group'],'limit':config.DELETE_MAP['limit']}
        datasets = ckanapi_utils.get_packages_in_group(params)
      else:
        params = {'rows':config.DELETE_MAP['limit']}
        if state_filter is not None:
          params['fq'] = '+state:'+state_filter
        datasets = ckanapi_utils.search_packages(params)['results']

      for dataset in datasets:
        if counter < int(config.DELETE_MAP['limit']):

          filter_matching = True
          if field_filter is not None:
            matching_extras = []
            supported_fields = odm_theme_helper.odc_fields + odm_theme_helper.metadata_fields + odm_theme_helper.library_fields
            for field_key in field_filter.keys():
              if field_key in dataset and dataset[field_key] == field_filter[field_key]:
                if field_key not in matching_extras:
                  matching_extras.append(field_key)

            if len(matching_extras) != len(field_filter.keys()):
              filter_matching = False

          state_matching = True
          if state_filter is not None and dataset['state'] != state_filter:
            state_matching = False

          if state_matching and filter_matching:
            if dataset['owner_org'] not in orga_datasets.keys():
              orga_datasets[dataset['owner_org']] = []
            orga_datasets[dataset['owner_org']].append(dataset['id'])
            counter = counter + 1

      if (config.DEBUG):
        print(orga_datasets)

      for orga_id in orga_datasets.keys():
        params = {'datasets':orga_datasets[orga_id],'org_id':orga_id}
        #ckanapi_utils.delete_packages_list(params)

    except ckanapi.NotFound:

      print 'Group ' + config.DELETE_MAP['group'] + ' not found'

    print("COMPLETED delete_datasets_in_group")

  # Import odc contents into CKAN
  # Pulls the exported XML files from the current ODC Website
  # ( hosted under https://github.com/OpenDevelopmentMekong/odm-migration ) and
  # creates archived datasets.
  def import_odc_contents(self,github_utils,ckanapi_utils,config):

    for config_item in config.ODC_MAP:

      ontology = config_item['ontology']
      ontology_xml = github_utils.get_odc_ontology(ontology)

      taxonomy_tags = ckanapi_utils.get_all_tags_from_tag_vocabulary({'vocabulary_id':config.TAXONOMY_TAG_VOCAB})

      try:
        organization = config_item['organization']
        orga = ckanapi_utils.get_organization_id_from_name(organization)
      except ckanapi.NotFound:
        print("Organization " + organization + " not found, please check config")
        return False

      if (ontology_xml):

        try:

          context = etree.iterparse(io.BytesIO(ontology_xml), events=('end', ))
          context = iter(context)
          root = context.next()[1]
          counter = 0

          for event, elem in context:
            if event == "end" and elem.tag == "item":

              if (elem.find('wp:status',root.nsmap) is not None):
                status = elem.find('wp:status',root.nsmap).text

                if status == 'publish':

                  if ((int(config.SKIP_N_DATASETS) > 0) and (counter < int(config.SKIP_N_DATASETS))):
                    counter += 1
                    continue

                  dataset_metadata = self._map_xml_item_to_ckan_dataset_dict(orga,root,elem,config_item,taxonomy_tags,config)
                  dataset_metadata = self._set_extras_from_xml_item_to_ckan_dataset_dict(dataset_metadata,config_item,root,elem,config)

                  if (config.DEBUG):
                    print(dataset_metadata)
                    self.log.debug(dataset_metadata)

                  try:

                    response = ckanapi_utils.get_package_contents(dataset_metadata['name'])

                    if config.SKIP_EXISTING:
                      print("Dataset skipped ",dataset_metadata['name'])
                      continue

                    dataset_metadata = ckanapi_utils.update_package(dataset_metadata)
                    print("Dataset modified ",dataset_metadata['id'],dataset_metadata['title'])

                  except (ckanapi.SearchError,ckanapi.NotFound) as e:

                    try:

                      dataset_metadata = ckanapi_utils.create_package(dataset_metadata)
                      print("Dataset created ",dataset_metadata['id'],dataset_metadata['title'])

                    except TypeError as e:

                      print(e)

                  if 'id' in dataset_metadata:
                    self._add_extras_urls_as_resources(dataset_metadata,config_item,ckanapi_utils)

              elem.clear()

          root.clear()

        except TypeError as e:
          if (config.DEBUG):
            traceback.print_exc()
        except etree.XMLSyntaxError as e:
          if (config.DEBUG):
            traceback.print_exc()

    print("COMPLETED import_odc_contents")

    return True

  # Import marc21 library records into CKAN
  # Takes a marc21 formatted binary file from https://github.com/OpenDevelopmentMekong/odm-library
  # parses the information (metadata, additional material to download ) contained on the fields,
  # stores the records as Datasets and adds alternative representations (MARC21, MARCXML, MARCJSON).
  # Uses https://github.com/edsu/pymarc
  # TODO: Add link to covers in field 59X
  def import_marc21_library_records(self,github_utils,ckanapi_utils,ngl_utils,config):

    records = github_utils.get_library_records()

    try:
      organization = config.NGL_MAP['organization']
      orga = ckanapi_utils.get_organization_id_from_name(organization)
    except ckanapi.NotFound:
      print("Organization " + organization + " not found, please check config")
      return False

    reader = MARCReader(records)
    counter = 0
    for record in reader:

      if ((int(config.SKIP_N_DATASETS) > 0) and (counter < int(config.SKIP_N_DATASETS))):
        counter += 1
        continue

      dataset_metadata = self._map_record_to_ckan_dataset_dict(record,config)
      dataset_metadata = self._set_extras_from_record_to_ckan_dataset_dict(dataset_metadata,record,config)

      if (dataset_metadata is None) or (dataset_metadata["name"] == ''):
        print("Dataset does not have any title or ISBN, unique name cannot be generated")
        continue
      dataset_metadata['owner_org'] = orga['id']
      dataset_metadata['groups']	= config.NGL_MAP['groups']

      try:

        response = ckanapi_utils.get_package_contents(dataset_metadata['name'])

        if config.SKIP_EXISTING:
          print("Dataset skipped ",dataset_metadata['name'])
          continue

        modified_dataset = ckanapi_utils.update_package(dataset_metadata)
        dataset_metadata['id'] = modified_dataset['id']
        print("Dataset modified ",modified_dataset['id'],modified_dataset['title'])

      except (ckanapi.SearchError,ckanapi.NotFound) as e:

        created_dataset = ckanapi_utils.create_package(dataset_metadata)
        dataset_metadata['id'] = created_dataset['id']
        print("Dataset created ",created_dataset['id'],created_dataset['title'])

      try:

        temp_file_path = self._generate_temp_filename('xml')

        with open(temp_file_path, 'w') as fw:
          xml = marcxml.record_to_xml(record)
          fw.write(xml)
          fw.close()

        resource_dict = self._create_metadata_dictionary_for_upload(dataset_metadata['id'],"N/A",temp_file_path,dataset_metadata['title'],'Alternative representation [MARCXML]','xml')
        ckanapi_utils.create_resource_with_file_upload(resource_dict)
        if os.path.exists(temp_file_path):
          os.remove(temp_file_path)

      except (ValueError, OSError) as e:
        if (config.DEBUG):
          traceback.print_exc()

      try:

        temp_file_path = self._generate_temp_filename('json')

        with open(temp_file_path, 'w') as fw:
          json = record.as_json()
          fw.write(json)
          fw.close()

        resource_dict = self._create_metadata_dictionary_for_upload(dataset_metadata['id'],"N/A",temp_file_path,dataset_metadata['title'],'Alternative representation [JSON]','json')
        ckanapi_utils.create_resource_with_file_upload(resource_dict)
        if os.path.exists(temp_file_path):
          os.remove(temp_file_path)

      except (ValueError, OSError) as e:
        if (config.DEBUG):
          traceback.print_exc()

      try:

        temp_file_path = self._generate_temp_filename('mrc')

        with open(temp_file_path, 'wb') as fw:
          json = record.as_marc()
          fw.write(json)
          fw.close()

        resource_dict = self._create_metadata_dictionary_for_upload(dataset_metadata['id'],"N/A",temp_file_path,dataset_metadata['title'],'Record [MARC21]','mrc')
        ckanapi_utils.create_resource_with_file_upload(resource_dict)
        if os.path.exists(temp_file_path):
          os.remove(temp_file_path)

      except (ValueError, OSError) as e:
        if (config.DEBUG):
          traceback.print_exc()

      if record.get_fields('856'):
        for f in record.get_fields('856'):

          if f['u'] is not None:
            resource_url = f['u']

            try:

              urllib.urlopen(resource_url)
              resource_dict = self._create_metadata_dictionary_for_resource(dataset_metadata['id'],resource_url,dataset_metadata['title'],'Extra material [Link]','html')
              created_resource = ckanapi_utils.create_resource(resource_dict)

            except (UnicodeError):
              if (config.DEBUG):
                traceback.print_exc()

            except (IOError, AttributeError) as e:

              try:

                temp_file_path = self._generate_temp_filename('pdf')
                ngl_utils.download_file(resource_url,temp_file_path)
                resource_dict = self._create_metadata_dictionary_for_upload(dataset_metadata['id'],"N/A",temp_file_path,dataset_metadata['title'],'Extra material [PDF]','pdf')
                ckanapi_utils.create_resource_with_file_upload(resource_dict)
                if os.path.exists(temp_file_path):
                  os.remove(temp_file_path)

              except (ValueError, OSError, TypeError) as e:
                if (config.DEBUG):
                  traceback.print_exc()

    print("COMPLETED import_marc21_library_records")

    return True

  # Import GeoServer layers into CKAN
  # Using GeoServer's REST API. Obtain a list of the layers, pull their metadata
  # along with GEOJson representation (if available) and link to OpenLayers and
  # upload the information to CKAN creating a new dataset or modifying it in case
  # it already exists.
  def import_from_geoserver(self,geoserver_utils,ckanapi_utils,config):

    log = logging.getLogger(__name__)

    try:
      organization = config.GEOSERVER_MAP['organization']
      orga = ckanapi_utils.get_organization_id_from_name(organization)
    except ckanapi.NotFound:
      print("Organization " + organization + " not found, please check config")
      return False

    taxonomy_tags = ckanapi_utils.get_all_tags_from_tag_vocabulary({'vocabulary_id':config.TAXONOMY_TAG_VOCAB})

    # Use geoserver_utils to get a dictionary with the layers
    response_dict = geoserver_utils.get_layers()
    context = etree.iterparse(io.BytesIO(response_dict), events=('end', ))
    context = iter(context)
    root = context.next()[1]
    counter = 0

    for event, elem in context:

      if event == "end" and elem.tag == "layer":

        if (elem.find('name') is not None):
          name = elem.find('name').text
          feature_namespace = name.split(":")[0]
          feature_name = name.split(":")[1]
          feature_title = self._prettify_name(feature_name)

        try:

          # Create dictionary with data to create/update datasets on CKAN
          dataset_metadata = self._map_geoserver_feature_to_ckan_dataset(feature_namespace,feature_name,feature_title,taxonomy_tags,config)
          dataset_metadata = self._set_extras_from_layer_to_ckan_dataset_dict(dataset_metadata,config)

          # Get id of organization from its name and add it to dataset_metadata
          dataset_metadata['id'] = ''
          dataset_metadata['owner_org'] = orga['id']
          dataset_metadata['groups']	= config.GEOSERVER_MAP['groups']

          if (config.DEBUG):
            print(dataset_metadata)

          try:

            # Search for the dataset
            response = ckanapi_utils.get_package_contents(dataset_metadata['name'].lower())

            # if SKIP_EXISTING is set, skip this one
            if config.SKIP_EXISTING:
              print("Dataset skipped ",dataset_metadata['id'],dataset_metadata['name'])
              continue

            # Lets modify it
            modified_dataset = ckanapi_utils.update_package(dataset_metadata)
            dataset_metadata['id'] = modified_dataset['id']

            print("Dataset modified ",modified_dataset['id'],modified_dataset['title'])

          except (ckanapi.SearchError,ckanapi.NotFound) as e1:

            # Lets create it
            created_dataset = ckanapi_utils.create_package(dataset_metadata)
            dataset_metadata['id'] = created_dataset['id']

            print("Dataset created ",created_dataset['id'],created_dataset['title'])

          ol_url = self._generate_wms_download_url(geoserver_utils.geoserver_url,feature_namespace,feature_name,'application/openlayers')
          resource_dict = self._create_metadata_dictionary_for_resource(dataset_metadata['id'],ol_url,dataset_metadata['title'],'Data representation [Open Layers]','html')
          created_resource = ckanapi_utils.create_resource(resource_dict)

          ol_url = self._generate_wms_download_url(geoserver_utils.geoserver_url,feature_namespace,feature_name,'application/vnd.google-earth.kml')
          resource_dict = self._create_metadata_dictionary_for_resource(dataset_metadata['id'],ol_url,dataset_metadata['title'],'Data representation KML]','kml')
          created_resource = ckanapi_utils.create_resource(resource_dict)

          try:

            temp_file_path = self._generate_temp_filename('geojson')
            geojson_url = self._generate_ows_download_url(geoserver_utils.geoserver_url,feature_namespace,feature_name,'json')
            geojson_file = geoserver_utils.download_file(geojson_url,temp_file_path)

            resource_dict = self._create_metadata_dictionary_for_upload(dataset_metadata['id'],geojson_url,temp_file_path,dataset_metadata['title'],'Data representation [Geojson]','geojson')
            ckanapi_utils.create_resource_with_file_upload(resource_dict)
            if os.path.exists(temp_file_path):
              os.remove(temp_file_path)

          except (urllib2.HTTPError, ValueError) as e3:
            if (config.DEBUG):
              traceback.print_exc()

          try:

            temp_file_path = self._generate_temp_filename('csv')
            csv_url = self._generate_ows_download_url(geoserver_utils.geoserver_url,feature_namespace,feature_name,'csv')
            csv_file = geoserver_utils.download_file(csv_url,temp_file_path)

            resource_dict = self._create_metadata_dictionary_for_upload(dataset_metadata['id'],csv_file,temp_file_path,dataset_metadata['title'],'Data representation [CSV]','csv')
            ckanapi_utils.create_resource_with_file_upload(resource_dict)
            if os.path.exists(temp_file_path):
              os.remove(temp_file_path)

          except (urllib2.HTTPError, ValueError) as e3:
            if (config.DEBUG):
              traceback.print_exc()

          file_formats = [
            {'mime':'image/png','ext':'png'},
            {'mime':'application/pdf','ext':'pdf'}
          ]

          for file_format in file_formats:

            try:

              temp_file_path = self._generate_temp_filename(file_format['ext'])

              file_url = self._generate_wms_download_url(geoserver_utils.geoserver_url,feature_namespace,feature_name,file_format['mime'])
              file_contents = geoserver_utils.download_file(file_url,temp_file_path)

              resource_dict = self._create_metadata_dictionary_for_upload(dataset_metadata['id'],file_url,temp_file_path,dataset_metadata['title'],"Data representation ["+file_format['ext']+"]",file_format['ext'])
              ckanapi_utils.create_resource_with_file_upload(resource_dict)
              if os.path.exists(temp_file_path):
                os.remove(temp_file_path)

            except (urllib2.HTTPError, ValueError) as e3:
              if (config.DEBUG):
                traceback.print_exc()

        except ckanapi.NotFound:
          if (config.DEBUG):
            traceback.print_exc()

        except (KeyError,ValueError) as e2:
          if (config.DEBUG):
            traceback.print_exc()
          continue

    print("COMPLETED import_from_geoserver")

    return True

  # Import taxonomy translations as term_translations
  # This function pulls the translation of the taxonomy hosted on Github and
  # creates term_translation using the term_translation_update method of CKAN's Action api
  def import_taxonomy_term_translations(self,github_utils,ckanapi_utils,config):

    self.ckanapi_utils = ckanapi_utils
    self.github_utils = github_utils

    added_term_translations = []

    # Obtain JSON File from Github containing the different translations
    locales = config.SUPPORTED_LANGS
    term_lists = {}
    terms_to_import = []

    # Generate term lists for each one of the supported locales
    for locale in locales:

      # init list
      term_lists[locale] = []

      # Obtain the translation_dict from github
      translation_dict = self.github_utils.get_taxonomy_for_locale(locale)

      # Call utility function
      self._inspect_json_dict_fill_list(translation_dict,term_lists[locale])

    # Now loop through the term_lists
    for locale_origin in locales:

      # Set counter
      term_position = 0
      other_locales = list(locales)
      other_locales.remove(locale_origin)

      # Now loop through the terms of the particular locale
      for term in term_lists[locale_origin]:

        # For each term, we add a term translation of each of the other languages
        for locale_destination in other_locales:

          orig_term = term_lists[locale_origin][term_position]
          dest_term = term_lists[locale_destination][term_position]

          if orig_term != dest_term:

            # Add term translation locale_origin -> locale_destination
            params1 = {'term':self._prepare_string_for_ckan_tag_name(orig_term),'term_translation':dest_term,'lang_code':locale_destination}
            terms_to_import.append(dict(params1))

            print('Translating ' + params1['term'].encode("utf-8") + ' ('+ locale_origin + ') as ' + params1['term_translation'].encode("utf-8") + ' (' +  locale_destination + ')')

            # Add term translation locale_origin -> locale_destination
            params2 = {'term':self._prepare_string_for_ckan_tag_name(dest_term),'term_translation':orig_term,'lang_code':locale_origin}
            terms_to_import.append(dict(params2))

            print('Translating ' + params2['term'].encode("utf-8") + ' ('+ locale_destination + ') as ' + params2['term_translation'].encode("utf-8") + ' (' +  locale_origin + ')')

        term_position = term_position + 1

    count = 0
    if len(terms_to_import) > 0:
      result = self.ckanapi_utils.add_term_translation_many(dict({'data':terms_to_import}))
      count = result["success"]

    print("COMPLETED import_taxonomy_term_translations " + str(count) + " terms imported successfully.")

    return True

  # Import subject list translations as term_translations
  # This function pulls the translation of the taxonomy hosted on Github and
  # creates term_translation using the term_translation_update method of CKAN's Action api
  def import_subject_list_term_translations(self,github_utils,ckanapi_utils,config):

    self.ckanapi_utils = ckanapi_utils
    self.github_utils = github_utils

    added_term_translations = []

    # Obtain JSON File from Github containing the different translations
    locales = config.SUPPORTED_LANGS
    term_lists = {}
    terms_to_import = []

    # Generate term lists for each one of the supported locales
    for locale in locales:

      # init list
      term_lists[locale] = []

      # Obtain the translation_dict from github
      translation_dict = self.github_utils.get_subject_list_for_locale(locale)

      # Call utility function
      self._inspect_json_dict_fill_list(translation_dict,term_lists[locale])

    # Now loop through the term_lists
    for locale_origin in locales:

      # Set counter
      term_position = 0
      other_locales = list(locales)
      other_locales.remove(locale_origin)

      # Now loop through the terms of the particular locale
      for term in term_lists[locale_origin]:

        # For each term, we add a term translation of each of the other languages
        for locale_destination in other_locales:

          orig_term = term_lists[locale_origin][term_position]
          dest_term = term_lists[locale_destination][term_position]

          if orig_term != dest_term:

            # Add term translation locale_origin -> locale_destination
            params1 = {'term':self._prepare_string_for_ckan_tag_name(orig_term),'term_translation':dest_term,'lang_code':locale_destination}
            terms_to_import.append(dict(params1))

            print('Translating ' + params1['term'].encode("utf-8") + ' ('+ locale_origin + ') as ' + params1['term_translation'].encode("utf-8") + ' (' +  locale_destination + ')')

            # Add term translation locale_origin -> locale_destination
            params2 = {'term':self._prepare_string_for_ckan_tag_name(dest_term),'term_translation':orig_term,'lang_code':locale_origin}
            terms_to_import.append(dict(params2))

            print('Translating ' + params2['term'].encode("utf-8") + ' ('+ locale_destination + ') as ' + params2['term_translation'].encode("utf-8") + ' (' +  locale_origin + ')')

        term_position = term_position + 1

    count = 0
    if len(terms_to_import) > 0:
      result = self.ckanapi_utils.add_term_translation_many(dict({'data':terms_to_import}))
      count = result["success"]

    print("COMPLETED import_subject_list_term_translations " + str(count) + " terms imported successfully.")

    return True

  # Import taxonomy into tag dictionaries
  # This function pulls the json file hosted on github which represents ODM's taxonomy
  # and creates tag dictionaries in the CKAN instance
  def import_taxonomy_tag_dictionaries(self,github_utils,ckanapi_utils,config):

    self.ckanapi_utils = ckanapi_utils
    self.github_utils = github_utils

    # Obtain dictionary with taxonomy
    taxonomy_dict = self.github_utils.get_taxonomy_for_locale('en')

    try:

      # Create tag_vocabulary for taxonomy , it can happen that it has already been created
      taxonomy_tag_vocabulary = self.ckanapi_utils.show_tag_vocabulary({'id': config.TAXONOMY_TAG_VOCAB})

      # if found, reset tags in vocabulary
      taxonomy_tag_vocabulary['tags'] = list()

    except ckanapi.NotFound:

      # Create tag_vocabulary for taxonomy , it can happen that it has already been created
      params_create = dict({'name':config.TAXONOMY_TAG_VOCAB,'tags': list()})
      taxonomy_tag_vocabulary = self.ckanapi_utils.create_tag_vocabulary(params_create)

    # Loop through the json structure recursively and add tags to the vocabulary
    self._inspect_json_create_tags(taxonomy_dict,taxonomy_tag_vocabulary)

    self.ckanapi_utils.update_tag_vocabulary(taxonomy_tag_vocabulary)
    print("COMPLETED import_taxonomy_tag_dictionaries " + str(len(taxonomy_tag_vocabulary['tags'])) + ' taxonomy tags imported in taxonomy vocabulary')

    return True

  # Import subjects into tag dictionaries
  # This function pulls the json file hosted on github which represents ODM's taxonomy
  # and creates tag dictionaries in the CKAN instance
  def import_subject_list_tag_dictionaries(self,github_utils,ckanapi_utils,config):

    self.ckanapi_utils = ckanapi_utils
    self.github_utils = github_utils

    # Obtain dictionary with taxonomy
    subject_list_dict = self.github_utils.get_subject_list_for_locale('en')

    try:

      # Create tag_vocabulary for taxonomy , it can happen that it has already been created
      subject_list_tag_vocabulary = self.ckanapi_utils.show_tag_vocabulary({'id': config.SUBJECT_LIST_TAG_VOCAB})

      # if found, reset tags in vocabulary
      subject_list_tag_vocabulary['tags'] = list()

    except ckanapi.NotFound:

      # Create tag_vocabulary for taxonomy , it can happen that it has already been created
      params_create = dict({'name':config.SUBJECT_LIST_TAG_VOCAB,'tags': list()})
      subject_list_tag_vocabulary = self.ckanapi_utils.create_tag_vocabulary(params_create)

    # Loop through the json structure recursively and add tags to the vocabulary
    self._inspect_json_create_tags(subject_list_dict,subject_list_tag_vocabulary)

    self.ckanapi_utils.update_tag_vocabulary(subject_list_tag_vocabulary)
    print("COMPLETED import_taxonomy_tag_dictionaries " + str(len(subject_list_tag_vocabulary['tags'])) + ' taxonomy tags imported in taxonomy vocabulary')

    return True

  def _map_xml_item_to_ckan_dataset_dict(self,orga,root,elem,config_item,taxonomy_tags,config):

    params_dict = {}
    params_dict['owner_org'] = orga['id']
    params_dict['groups'] = config_item['groups']
    params_dict['title'] = elem.find('title').text
    params_dict['name'] = elem.find('wp:post_name',root.nsmap).text
    if (params_dict['name'] is None):
      params_dict['name'] = str(uuid.uuid4())
    params_dict['name'] = self._prepare_string_for_ckan_name(params_dict['name'])
    params_dict['author'] = config.IMPORTER_NAME
    params_dict['author_email'] = config.IMPORTER_EMAIL
    params_dict['state'] = 'active'
    params_dict['notes'] = elem.find('content:encoded',root.nsmap).text


    tags = []
    for category in elem.findall('category'):
      category_name = self._prepare_string_for_ckan_tag_name(category.text)
      if (category_name in taxonomy_tags):
        tags.append({'name':category_name})

    if len(tags):
      params_dict['tags'] = list(tags)

    return params_dict

  def _set_extras_from_xml_item_to_ckan_dataset_dict(self,params_dict,config_item,root,elem,config):

    # Add Spatial Range
    params_dict['odm_spatial_range'] = 'Cambodia'

    # Add Contact
    params_dict['odm_contact'] = config.IMPORTER_NAME
    params_dict['odm_contact_email'] = config.IMPORTER_EMAIL

    # Add Language
    languages = []
    for meta in elem.findall('wp:postmeta',root.nsmap):
      meta_key = meta.find('wp:meta_key',root.nsmap).text
      if meta_key.endswith('_kh'):
        if 'kh' not in languages:
          languages.append('kh')
      if meta_key.endswith('_en'):
        if 'en' not in languages:
          languages.append('en')
    if len(languages) > 0:
      params_dict['odm_language'] = ",".join(languages)

    if (elem.find('pubDate') is not None):
      params_dict['published_date'] = elem.find('pubDate').text
    added_meta = list()
    for meta in elem.findall('wp:postmeta',root.nsmap):
      meta_key = meta.find('wp:meta_key',root.nsmap).text
      supported_fields = odm_theme_helper.odc_fields + odm_theme_helper.metadata_fields + odm_theme_helper.library_fields
      if self._is_key_in_fields(meta_key,supported_fields):
        meta_key_copy = meta_key
        meta_value = meta.find('wp:meta_value',root.nsmap).text
        if ((meta_value is not None) and (meta_value is not "")):
          if meta_key in added_meta:
            meta_key = meta_key + '_' + str(added_meta.count(meta_key))
          params_dict[meta_key] = meta_value
          added_meta.append(meta_key_copy)

    return params_dict

  def _add_extras_urls_as_resources(self,dataset_metadata,config_item,ckanapi_utils):

    # Inspect extras, look for valid URLs or fields specified on item['field_prefixes'] and add them as resources
    supported_fields = odm_theme_helper.odc_fields + odm_theme_helper.metadata_fields + odm_theme_helper.library_fields
    for  field in supported_fields:
      extra = field[0]
      if extra in dataset_metadata:
        add_resource = False
        field_key = field[0]
        field_value = dataset_metadata[extra]
        resource_format = 'html'
        if self._is_valid_url(field_value):
          add_resource = True
          resource_format = 'html'
        else:
          for field_prefix in config_item['field_prefixes']:
            if field_key == field_prefix['field']:
              field_value = field_prefix['prefix'] + field_value
              add_resource = True
              resource_format = self._get_ext(field_value)

        if add_resource:

          try:

            temp_file_path = self._generate_temp_filename(self._get_ext(field_value))
            self._download_file(field_value,temp_file_path)
            resource_dict = self._create_metadata_dictionary_for_upload(dataset_metadata['id'],"N/A",temp_file_path,dataset_metadata['title'],self._capitalize_name(field_key),self._get_ext(field_value))
            created_resource = ckanapi_utils.create_resource_with_file_upload(resource_dict)

          except (UnicodeError):
              traceback.print_exc()

  def _map_record_to_ckan_dataset_dict(self,record,config):

    # First, extract the information from the layer (Title, Abstract, Tags)
    params_dict = {}
    params_dict['id'] = ''
    params_dict['state'] = 'active'

    params_dict['author'] = config.IMPORTER_NAME
    params_dict['author_email'] = config.IMPORTER_EMAIL

    try:

      if record.title():
        params_dict['title'] = record.title()

      if (record.title()) and (record.title() != ''):
        params_dict['name'] = self._prepare_string_for_ckan_name(str(uuid.uuid5(uuid.NAMESPACE_DNS, record.title().encode('utf-8'))))
      elif record.isbn() and (record.isbn() != ''):
        params_dict['name'] = self._prepare_string_for_ckan_name(record.isbn())
      else:
        return None

      if (not record.title()) or (record.title() == ''):
        params_dict['title'] = params_dict['name']

    except UnicodeEncodeError as e:
      if (config.DEBUG):
        traceback.print_exc()

    # Summary
    if record['520']:
      params_dict['notes'] = unicode(record['520'].value())

    return params_dict

  def _set_extras_from_record_to_ckan_dataset_dict(self,dataset_metadata,record,config):

    if dataset_metadata is None:
      return None

    # Spatial range
    dataset_metadata['odm_spatial_range'] = 'Cambodia'

    # Contact
    dataset_metadata['odm_contact'] = config.IMPORTER_NAME
    dataset_metadata['odm_contact_email'] = config.IMPORTER_EMAIL

    # Language
    dataset_metadata['odm_language'] = 'en'

    # ISBN
    if record.isbn():
      dataset_metadata['marc21_020'] = unicode(record.isbn())
    # ISSN
    if record['022']:
      dataset_metadata['marc21_022'] = unicode(record['022'].value())
    # Classification
    if record['084']:
      dataset_metadata['marc21_084'] = unicode(record['084'].value())
    # Author
    if record['100']:
      dataset_metadata['marc21_100'] = unicode(record['100'].value())
    # Corporate Author
    if record['110']:
      dataset_metadata['marc21_110'] = unicode(record['110'].value())
    # Varying Form of Title
    if record['246']:
      dataset_metadata['marc21_246'] = unicode(record['246'].value())
    # Edition
    if record['250']:
      dataset_metadata['marc21_250'] = unicode(record['250'].value())
    # Publication Name
    if record['260'] and record['260']['a']:
      dataset_metadata['marc21_260a'] = unicode(record['260']['a'])
    # Publication Place
    if record['260'] and record['260']['b']:
      dataset_metadata['marc21_260b'] = unicode(record['260']['b'])
    # Publication Date
    if record['260'] and record['260']['c']:
      dataset_metadata['marc21_260c'] = unicode(record['260']['c'])
    # Pagination
    if record.physicaldescription():
      dataset_metadata['marc21_300'] = unicode(','.join([e.value() for e in record.physicaldescription()]))
    # General Note
    if record.notes():
      dataset_metadata['marc21_500'] = unicode(','.join([e.value() for e in record.notes()]))
    # Subject
    if record.subjects():
      dataset_metadata['marc21_650'] = unicode(','.join([e.value() for e in record.subjects()]))
    # Subject (Geographic Name)
    if record['651']:
      dataset_metadata['marc21_651'] = unicode(record['651'].value())
    # Keyword
    if record['653']:
      dataset_metadata['marc21_653'] = unicode(','.join([e.value() for e in record.get_fields('653')]))
    # Added entries
    if record.addedentries():
      dataset_metadata['marc21_700'] = unicode(','.join([e.value() for e in record.addedentries()]))
    # Institution
    if record['850']:
      dataset_metadata['marc21_850'] = unicode(record['850'].value())
    # Location
    if record.location():
      dataset_metadata['marc21_852'] = unicode(','.join([e.value() for e in record.location()]))

    return dataset_metadata

  def _generate_temp_filename(self,ext):
    return str(uuid.uuid4()) + "." + str(ext)

  # Utility method to compose URL to download ows resource
  def _generate_ows_download_url(self,geoserver_url,namespace,title,file_format):

    file_url = '<geoserver><namespace>/ows?service=WFS&version=1.0.0&request=GetFeature&typeName=<namespace>:<title>&srsName=EPSG:4326&outputFormat=<format>'
    file_url = file_url.replace('<geoserver>',geoserver_url)
    file_url = file_url.replace('<namespace>',namespace)
    file_url = file_url.replace('<format>',file_format)
    file_url = file_url.replace('<title>',title)
    file_url = file_url.replace('<width>','512')
    file_url = file_url.replace('<height>','429')

    return file_url

  # Utility method to compose URL to download wms resource
  def _generate_wms_download_url(self,geoserver_url,namespace,title,file_format):

    file_url = '<geoserver><namespace>/wms?service=WMS&version=1.1.0&request=GetMap&layers=<namespace>:<title>&styles=&bbox=211430.86563420878,1144585.4696614784,784623.3606298851,1625594.694892376&width=<width>&height=<height>&srs=EPSG:32648&format=<format>'
    file_url = file_url.replace('<geoserver>',geoserver_url)
    file_url = file_url.replace('<namespace>',namespace)
    file_url = file_url.replace('<format>',file_format)
    file_url = file_url.replace('<title>',title)
    file_url = file_url.replace('<width>','512')
    file_url = file_url.replace('<height>','429')

    return file_url

  # Function that creates a dictionary with the data to create resources on
  # the dataset specified by id
  def _create_metadata_dictionary_for_resource(self,dataset_id,url,name,description,format):

    params_dict = dict({})
    params_dict['package_id'] = dataset_id
    params_dict['url'] = url
    params_dict['name'] = self._prettify_name(name)
    params_dict['description'] = description
    params_dict['format'] = format

    return params_dict

  # Function that creates a dictionary with the data to create resources on
  # the dataset specified by id
  def _create_metadata_dictionary_for_upload(self,dataset_id,url,path,name,description,format):

    params_dict = dict({})
    params_dict['package_id'] = dataset_id
    params_dict['url'] = url
    params_dict['upload'] = open(path)
    params_dict['name'] = self._prettify_name(name)
    params_dict['description'] = description
    params_dict['format'] = format

    return params_dict

  # Function that maps the <feature> data structure returned by GeoServer
  # and maps it to a dictionary to be used later to create/update the
  # corresponding datasets on CKAN
  def _map_geoserver_feature_to_ckan_dataset(self,feature_namespace,feature_name,feature_title,taxonomy_tags,config):

    # First, extract the information from the layer (Title, Abstract, Tags)
    params_dict = {}

    params_dict['author'] = config.IMPORTER_NAME
    params_dict['author_email'] = config.IMPORTER_EMAIL

    # The dataset id will be set when we find or create it
    params_dict['state'] = 'active'

    # Extract title (Mandatory)
    params_dict['title'] = feature_title

    # Extract name (Mandatory, lowcase and without characters except _-')
    params_dict['name'] = self._prepare_string_for_ckan_name(feature_name)

    # Notes / Description / Abstract
    params_dict['notes'] = 'Imported Geoserver Layer: '+params_dict['title'] + '.'

    params_dict['tags'] = []
    category_name = self._prepare_string_for_ckan_tag_name(feature_namespace)
    if (config.DEBUG):
      print(category_name)
    if (category_name in taxonomy_tags):
      params_dict['tags'].append({'name':category_name})

    return params_dict

  def _set_extras_from_layer_to_ckan_dataset_dict(self,dataset_metadata,config):

    # Spatial range
    dataset_metadata['odm_spatial_range'] = 'Cambodia'

    # Contact
    dataset_metadata['odm_contact'] = config.IMPORTER_NAME
    dataset_metadata['odm_contact_email'] = config.IMPORTER_EMAIL

    # Add Language
    if dataset_metadata['name'].endswith('_kh'):
      dataset_metadata['odm_language'] = 'kh'
    else:
      dataset_metadata['odm_language'] = 'en'

    return dataset_metadata

  # Utilty function that goes through the tree structure of a dictionary recursively
  # and appends them to taxonomy_tag_vocabulary for them to be inserted later
  def _inspect_json_create_tags(self,inspected_dict,taxonomy_tag_vocabulary):

    if 'children' in inspected_dict.keys():

        # Has children
        for child in inspected_dict['children']:

          # Iterate deeper
          self._inspect_json_create_tags(child,taxonomy_tag_vocabulary)

    else:

      # Is a leaf, create tag and assign to taxonomy vocabulary
      tag_name = self._prepare_string_for_ckan_tag_name(inspected_dict['name'])
      tag = {'name': tag_name}

      # Avoid duplicates
      tag_exists = False
      for existing_tag in taxonomy_tag_vocabulary['tags']:
        if ( existing_tag['name'] == tag_name):
          tag_exists = True

      if (tag_exists == False):
        taxonomy_tag_vocabulary['tags'].append(dict(tag))

  # Utilty function that goes through the tree structure of a inspected_dict recursively
  # collecting the "name" attributes of all the nodes on the term_list object specified by
  # parameter.
  # TODO: What to do when a dictionary already exists with a certain name and another
  # one with the same name needs to be created?
  def _inspect_json_dict_fill_list(self,inspected_dict,term_list):

    # Append name to term_list from each of the nodes, indepently of whether they are node or leaf
    term_list.append(inspected_dict['name'])

    # Then try to go deeper recursively
    if 'children' in inspected_dict.keys():

      # Has children
      for child in inspected_dict['children']:

        # Iterate deeper
        self._inspect_json_dict_fill_list(child,term_list)

  def _is_key_in_fields(self,key,fields):

    for field in fields:
      if key == field[0]:
        return True

    return False

  def _cap_string(self,string, length):
    return string if len(string)<=length else string[0:length-1]

  def _prepare_string_for_ckan_tag_name(self,string):
    string = ''.join(ch for ch in string if (ch.isalnum() or ch == '_' or ch == '-' or ch == ' ' ))
    #string = string.replace(' ','_').lower()
    string = self._cap_string(string,100)
    return string

  def _prepare_string_for_ckan_name(self,string):
    string = ''.join(ch for ch in string if (ch.isalnum() or ch == '_' or ch == '-'))
    string = string.replace(' ','_').lower()
    string = self._cap_string(string,100)
    return string

  def _prettify_name(self,string):
    return string.replace('_',' ').encode('utf-8')

  def _capitalize_name(self,string):
    return self._prettify_name(string.title())

  def _is_unicode(self,string):
    return isinstance(string, unicode)

  def _is_valid_url(self,url):
    regex = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return url is not None and regex.search(url)

  def _contains_non_utf8(self,string):
    try:
      string.decode('UTF-8', 'strict')
    except UnicodeDecodeError:
      return True

    return False

  def _get_ext(self,url):
    parsed = urlparse.urlparse(url)
    root, ext = os.path.splitext(parsed.path)
    return ext[1:]  # or ext[1:] if you don't want the leading '.'

  def _download_file(self,url,dest):
    urllib.urlretrieve(url,dest)
