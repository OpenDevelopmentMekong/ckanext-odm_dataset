from setuptools import setup, find_packages
import sys, os

version = '1.2.0'

setup(
    name='ckanext-odm_theme',
    version=version,
    description="ODM CKAN's theme extension",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Alex Corbi',
    author_email='mail@lifeformapps.com',
    url='http://www.lifeformapps.com',
    license='',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.odm_theme'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        odm_theme=ckanext.odm_theme.plugin:OdmThemePlugin
    ''',
)
