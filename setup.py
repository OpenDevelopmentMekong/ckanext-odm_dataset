from setuptools import setup, find_packages
import sys, os

version = '1.2.0'

def gen_data_files(*dirs):
    results = []

    for src_dir in dirs:
        for root,dirs,files in os.walk(src_dir):
            results.append((root, map(lambda f:root + "/" + f, files)))
    return results

setup(
    name='ckanext-odm_theme',
    version=version,
    description="OD Mekong CKAN's theme extension",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Alex Corbi',
    author_email='mail@lifeformapps.com',
    url='http://www.lifeformapps.com',
    license='AGPL3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext', 'ckanext.odm_theme'],
    include_package_data=True,
    zip_safe=False,
    data_files = gen_data_files("odm-taxonomy"),
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        odm_theme=ckanext.odm_theme.plugin:OdmThemePlugin
    ''',
)
