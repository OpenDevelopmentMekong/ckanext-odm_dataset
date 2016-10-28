from setuptools import setup, find_packages
import sys, os

version = '2.0.3'

setup(
    name='ckanext-odm_dataset',
    version=version,
    description="OD Mekong CKAN's extension for datasets",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Alex Corbi',
    author_email='mail@lifeformapps.com',
    url='http://www.lifeformapps.com',
    license='AGPL3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        odm_dataset=ckanext.odm_dataset.plugin:OdmDatasetPlugin

        [ckan.rdf.profiles]
        odm_dcat_dataset=ckanext.odm_dataset.odm_dataset_profiles:ODMDCATBasicProfileDataset
    ''',
)
