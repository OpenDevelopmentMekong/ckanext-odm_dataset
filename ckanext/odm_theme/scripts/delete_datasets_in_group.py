#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Delete datasets in group
# This script deletes all the datasets assigned to a group.

# NOTE: This script has to be run within a virtual environment!!!
# Do not forget to set the correct API Key while initialising RealCkanApi
# . /usr/lib/ckan/default/bin/activate

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../utils'))
import ckanapi_utils
from odm_importer import ODMImporter

try:
  sys.path.append(os.path.join(os.path.dirname(__file__), "../config"))
  import odm_theme_config as config
except ImportError as e:
  sys.exit("Please make sure that you have renamed and initialized odm_theme_config.sample.py")

ckanapiutils = ckanapi_utils.RealCkanApi(config)

importer = ODMImporter()
importer.delete_datasets_in_group(ckanapiutils,config)
