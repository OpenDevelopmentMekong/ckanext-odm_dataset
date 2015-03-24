# -*- coding: utf-8 -*-
''' Module containing config variables for scripts, please rename to odm_theme_config.py

'''

#DEBUG
DEBUG = False

#Control logic
SKIP_N_DATASETS = 0
SKIP_EXISTING = False

#Common
CKAN_URL='URL'
CKAN_APIKEY='KEY'

# Geoserver
GEOSERVER_URL='URL'
GEOSERVER_AUTH='AUTH'
GEOSERVER_MAP={'ontology':'*','organization':'cambodia-organization','groups':[{'name':'maps-group'},{'name':'cambodia-group'}]}

# NewGenLib
NGL_URL=''
NGL_MAP={'ontology':'*','organization':'odm-library','groups':[{'name':'library-group'},{'name':'cambodia-group'}]}

# ODC
ODC_MAP=[{'ontology':'ODC/laws','organization':'cambodia-organization','groups':[{'name':'laws-group'},{'name':'cambodia-group'}],'field_prefixes':[{'field':'file_name_kh','prefix':'http://cambodia.opendevelopmentmekong.net/wp-content/blogs.dir/2/download/law/'},{'field':'file_name_en','prefix':'http://cambodia.opendevelopmentmekong.net/wp-content/blogs.dir/2/download/law/'}]}]

# Insert initial data
ODM_ADMINS_PASS='odmadmin'

# Delete datasets in group
DELETE_GROUP_NAME='news-group'
DELETE_LIMIT=500

# Tag vocabularies
TAXONOMY_TAG_VOCAB='taxonomy'
