ckanext-odm_theme
=================

[![Build Status](https://travis-ci.org/OpenDevelopmentMekong/ckanext-odm_theme.svg?branch=master)](https://travis-ci.org/OpenDevelopmentMekong/ckanext-odm_theme)

A CKAN extension which provides with template files replacing CKAN's default UI and adding some javascript logic.

# Installation

In order to install this CKAN Extension:

  * clone the ckanext-odm_theme folder to the src/ folder in the target CKAN instance.

 ```
 git clone https://github.com/OpenDevelopmentMekong/ckanext-odm_theme.git
 cd ckanext-odm_theme
 ```

 * Install dependencies
 <code>pip install -r requirements.txt</code>

 * Setup plugin
 <code>python setup.py develop</code>

# Testing

  In order to test it:

  * Make sure that test.ini is properly configured, specially noting the values of:
    * **solr_url**
    * **who.config_file**

  * Run tests:
    <code>nosetests --ckan --with-pylons=test.ini ckanext/odm_theme/tests/</code>

# Copyright and License

This material is copyright (c) 2014-2015 East-West Management Institute, Inc. (EWMI).

It is open and licensed under the GNU Affero General Public License (AGPL) v3.0 whose full text may be found at:

http://www.fsf.org/licensing/licenses/agpl-3.0.html
