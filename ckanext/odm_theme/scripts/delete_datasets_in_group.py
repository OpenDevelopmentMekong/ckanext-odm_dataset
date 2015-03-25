#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Delete datasets in group
# This script deletes all the datasets assigned to a group.

# NOTE: This script has to be run within a virtual environment!!!
# Do not forget to set the correct API Key while initialising RealCkanApi
# . /usr/lib/ckan/default/bin/activate

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
import ckanapi_utils
import ckan
import ckanapi

try:
  sys.path.append(os.path.join(os.path.dirname(__file__), "../config"))
  import odm_theme_config as config
except ImportError as e:
  sys.exit("Please make sure that you have renamed and initialized odm_theme_config.sample.py")

ckanapiutils = ckanapi_utils.RealCkanApi(config)

try:

  orga_datasets = {}
  params = {'id':config.DELETE_GROUP_NAME,'limit':config.DELETE_LIMIT}
  datasets = ckanapiutils.get_packages_in_group(params)

  for dataset in datasets:
    if dataset['owner_org'] not in orga_datasets.keys():
      orga_datasets[dataset['owner_org']] = []
    orga_datasets[dataset['owner_org']].append(dataset['id'])
    if (config.DEBUG):
      print(orga_datasets)

  for orga_id in orga_datasets.keys():
    params = {'datasets':orga_datasets[orga_id],'org_id':orga_id}
    ckanapiutils.delete_packages_list(params)

except ckanapi.NotFound:

  print 'Group ' + config.DELETE_GROUP_NAME + ' not found'

print("COMPLETED delete_datasets_in_group")
