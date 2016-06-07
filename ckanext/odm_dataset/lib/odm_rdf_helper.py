#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import rdflib
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF
import traceback

AGLS = Namespace('http://www.agls.gov.au/agls/terms/')
BIBO = Namespace('http://bibliontology.com/bibo/bibo.php#')
BIBFRAME = Namespace('http://id.loc.gov/ontologies/bibframe.html#')
GC = Namespace('http://www.oegov.org/core/owl/gc#')
DBPEDIA = Namespace('http://dbpedia.org/ontology/')
DCT = Namespace('http://purl.org/dc/terms/')
DCAT = Namespace('http://www.w3.org/ns/dcat#')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
MREL = Namespace('http://id.loc.gov/vocabulary/relators/')
SCHEMA = Namespace('http://schema.org/')
SPDX = Namespace('http://spdx.org/rdf/terms#')
CRO = Namespace('http://rhizomik.net/ontologies/copyrightonto.owl#')
DOAP = Namespace('http://usefulinc.com/ns/doap#')
EBUCORE = Namespace(
    'https://www.ebu.ch/metadata/ontologies/ebucore/index.html#')
DQM = Namespace('http://semwebquality.org/dqm-vocabulary/v1/dqm#')
DQ = Namespace(
    'http://def.seegrid.csiro.au/isotc211/iso19115/2003/dataquality#')
OMN = Namespace(
    'https://raw.githubusercontent.com/open-multinet/playground-rspecs-ontology/master/omnlib/ontologies/omn.ttl#')
OPUS = Namespace('http://lsdis.cs.uga.edu/projects/semdis/opus#')
PPROC = Namespace('http://contsem.unizar.es/def/sector-publico/pproc.html#')
MD = Namespace('http://def.seegrid.csiro.au/isotc211/iso19115/2003/metadata#')
GN = Namespace('http://www.geonames.org/ontology#')
SKOS = Namespace('https://www.w3.org/2009/08/skos-reference/skos.html#')
SORON = Namespace(
    'http://www.bib.uc3m.es/~fcalzada/soron/soron_content/soron#')
DC = Namespace('http://purl.org/dc/elements/1.1/')

log = logging.getLogger(__name__)


def split_multilingual_object_into_triples(triple):
  ''' Takes a triple and splits it into different localized if literal_object_value
      is multilingual (JSON object, ckanext-fluent format)
  '''
  subject, predicate, object_value = triple

  if object_value is None:
    return []
  elif isinstance(object_value, basestring):
    return[(subject, predicate, Literal(object_value))]
  else:
    triples_to_return = []
    for key, value in object_value.iteritems():
      if value:
        triples_to_return.append(
            (subject, predicate, Literal(value, lang=key)))

    return triples_to_return


def map_internal_to_standard_taxonomic_term(term):
  ''' Takes an internal taxonomic term and returns the URI of a corresponding standard term, if found
  '''

  log.debug("map_internal_to_standard_taxonomic_term: %s", term)

  mapping = {
      "Deforestration drivers": {
          "broad_matches": ["http://aims.fao.org/aos/agrovoc/c_15590"]
      },
      "Development and assistance for land tenure and land titling": {
          "broad_matches": ["http://aims.fao.org/aos/agrovoc/c_2224"]
      },
      "Environment and natural resources": {
          "broad_matches": ["http://aims.fao.org/aos/agrovoc/c_2593"]
      },
      "Agricultural management systems and technologies": {
          "broad_matches": ["http://aims.fao.org/aos/agrovoc/c_2807"]
      },
      "Fishing fisheries and aquaculture": {
          "broad_matches": ["http://aims.fao.org/aos/agrovoc/c_2934"]
      },
      "Forests and forestry": {
          "broad_matches": ["http://aims.fao.org/aos/agrovoc/c_3055"]
      },
      "Forest policy and administration": {
          "broad_matches": ["http://aims.fao.org/aos/agrovoc/c_3060"]
      },
      "Disasters": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_10391"
      },
      "Poverty policy and regulation": {
          "broad_matches": ["http://aims.fao.org/aos/agrovoc/c_6151"]
      },
      "Land sales and trades": {
          "broad_matches": ["http://aims.fao.org/aos/agrovoc/c_9a4f48b4"]
      },
      "Urban policy and administration": {
          "broad_matches": ["http://aims.fao.org/aos/agrovoc/c_37948"]
      },
      "Agriculture": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_203"
      },
      "Climate change": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_1666"
      },
      "Expropriation": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_1798"
      },
      "Extractive industries": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_5d3b8015"
      },
      "Food Security  ": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_10967"
      },
      "Ethnic minorities and indigenous people": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_331524"
      },
      "Water rights": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_16062"
      },
      "Contract farming": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_1839"
      },
      "Organic farming": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_15911"
      },
      "Pest management": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_13262"
      },
      "Soil management": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_7176"
      },
      "Animal products": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_438"
      },
      "Dairy": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_4830"
      },
      "Meat": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_4669"
      },
      "Leather": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_4241"
      },
      "Cassava": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_9649"
      },
      "Jatropha": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_16253"
      },
      "Cashews": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_9647"
      },
      "Maize (corn)": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_12332"
      },
      "Palm oil": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_5514"
      },
      "Rice": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_6599"
      },
      "Rubber": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_6678"
      },
      "Soybean": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_14477"
      },
      "Sugarcane": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_7501"
      },
      "Fisheries production": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_2940"
      },
      "Fish farming and aquaculture": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_550"
      },
      "Asian Development Bank (ADB)": {
          "exact_match": "http://eurovoc.europa.eu/6336"
      },
      "Food and Agriculture Organization (FAO)": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_2791"
      },
      "International Monetary Fund (IMF)": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_11710"
      },
      "United Nations": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_8069"
      },
      "World Bank": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_3781"
      },
      "Red Cross": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_50295"
      },
      "Drought": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_2391"
      },
      "Fires": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_2915"
      },
      "Floods": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_2980"
      },
      "Storms": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_7436"
      },
      "Earthquakes": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_2440"
      },
      "Tsunamis": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_92355"
      },
      "Micro-finance": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_331091"
      },
      "Business associations": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_50167"
      },
      "Investment": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_3930"
      },
      "Small and medium enterprises (SME)": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_50307"
      },
      "Trade": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_7848"
      },
      "Imports": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_3815"
      },
      "Exports": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_2761"
      },
      "Securities exchange (stock market)": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_28645"
      },
      "Stock market": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_28645"
      },
      "Energy": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_2565"
      },
      "Electricity production": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_24836"
      },
      "Hydropower dams": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_25612"
      },
      "Renewable energy production": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_25719"
      },
      "Biodiversity": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_33949"
      },
      "Plants": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_5993"
      },
      "Ecosystems": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_2482"
      },
      "Environmental impact assessments": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_33483"
      },
      "Climate change": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_1666"
      },
      "Adaptation": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_1374567058134"
      },
      "Mitigation": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_1374571087594"
      },
      "Air pollution": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_228"
      },
      "Water pollution": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_8321"
      },
      "Solid waste": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_7228"
      },
      "Forest cover": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_9000180"
      },
      "Secondary/mixed forest": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_28144"
      },
      "Forest products": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_3049"
      },
      "Forest industry": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_28084"
      },
      "Logging and timber": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_7775"
      },
      "Hardwoods": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_3495"
      },
      "Acacia": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_32"
      },
      "Eucalyptus": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_2683"
      },
      "Pine": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_5890"
      },
      "Forest protection": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_28075"
      },
      "Protected areas": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_37952"
      },
      "Protected forests": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_28126"
      },
      "Community forest": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_16532"
      },
      "Water resources": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_8325"
      },
      "Ground water": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_3391"
      },
      "Mining": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_49983"
      },
      "Coal": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_1693"
      },
      "Copper": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_1868"
      },
      "Gold": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_33067"
      },
      "Uranium": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_8084"
      },
      "Government": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_11230"
      },
      "National government": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_1437"
      },
      "Head of state": {
          "exact_match": "http://reference.data.gov.uk/def/central-government/headOfGovernment"
      },
      "Parliament": {
          "exact_match": "http://dbpedia.org/ontology/Parliament"
      },
      "Provincial and local governments": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_4412"
      },
      "Elections": {
          "exact_match": "http://www.ontotext.com/proton/protonext#Election"
      },
      "Budget": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_1134"
      },
      "Taxation": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_7626"
      },
      "Government services": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_6353"
      },
      "International relations": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_26793"
      },
      "Construction": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_35060"
      },
      "Handicrafts": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_3483"
      },
      "Manufacturing": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_92365"
      },
      "Animal feed": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_2843"
      },
      "Biofuels": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_27465"
      },
      "Fertilizer": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_2867"
      },
      "Food processing": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_37969"
      },
      "Furniture": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_3152"
      },
      "Rubber": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_6678"
      },
      "Beverages": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_896"
      },
      "Processed foods": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_28228"
      },
      "Salt": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_33129"
      },
      "Cement": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_1426"
      },
      "Steel": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_7384"
      },
      "Real estate": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_13767"
      },
      "Tourism": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_7822"
      },
      "Infrastructure": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_26790"
      },
      "Internet": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_36661"
      },
      "Radio": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_6424"
      },
      "Television": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_7651"
      },
      "Markets": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_4626"
      },
      "Rail": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_6434"
      },
      "Labor": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_4128"
      },
      "Unions": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_50323"
      },
      "Land": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_4172"
      },
      "Land classifications": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_15991"
      },
      "Land transfers": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_4181"
      },
      "Concessions": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_357653f9"
      },
      "Expropriation": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_1798"
      },
      "Communal land": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_1782"
      },
      "Legal framework": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_331456"
      },
      "Police": {
          "exact_match": "http://linkedgeodata.org/ontology/Police"
      },
      "Prisons": {
          "exact_match": "http://dbpedia.org/ontology/Prison"
      },
      "Population": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_330887"
      },
      "Demographics": {
          "exact_match": "http://dbpedia.org/ontology/demographics"
      },
      "Migration": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_4822"
      },
      "Immigration": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_37976"
      },
      "Emigration": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_37979"
      },
      "Censuses": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_1430"
      },
      "Foreign workers in country": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_10981"
      },
      "Arts": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_49887"
      },
      "Civil society": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_9000020"
      },
      "Non-governmental organizations": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_24068"
      },
      "Education and training": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_2488"
      },
      "Pre school": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_6160"
      },
      "Ethnic minorities and indigenous people": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_331524"
      },
      "Human rights": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_37883"
      },
      "Vocational education": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_8285"
      },
      "Higher education": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_3613"
      },
      "Universities": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_8070"
      },
      "Access to information": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_37829"
      },
      "Public health": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_6349"
      },
      "Health care policy and administration": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_28754"
      },
      "HIV/AIDS": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_37855"
      },
      "Malaria": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_34312"
      },
      "Tuberculosis": {
          "exact_match": "http://aims.fao.org/aos/agrovoc/c_7997"
      },
      "Irrigation and water management": {
          "broad_matches": ["http://aims.fao.org/aos/agrovoc/c_8320"]
      },
      "Land policy and administration": {
          "broad_matches": ["http://aims.fao.org/aos/agrovoc/c_195"]
      },
      "Family, children and youth": {
          "broad_matches": ["http://aims.fao.org/aos/agrovoc/c_8491"]
      },
      "Land and housing rights and evictions": {
          "broad_matches": ["http://aims.fao.org/aos/agrovoc/c_37898"]
      },
      "": {
          "broad_matches": [""]
      },
      "": {
          "broad_matches": [""]
      }
  }

  if term not in mapping:
    return term

  return mapping[term]


def get_triples_by_dataset_type(subject, dataset_dict, dataset_type):

  # Basic fields
  triples_by_dataset_type = {
      "dataset": [
          (subject, CRO.copyright, dataset_dict.get('copyright')),
          (subject, DOAP.version, dataset_dict.get('version')),
          (subject, EBUCORE.contact, dataset_dict.get('contact')),
          (subject, DQM.accuracy, dataset_dict.get('odm_accuracy')),
          (subject, DQ.logicalConsistency,
           dataset_dict.get('odm_logical_consistency')),
          (subject, DQ.completeness, dataset_dict.get('odm_completeness')),
          (subject, MD.useconstraints, dataset_dict.get(
              'odm_access_and_use_constraints')),
          (subject, OMN.attribute, dataset_dict.get('odm_attributes')),
          (subject, DCT.source, dataset_dict.get('odm_source'))
      ],
      "library_record": [
          (subject, AGLS.documentType, dataset_dict.get('document_type')),
          (subject, GC.shortTitle, dataset_dict.get('marc21_246')),
          (subject, CRO.copyright, dataset_dict.get('copyright')),
          (subject, DOAP.version, dataset_dict.get('version')),
          (subject, EBUCORE.contact, dataset_dict.get('contact')),
          (subject, MD.useconstraints, dataset_dict.get(
              'odm_access_and_use_constraints')),
          (subject, OPUS.author, dataset_dict.get('marc21_100')),
          (subject, OPUS.author, dataset_dict.get('marc21_110')),
          (subject, OPUS.coauthor, dataset_dict.get('marc21_700')),
          (subject, OPUS.coauthor, dataset_dict.get('marc21_710')),
          (subject, OPUS.isbn, dataset_dict.get('marc21_020')),
          (subject, DBPEDIA.issn, dataset_dict.get('marc21_022')),
          (subject, MREL.pup, dataset_dict.get('marc21_260a')),
          (subject, DCT.publisher, dataset_dict.get('marc21_260b')),
          (subject, BIBO.numPages, dataset_dict.get('marc21_300')),
          (subject, SKOS.note, dataset_dict.get('marc21_500')),
          (subject, PPROC.documentReference,
           dataset_dict.get('odm_reference_document'))
      ],
      "laws_record": [
          (subject, AGLS.documentType, dataset_dict.get('document_type')),
          (subject, DBPEDIA.documentNumber, dataset_dict.get('odm_document_number')),
          (subject, GC.shortTitle, dataset_dict.get('odm_short_title')),
          (subject, CRO.copyright, dataset_dict.get('copyright')),
          (subject, EBUCORE.contact, dataset_dict.get('contact')),
          (subject, SKOS.changeNote, dataset_dict.get(
              'odm_laws_previous_changes_notes')),
          (subject, SORON.citedBy, dataset_dict.get(
              'odm_laws_official_publication_reference')),
          (subject, SKOS.note, dataset_dict.get('odm_laws_notes')),
          (subject, PPROC.documentReference,
           dataset_dict.get('odm_reference_document'))
      ]
  }

  return triples_by_dataset_type[dataset_type]


def get_namespaces_by_dataset_type(dataset_type):

  # Basic fields
  namespaces_by_dataset_type = {
      "dataset": {
          'dct': DCT,
          'dcat': DCAT,
          'foaf': FOAF,
          'schema': SCHEMA,
          'skos': SKOS,
          'cro': CRO,
          'doap': DOAP,
          'ebucore': EBUCORE,
          'dqm': DQM,
          'dq': DQ,
          'omn': OMN,
          'md': MD,
          'gn': GN,
          'dc': DC
      },
      "library_record": {
          'agls': AGLS,
          'bibo': BIBO,
          'dbpedia': DBPEDIA,
          'gc': GC,
          'dct': DCT,
          'dcat': DCAT,
          'foaf': FOAF,
          'mrel': MREL,
          'schema': SCHEMA,
          'cro': CRO,
          'doap': DOAP,
          'ebucore': EBUCORE,
          'dqm': DQM,
          'dq': DQ,
          'omn': OMN,
          'opus': OPUS,
          'pproc': PPROC,
          'md': MD,
          'gn': GN,
          'skos': SKOS,
          'dc': DC
      },
      "laws_record": {
          'agls': AGLS,
          'bibo': BIBO,
          'bibframe': BIBFRAME,
          'dbpedia': DBPEDIA,
          'gc': GC,
          'dct': DCT,
          'dcat': DCAT,
          'foaf': FOAF,
          'mrel': MREL,
          'schema': SCHEMA,
          'cro': CRO,
          'doap': DOAP,
          'ebucore': EBUCORE,
          'dqm': DQM,
          'dq': DQ,
          'omn': OMN,
          'opus': OPUS,
          'pproc': PPROC,
          'md': MD,
          'gn': GN,
          'skos': SKOS,
          'soron': SORON,
          'dc': DC
      },
      "all": {
        'agls': AGLS,
        'bibo': BIBO,
        'bibframe': BIBFRAME,
        'dbpedia': DBPEDIA,
        'gc': GC,
        'dct': DCT,
        'dcat': DCAT,
        'foaf': FOAF,
        'mrel': MREL,
        'schema': SCHEMA,
        'cro': CRO,
        'doap': DOAP,
        'ebucore': EBUCORE,
        'dqm': DQM,
        'dq': DQ,
        'omn': OMN,
        'opus': OPUS,
        'pproc': PPROC,
        'md': MD,
        'gn': GN,
        'skos': SKOS,
        'soron': SORON,
        'dc': DC
      }
  }

  return namespaces_by_dataset_type[dataset_type]


def get_date_fields_by_dataset_type(dataset_type):

  # Basic fields
  date_fields_by_dataset_type = {
      "dataset": [
          ('odm_date_created', DCT.created, None),
          ('odm_date_uploaded', SCHEMA.uploadDate, None),
          ('odm_date_modified', DCT.modified, None)
      ],
      "library_record": [
          ('marc21_260c', DCT.issued, None),
          ('odm_date_uploaded', SCHEMA.uploadDate, None)
      ],
      "laws_record": [
          ('odm_promulgation_date', BIBFRAME.legalDate, None)
      ]
  }

  return date_fields_by_dataset_type[dataset_type]


def map_country_code_iso2_iso3(iso2_code):

  countries = {"AD": "AND", "AE": "ARE", "AF": "AFG", "AG": "ATG", "AI": "AIA", "AL": "ALB", "AM": "ARM", "AO": "AGO", "AQ": "ATA", "AR": "ARG", "AS": "ASM", "AT": "AUT", "AU": "AUS", "AW": "ABW", "AX": "ALA", "AZ": "AZE", "BA": "BIH", "BB": "BRB", "BD": "BGD", "BE": "BEL", "BF": "BFA", "BG": "BGR", "BH": "BHR", "BI": "BDI", "BJ": "BEN", "BL": "BLM", "BM": "BMU", "BN": "BRN", "BO": "BOL", "BQ": "BES", "BR": "BRA", "BS": "BHS", "BT": "BTN", "BV": "BVT", "BW": "BWA", "BY": "BLR", "BZ": "BLZ", "CA": "CAN", "CC": "CCK", "CD": "COD", "CF": "CAF", "CG": "COG", "CH": "CHE", "CI": "CIV", "CK": "COK", "CL": "CHL", "CM": "CMR", "CN": "CHN", "CO": "COL", "CR": "CRI", "CU": "CUB", "CV": "CPV", "CW": "CUW", "CX": "CXR", "CY": "CYP", "CZ": "CZE", "DE": "DEU", "DJ": "DJI", "DK": "DNK", "DM": "DMA", "DO": "DOM", "DZ": "DZA", "EC": "ECU", "EE": "EST", "EG": "EGY", "EH": "ESH", "ER": "ERI", "ES": "ESP", "ET": "ETH", "FI": "FIN", "FJ": "FJI", "FK": "FLK", "FM": "FSM", "FO": "FRO", "FR": "FRA", "GA": "GAB", "GB": "GBR", "GD": "GRD", "GE": "GEO", "GF": "GUF", "GG": "GGY", "GH": "GHA", "GI": "GIB", "GL": "GRL", "GM": "GMB", "GN": "GIN", "GP": "GLP", "GQ": "GNQ", "GR": "GRC", "GS": "SGS", "GT": "GTM", "GU": "GUM", "GW": "GNB", "GY": "GUY", "HK": "HKG", "HM": "HMD", "HN": "HND", "HR": "HRV", "HT": "HTI", "HU": "HUN", "ID": "IDN", "IE": "IRL", "IL": "ISR", "IM": "IMN", "IN": "IND", "IO": "IOT", "IQ": "IRQ", "IR": "IRN", "IS": "ISL", "IT": "ITA", "JE": "JEY", "JM": "JAM", "JO": "JOR", "JP": "JPN", "KE": "KEN", "KG": "KGZ", "KH": "KHM", "KI": "KIR", "KM": "COM", "KN": "KNA", "KP": "PRK", "KR": "KOR", "KW": "KWT", "KY": "CYM",
               "KZ": "KAZ", "LA": "LAO", "LB": "LBN", "LC": "LCA", "LI": "LIE", "LK": "LKA", "LR": "LBR", "LS": "LSO", "LT": "LTU", "LU": "LUX", "LV": "LVA", "LY": "LBY", "MA": "MAR", "MC": "MCO", "MD": "MDA", "ME": "MNE", "MF": "MAF", "MG": "MDG", "MH": "MHL", "MK": "MKD", "ML": "MLI", "MM": "MMR", "MN": "MNG", "MO": "MAC", "MP": "MNP", "MQ": "MTQ", "MR": "MRT", "MS": "MSR", "MT": "MLT", "MU": "MUS", "MV": "MDV", "MW": "MWI", "MX": "MEX", "MY": "MYS", "MZ": "MOZ", "NA": "NAM", "NC": "NCL", "NE": "NER", "NF": "NFK", "NG": "NGA", "NI": "NIC", "NL": "NLD", "NO": "NOR", "NP": "NPL", "NR": "NRU", "NU": "NIU", "NZ": "NZL", "OM": "OMN", "PA": "PAN", "PE": "PER", "PF": "PYF", "PG": "PNG", "PH": "PHL", "PK": "PAK", "PL": "POL", "PM": "SPM", "PN": "PCN", "PR": "PRI", "PS": "PSE", "PT": "PRT", "PW": "PLW", "PY": "PRY", "QA": "QAT", "RE": "REU", "RO": "ROU", "RS": "SRB", "RU": "RUS", "RW": "RWA", "SA": "SAU", "SB": "SLB", "SC": "SYC", "SD": "SDN", "SE": "SWE", "SG": "SGP", "SH": "SHN", "SI": "SVN", "SJ": "SJM", "SK": "SVK", "SL": "SLE", "SM": "SMR", "SN": "SEN", "SO": "SOM", "SR": "SUR", "SS": "SSD", "ST": "STP", "SV": "SLV", "SX": "SXM", "SY": "SYR", "SZ": "SWZ", "TC": "TCA", "TD": "TCD", "TF": "ATF", "TG": "TGO", "TH": "THA", "TJ": "TJK", "TK": "TKL", "TL": "TLS", "TM": "TKM", "TN": "TUN", "TO": "TON", "TR": "TUR", "TT": "TTO", "TV": "TUV", "TW": "TWN", "TZ": "TZA", "UA": "UKR", "UG": "UGA", "UM": "UMI", "US": "USA", "UY": "URY", "UZ": "UZB", "VA": "VAT", "VC": "VCT", "VE": "VEN", "VG": "VGB", "VI": "VIR", "VN": "VNM", "VU": "VUT", "WF": "WLF", "WS": "WSM", "YE": "YEM", "YT": "MYT", "ZA": "ZAF", "ZM": "ZMB", "ZW": "ZWE"}

  if iso2_code not in countries:
    return iso2_code

  return countries[iso2_code]
