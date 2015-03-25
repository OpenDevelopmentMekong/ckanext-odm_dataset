#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import from Geoserver
# This script imports all Layers from GeoServer using the import_from_geoserver function
# from the ODMImporter.

# NOTE: This script has to be run within a virtual environment!!!
# Do not forget to set the correct API Key while initialising RealCkanApi
# . /usr/lib/ckan/default/bin/activate

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))
import geoserver_utils
import ckanapi_utils
from odm_importer import ODMImporter

try:
  sys.path.append(os.path.join(os.path.dirname(__file__), "../config"))
  import odm_theme_config as config
except ImportError as e:
  sys.exit("Please make sure that you have renamed and initialized odm_theme_config.sample.py")

geoserverutils = geoserver_utils.RealGeoserverRestApi(config)
ckanapiutils = ckanapi_utils.RealCkanApi(config)

importer = ODMImporter()
importer.import_from_geoserver(geoserverutils,ckanapiutils,config)
