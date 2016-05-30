import datetime
import json
from pylons import config
import rdflib
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF, XSD, SKOS, RDFS
from geomet import wkt, InvalidGeoJSONException
from ckan.plugins import toolkit
from ckanext.dcat.utils import resource_uri, publisher_uri_from_dataset_dict
from ckanext.dcat.profiles import RDFProfile
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "lib"))
import odm_rdf_helper
import logging

DCT = Namespace('http://purl.org/dc/terms/')
GN = Namespace('http://www.geonames.org/ontology#')
DCAT = Namespace('http://www.w3.org/ns/dcat#')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
SKOS = Namespace('https://www.w3.org/2009/08/skos-reference/skos.html#')

log = logging.getLogger(__name__)

class ODMDCATBasicProfileDataset(RDFProfile):
  '''
  An RDF profile exposing metadata using standard vocabularies

  More information and specification:

  https://joinup.ec.europa.eu/asset/dcat_application_profile

  '''

  def parse_dataset(self, dataset_dict, dataset_ref):

    # This method does not need to be implemented until Harvesters are needed
    return super(ODMDCATBasicProfileDataset, self).parse_dataset(dataset_dict, dataset_ref)

  def graph_from_dataset(self, dataset_dict, dataset_ref):

    log.debug("ODMDCATBasicProfileDataset graph_from_dataset")

    g = self.g

    namespaces = odm_rdf_helper.get_namespaces_by_dataset_type(dataset_dict['type'])

    for prefix, namespace in namespaces.iteritems():
      g.bind(prefix, namespace)

    g.add((dataset_ref, DCT.identifier, Literal(dataset_dict.get('id'))))
    g.add((dataset_ref, DCT.type, Literal(dataset_dict.get('type', 'dataset'))))
    g.add((dataset_ref, RDF.type, DCAT.Dataset))

    raw_triples = odm_rdf_helper.get_triples_by_dataset_type(dataset_ref,dataset_dict,dataset_dict['type'])

    for raw_triple in raw_triples:
      triples = odm_rdf_helper.split_multilingual_object_into_triples(raw_triple)
      for triple in triples:
        g.add(triple)

    #license
    license = URIRef(dataset_dict.get('license_url'))
    g.add((license, DCT.title, Literal(dataset_dict.get('license_title'))))
    g.add((dataset_ref, DCT.license, license))

    # odm_spatial_range
    for item in dataset_dict.get('odm_spatial_range'):
      g.add((dataset_ref, GN.countrycode, Literal(item.upper())))

    #taxonomy
    for term in dataset_dict.get('taxonomy'):
      matches = odm_rdf_helper.map_internal_to_standard_taxonomic_term(term)

      if isinstance(matches,basestring):
        g.add((dataset_ref, FOAF.topic, Literal(matches)))
      else:
        node = BNode()
        if 'exact_match' in matches:
          node = URIRef(matches['exact_match'])
        if 'broad_match' in matches:
          for broad_match in matches['broad_match']:
            g.add((node,SKOS.broadMatch, URIRef(broad_match)))

        g.add((node,DCT.title, Literal(term)))
        g.add((dataset_ref, FOAF.topic, node))

    #  Lists
    items = [
      ('odm_language', DCT.language, None)
    ]
    self._add_list_triples_from_dict(dataset_dict, dataset_ref, items)

    # Dates
    items = odm_rdf_helper.get_date_fields_by_dataset_type(dataset_dict['type'])
    self._add_date_triples_from_dict(dataset_dict, dataset_ref, items)

    # Resources
    for resource_dict in dataset_dict.get('resources', []):

      resource = URIRef(resource_uri(resource_dict))
      g.add((dataset_ref, DCAT.Resources, resource))
      g.add((resource, RDF.type, DCAT.Resource))

      items = [
        ('name', DCT.title, None),
        ('description', DCT.description, None)
      ]
      self._add_triples_from_dict(resource_dict, resource, items)

      #  Lists
      items = [
        ('odm_language', DCT.language, None)
      ]
      self._add_list_triples_from_dict(resource_dict, resource, items)

      # Format
      if '/' in resource_dict.get('format', ''):
        g.add((resource, DCAT.mediaType,
               Literal(resource_dict['format'])))
      else:
        if resource_dict.get('format'):
          g.add((resource, DCT['format'],
                 Literal(resource_dict['format'])))

        if resource_dict.get('mimetype'):
          g.add((resource, DCAT.mediaType,
                 Literal(resource_dict['mimetype'])))

      # URL
      url = resource_dict.get('url')
      download_url = resource_dict.get('download_url')
      if download_url:
        g.add((resource, DCAT.downloadURL, Literal(download_url)))
      if (url and not download_url) or (url and url != download_url):
        g.add((resource, DCAT.accessURL, URIRef(url)))

  def graph_from_catalog(self, catalog_dict, catalog_ref):

    log.debug("ODMDCATBasicProfileDataset graph_from_catalog")

    g = self.g

    for prefix, namespace in namespaces.iteritems():
      g.bind(prefix, namespace)

    g.add((catalog_ref, RDF.type, DCAT.Catalog))

    # Basic fields
    items = [
      ('title', DCT.title, config.get('ckan.site_title')),
      ('description', DCT.description, config.get('ckan.site_description')),
      ('homepage', FOAF.homepage, config.get('ckan.site_url')),
      ('language', DCT.language, config.get('ckan.locale_default', 'en')),
    ]
    for item in items:
      key, predicate, fallback = item
      if catalog_dict:
        value = catalog_dict.get(key, fallback)
      else:
        value = fallback
      if value:
        g.add((catalog_ref, predicate, Literal(value)))

    # Dates
    modified = self._last_catalog_modification()
    if modified:
      self._add_date_triple(catalog_ref, DCT.modified, modified)
