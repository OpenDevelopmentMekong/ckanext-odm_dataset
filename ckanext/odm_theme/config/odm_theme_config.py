# -*- coding: utf-8 -*-
''' Module containing config variables for scripts, please rename to odm_theme_config.py

'''

#DEBUG
DEBUG = True

#Control logic
SKIP_N_DATASETS = 0
SKIP_EXISTING = False

#Common
CKAN_URL='http://127.0.0.1:8081'
CKAN_APIKEY='c839d15d-4f86-4352-9f18-6df80516e4b1'

# Geoserver
GEOSERVER_URL='http://geoserver.opendevelopmentmekong.net/geoserver/'
GEOSERVER_AUTH='Basic b2RjX3Rlc3Q6QCMlZmtkT3BlODduZEF0YQ=='
GEOSERVER_MAP={'ontology':'*','organization':'cambodia-organization','groups':[{'name':'maps-group'},{'name':'cambodia-group'}]}

# NewGenLib
NGL_URL='http://library.opendevelopmentcambodia.net:8080/newgenlibctxt/'
NGL_MAP={'ontology':'*','organization':'odm-library','groups':[{'name':'library-group'},{'name':'cambodia-group'}]}

# ODC
ODC_MAP=[{'ontology':'ODC/laws','organization':'cambodia-organization','groups':[{'name':'laws-group'},{'name':'cambodia-group'}],'field_prefixes':[{'field':'file_name_kh','prefix':'http://cambodia.opendevelopmentmekong.net/wp-content/blogs.dir/2/download/law/'},{'field':'file_name_en','prefix':'http://cambodia.opendevelopmentmekong.net/wp-content/blogs.dir/2/download/law/'}]}]
#,'field_prefixes':[{'field':'file_name_kh','prefix':'http://cambodia.opendevelopmentmekong.net/wp-content/blogs.dir/2/download/law/'},{'field':'file_name_en','prefix':'http://cambodia.opendevelopmentmekong.net/wp-content/blogs.dir/2/download/law/'}]
ODC_IMPORTER_NAME = 'ODM Importer'
ODC_IMPORTER_EMAIL = 'info@opendevcam.net'

# Insert initial data
ODM_ADMINS_PASS='odmadmin'

# Delete datasets in group
DELETE_GROUP_NAME='laws-group'
DELETE_LIMIT=100

# Tag vocabularies
TAXONOMY_TAG_VOCAB='taxonomy'
