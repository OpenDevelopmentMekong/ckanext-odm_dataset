#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Insert initial ODM Data
# This script initialises the CKAN Instance with a list of organizations, groups and users:
# organizations (OD Mekong Cambodia, OD Mekong Laos, OD Mekong Thailand, OD Mekong Vietnam, OD Mekong Myanmar)
# Groups (Cambodia, Laos, Thailand, Vietnam, Myanmar)
# Users (odmcambodia, odmlaos, odmthailand, odmvietnam, odmmyanmar)

# NOTE: This script has to be run within a virtual environment!!!
# Do not forget to set the correct API Key while initialising RealCkanApi
# . /usr/lib/ckan/default/bin/activate

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "../utils"))
import ckanapi_utils
import ckan

try:
  sys.path.append(os.path.join(os.path.dirname(__file__), "../config"))
  import odm_theme_config as config
except ImportError as e:
  sys.exit("Please make sure that you have renamed and initialized odm_theme_config.sample.py")

ckanapiutils = ckanapi_utils.RealCkanApi(config)

# Add Users
for user in [{'name':'odmmekong','email':'mekong@opendevelopmentmekong.net','pass':config.ODM_ADMINS_PASS,'desc':'OD Mekong Mekong admin'},
              {'name':'odmcambodia','email':'cambodia@opendevelopmentmekong.net','pass':config.ODM_ADMINS_PASS,'desc':'OD Mekong Cambodia admin'},
              {'name':'odmlaos','email':'laos@opendevelopmentmekong.net','pass':config.ODM_ADMINS_PASS,'desc':'OD Mekong Laos admin'},
              {'name':'odmthailand','email':'thailand@opendevelopmentmekong.net','pass':config.ODM_ADMINS_PASS,'desc':'OD Mekong Thailand admin'},
              {'name':'odmvietnam','email':'vietnam@opendevelopmentmekong.net','pass':config.ODM_ADMINS_PASS,'desc':'OD Mekong Vietnam admin'},
              {'name':'odmmyanmar','email':'myanmar@opendevelopmentmekong.net','pass':config.ODM_ADMINS_PASS,'desc':'OD Mekong Myanmar admin'}]:

  try:

    ckanapiutils.add_user(user['name'],user['email'],user['pass'],user['desc'])

  except ckan.logic.ValidationError:

    print 'User ' + user['name'] + ' already added'

# Add organizations
for organization in [{'name':'mekong-organization','title':'Open Development Mekong','desc':'OD Mekong regional organization'},
                      {'name':'cambodia-organization','title':'Open Development Cambodia','desc':'Cambodia-based organizations and partners'},
                      {'name':'laos-organization','title':'Open Development Laos','desc':'Laos-based organizations and partners'},
                      {'name':'thailand-organization','title':'Open Development Thailand','desc':'Thailand-based organizations and partners'},
                      {'name':'vietnam-organization','title':'Open Development Vietnam','desc':'Vietnam-based organizations and partners'},
                      {'name':'myanmar-organization','title':'Open Development Myanmar','desc':'Myanmar-based organizations and partners'}]:

  try:

    ckanapiutils.add_organization(organization['name'],organization['title'],organization['desc'])

  except ckan.logic.ValidationError:

    print 'Organization ' + organization['name'] + ' already added'

# Add admins to organizations
for role in [{'organization':'mekong-organization','user':'odmmekong','role':'admin'},
              {'organization':'cambodia-organization','user':'odmcambodia','role':'admin'},
              {'organization':'laos-organization','user':'odmlaos','role':'admin'},
              {'organization':'thailand-organization','user':'odmthailand','role':'admin'},
              {'organization':'vietnam-organization','user':'odmvietnam','role':'admin'},
              {'organization':'myanmar-organization','user':'odmmyanmar','role':'admin'}]:

  try:

    ckanapiutils.add_admin_to_organization(role['organization'],role['user'],role['role'])

  except ckan.logic.ValidationError:

    print 'User ' + role['user'] + ' already admined'

# Add Groups
for group in [{'name':'maps-group','title':'Maps','desc':'Group for Maps'},
              {'name':'news-group','title':'News','desc':'Group for News'},
              {'name':'laws-group','title':'Laws','desc':'Group for Laws'}]:

  # Add groups
  try:

    ckanapiutils.add_group(group['name'],group['title'],group['desc'])

  except ckan.logic.ValidationError:

    print 'Group ' + group['name'] + ' already added'
