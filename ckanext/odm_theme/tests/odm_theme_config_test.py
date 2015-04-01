# -*- coding: utf-8 -*-
''' Module containing config variables for scripts

'''

#DEBUG
DEBUG = True

#Control logic
SKIP_N_DATASETS = 0
SKIP_EXISTING = True

# Geoserver
GEOSERVER_MAP={'ontology':'*','organization':'cambodia-organization','groups':[{'name':'maps-group'},{'name':'cambodia-group'}]}

# NewGenLib
NGL_MAP={'ontology':'*','organization':'odm-library','groups':[{'name':'library-group'},{'name':'cambodia-group'}]}

# ODC
ODC_MAP=[{'ontology':'ODC/News','organization':'cambodia-organization','groups':[{'name':'news-group'},{'name':'laws-group'},{'name':'cambodia-group'}],'field_prefixes':[]}]

# DELETE
DELETE_MAP={'group':'laws-group','limit':500,'field_filter':{}}

# Tag vocabularies
TAXONOMY_TAG_VOCAB='taxonomy'
SUBJECT_LIST_TAG_VOCAB='subject-list'
SUPPORTED_LANGS=['en','vi','th', 'km']

# Importer infos
IMPORTER_NAME='ODM Importer'
IMPORTER_EMAIL='info@opendevmekong.net'
