#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Import taxonomy term translations
# This script imports multi-lingual taxonomy from https://github.com/OpenDevelopmentMekong/odm-localization
# and stores term translations.

# NOTE: This script has to be run within a virtual environment!!!
# Do not forget to set the correct API Key while initialising RealCkanApi
# . /usr/lib/ckan/default/bin/activate

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
import ckanapi_utils
import github_utils
from odm_importer import ODMImporter

try:
  sys.path.append(os.path.join(os.path.dirname(__file__), "../config"))
  import odm_theme_config as config
except ImportError as e:
  sys.exit("Please make sure that you have renamed and initialized odm_theme_config.sample.py")

githubutils = github_utils.RealGithubApi()
ckanapiutils = ckanapi_utils.RealCkanApi(config)

importer = ODMImporter()
importer.import_taxonomy_term_translations(githubutils,ckanapiutils,config)
