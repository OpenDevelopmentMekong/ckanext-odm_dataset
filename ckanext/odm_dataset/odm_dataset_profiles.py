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
import logging

log = logging.getLogger(__name__)

DCT = Namespace("http://purl.org/dc/terms/")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
ADMS = Namespace("http://www.w3.org/ns/adms#")
VCARD = Namespace("http://www.w3.org/2006/vcard/ns#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SCHEMA = Namespace('http://schema.org/')
TIME = Namespace('http://www.w3.org/2006/time')
LOCN = Namespace('http://www.w3.org/ns/locn#')
GSP = Namespace('http://www.opengis.net/ont/geosparql#')
OWL = Namespace('http://www.w3.org/2002/07/owl#')
SPDX = Namespace('http://spdx.org/rdf/terms#')
CRO = Namespace('http://rhizomik.net/ontologies/copyrightonto.owl#')
DOAP = Namespace('http://usefulinc.com/ns/doap#')
EBUCORE = Namespace('https://www.ebu.ch/metadata/ontologies/ebucore/index.html#')
DQM = Namespace('http://semwebquality.org/dqm-vocabulary/v1/dqm#')
DQ = Namespace('http://def.seegrid.csiro.au/isotc211/iso19115/2003/dataquality#')
OMN = Namespace('https://raw.githubusercontent.com/open-multinet/playground-rspecs-ontology/master/omnlib/ontologies/omn.ttl#')

GEOJSON_IMT = 'https://www.iana.org/assignments/media-types/application/vnd.geo+json'

namespaces = {
    'dct': DCT,
    'dcat': DCAT,
    'adms': ADMS,
    'vcard': VCARD,
    'foaf': FOAF,
    'schema': SCHEMA,
    'time': TIME,
    'skos': SKOS,
    'locn': LOCN,
    'gsp': GSP,
    'owl': OWL,
    'cro': CRO,
    'doap': DOAP,
    'ebucore': EBUCORE,
    'dqm': DQM,
    'dq' : DQ,
    'omn' : OMN
}


class ODMDCATBasicProfile(RDFProfile):
  '''
  An RDF profile exposing metadata using standard vocabularies

  More information and specification:

  https://joinup.ec.europa.eu/asset/dcat_application_profile

  '''

  def parse_dataset(self, dataset_dict, dataset_ref):

    # This method does not need to be implemented until Harvesters are needed
    return super(ODMDCATBasicProfile, self).parse_dataset(dataset_dict, dataset_ref)

  def graph_from_dataset(self, dataset_dict, dataset_ref):

    log.debug("ODMDCATBasicProfile graph_from_dataset")

    g = self.g

    for prefix, namespace in namespaces.iteritems():
      g.bind(prefix, namespace)

    g.add((dataset_ref, RDF.type, DCAT.Dataset))

    # Basic fields
    items = [
        ('title', DCT.title, None),
        ('notes', DCT.description, None),
        ('license', DCT.license, None),
        ('url', DCAT.landingPage, None),
        ('identifier', DCT.identifier, ['guid', 'id']),
        ('version', DOAP.version, ['dcat_version']),
        ('contact', EBUCORE.contact, None),
        #('odm_temporal_range',  , None),
        #('odm_spatial_range',  , None),
        ('odm_accuracy', DQM.accuracy, None),
        ('odm_logical_consistency', DQ.logicalConsistency, None),
        ('odm_completeness', DQ.completeness, None),
        ('odm_source', DCT.source, None),
        #('odm_metadata_reference', DCT.source, None),
        ('odm_attributes', OMN.attribute, None)
    ]
    self._add_triples_from_dict(dataset_dict, dataset_ref, items)

    # Tags
    for tag in dataset_dict.get('tags', []):
      g.add((dataset_ref, DCAT.keyword, Literal(tag['name'])))

    # Dates
    items = [
        ('odm_date_created',DCT.created, None),
        ('odm_date_uploaded',DCT.issued, None),
        ('odm_date_modified',DCT.modified, None)
    ]
    self._add_date_triples_from_dict(dataset_dict, dataset_ref, items)

    #  Lists
    items = [
        ('odm_language', DCT.language, None),
        #('odm_spatial_range', DCT.language, None)
    ]
    self._add_list_triples_from_dict(dataset_dict, dataset_ref, items)

    # Contact details
    if any([
        self._get_dataset_value(dataset_dict, 'contact_uri'),
        self._get_dataset_value(dataset_dict, 'contact_name'),
        self._get_dataset_value(dataset_dict, 'contact_email'),
        self._get_dataset_value(dataset_dict, 'maintainer'),
        self._get_dataset_value(dataset_dict, 'maintainer_email'),
        self._get_dataset_value(dataset_dict, 'author'),
        self._get_dataset_value(dataset_dict, 'author_email'),
    ]):

      contact_uri = self._get_dataset_value(dataset_dict, 'contact_uri')
      if contact_uri:
        contact_details = URIRef(contact_uri)
      else:
        contact_details = BNode()

      g.add((contact_details, RDF.type, VCARD.Organization))
      g.add((dataset_ref, DCAT.contactPoint, contact_details))

      items = [
          ('contact_name', VCARD.fn, ['maintainer', 'author']),
          ('contact_email', VCARD.hasEmail, ['maintainer_email',
                                             'author_email']),
      ]

      self._add_triples_from_dict(dataset_dict, contact_details, items)

    # Publisher
    if any([
        self._get_dataset_value(dataset_dict, 'publisher_uri'),
        self._get_dataset_value(dataset_dict, 'publisher_name'),
        dataset_dict.get('organization'),
    ]):

      publisher_uri = publisher_uri_from_dataset_dict(dataset_dict)
      if publisher_uri:
        publisher_details = URIRef(publisher_uri)
      else:
        # No organization nor publisher_uri
        publisher_details = BNode()

      g.add((publisher_details, RDF.type, FOAF.Organization))
      g.add((dataset_ref, DCT.publisher, publisher_details))

      publisher_name = self._get_dataset_value(dataset_dict, 'publisher_name')
      if not publisher_name and dataset_dict.get('organization'):
        publisher_name = dataset_dict['organization']['title']

      g.add((publisher_details, FOAF.name, Literal(publisher_name)))
      # TODO: It would make sense to fallback these to organization
      # fields but they are not in the default schema and the
      # `organization` object in the dataset_dict does not include
      # custom fields
      items = [
          ('publisher_email', FOAF.mbox, None),
          ('publisher_url', FOAF.homepage, None),
          ('publisher_type', DCT.type, None),
      ]

      self._add_triples_from_dict(dataset_dict, publisher_details, items)

    # Temporal
    start = self._get_dataset_value(dataset_dict, 'temporal_start')
    end = self._get_dataset_value(dataset_dict, 'temporal_end')
    if start or end:
      temporal_extent = BNode()

      g.add((temporal_extent, RDF.type, DCT.PeriodOfTime))
      if start:
        self._add_date_triple(temporal_extent, SCHEMA.startDate, start)
      if end:
        self._add_date_triple(temporal_extent, SCHEMA.endDate, end)
      g.add((dataset_ref, DCT.temporal, temporal_extent))

    # Spatial
    spatial_uri = self._get_dataset_value(dataset_dict, 'spatial_uri')
    spatial_text = self._get_dataset_value(dataset_dict, 'spatial_text')
    spatial_geom = self._get_dataset_value(dataset_dict, 'spatial')

    if spatial_uri or spatial_text or spatial_geom:
      if spatial_uri:
        spatial_ref = URIRef(spatial_uri)
      else:
        spatial_ref = BNode()

      g.add((spatial_ref, RDF.type, DCT.Location))
      g.add((dataset_ref, DCT.spatial, spatial_ref))

      if spatial_text:
        g.add((spatial_ref, SKOS.prefLabel, Literal(spatial_text)))

      if spatial_geom:
        # GeoJSON
        g.add((spatial_ref,
               LOCN.geometry,
               Literal(spatial_geom, datatype=GEOJSON_IMT)))
        # WKT, because GeoDCAT-AP says so
        try:
          g.add((spatial_ref,
                 LOCN.geometry,
                 Literal(wkt.dumps(json.loads(spatial_geom),
                                   decimals=4),
                         datatype=GSP.wktLiteral)))
        except (TypeError, ValueError, InvalidGeoJSONException):
          pass

    # Resources
    for resource_dict in dataset_dict.get('resources', []):

      distribution = URIRef(resource_uri(resource_dict))

      g.add((dataset_ref, DCAT.distribution, distribution))

      g.add((distribution, RDF.type, DCAT.Distribution))

      #  Simple values
      items = [
          ('name', DCT.title, None),
          ('description', DCT.description, None)
      ]

      self._add_triples_from_dict(resource_dict, distribution, items)

      #  Lists
      items = [
          ('odm_language', DCT.language, None)
      ]
      self._add_list_triples_from_dict(resource_dict, distribution, items)

      # Format
      if '/' in resource_dict.get('format', ''):
        g.add((distribution, DCAT.mediaType,
               Literal(resource_dict['format'])))
      else:
        if resource_dict.get('format'):
          g.add((distribution, DCT['format'],
                 Literal(resource_dict['format'])))

        if resource_dict.get('mimetype'):
          g.add((distribution, DCAT.mediaType,
                 Literal(resource_dict['mimetype'])))

      # URL
      url = resource_dict.get('url')
      download_url = resource_dict.get('download_url')
      if download_url:
        g.add((distribution, DCAT.downloadURL, Literal(download_url)))
      if (url and not download_url) or (url and url != download_url):
        g.add((distribution, DCAT.accessURL, Literal(url)))

  def graph_from_catalog(self, catalog_dict, catalog_ref):

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
