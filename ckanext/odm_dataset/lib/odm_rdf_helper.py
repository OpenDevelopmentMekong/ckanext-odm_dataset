#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import rdflib
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF
import traceback

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
        triples_to_return.append((subject, predicate, Literal(value, lang=key)))

    return triples_to_return

def map_internal_to_standard_taxonomic_term(term):
  ''' Takes an internal taxonomic term and returns the URI of a corresponding standard term, if found
  '''

  log.debug("map_internal_to_standard_taxonomic_term: %s", term)

  mapping = {
    "Deforestration drivers": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_15590"
    },
    "Development and assistance for land tenure and land titling": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_2224"
    },
    "Environment and natural resources": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_2593"
    },
    "Agricultural management systems and technologies": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_2807"
    },
    "Fishing, fisheries and aquaculture": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_2934"
    },
    "Forests and forestry": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_3055"
    },
    "Forest policy and administration": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_3060"
    },
    "Disasters": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_10391"
    },
    "Poverty policy and regulation": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_6151"
    },
    "Land sales and trades": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_9a4f48b4"
    },
    "Urban policy and administration": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_37948"
    },
    "Agriculture": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_203"
    },
    "Climate change": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_1666"
    },
    "Expropriation": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_1798"
    },
    "Extractive industries": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_5d3b8015"
    },
    "Food Security  ": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_10967"
    },
    "Ethnic minorities and indigenous people": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_331524"
    },
    "Water rights": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_16062"
    },
    "Contract farming": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_1839"
    },
    "Organic farming": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_15911"
    },
    "Pest management": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_13262"
    },
    "Soil management": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_7176"
    },
    "Animal products": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_438"
    },
    "Dairy": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_4830"
    },
    "Meat": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_4669"
    },
    "Leather": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_4241"
    },
    "Cassava": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_9649"
    },
    "Jatropha": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_16253"
    },
    "Cashews": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_9647"
    },
    "Maize (corn)": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_12332"
    },
    "Palm oil": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_5514"
    },
    "Rice": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_6599"
    },
    "Rubber": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_6678"
    },
    "Soybean": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_14477"
    },
    "Sugarcane": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_7501"
    },
    "Fisheries production": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_2940"
    },
    "Fish farming and aquaculture": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_550"
    },
    "Asian Development Bank (ADB)": {
      "direct_match" : "http://eurovoc.europa.eu/6336"
    },
    "Food and Agriculture Organization (FAO)": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_2791"
    },
    "International Monetary Fund (IMF)": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_11710"
    },
    "United Nations": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_8069"
    },
    "World Bank": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_3781"
    },
    "Red Cross": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_50295"
    },
    "Drought": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_2391"
    },
    "Fires": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_2915"
    },
    "Floods": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_2980"
    },
    "Storms": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_7436"
    },
    "Earthquakes": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_2440"
    },
    "Tsunamis": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_92355"
    },
    "Micro-finance": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_331091"
    },
    "Business associations": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_50167"
    },
    "Investment": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_3930"
    },
    "Small and medium enterprises (SME)": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_50307"
    },
    "Trade": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_7848"
    },
    "Imports": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_3815"
    },
    "Exports": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_2761"
    },
    "Securities exchange (stock market)": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_28645"
    },
    "Stock market": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_28645"
    },
    "Energy": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_2565"
    },
    "Electricity production": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_24836"
    },
    "Hydropower dams": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_25612"
    },
    "Renewable energy production": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_25719"
    },
    "Biodiversity": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_33949"
    },
    "Plants": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_5993"
    },
    "Ecosystems": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_2482"
    },
    "Environmental impact assessments": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_33483"
    },
    "Climate change": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_1666"
    },
    "Adaptation": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_1374567058134"
    },
    "Mitigation": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_1374571087594"
    },
    "Air pollution": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_228"
    },
    "Water pollution": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_8321"
    },
    "Solid waste": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_7228"
    },
    "Forest cover": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_9000180"
    },
    "Secondary/mixed forest": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_28144"
    },
    "Forest products": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_3049"
    },
    "Forest industry": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_28084"
    },
    "Logging and timber": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_7775"
    },
    "Hardwoods": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_3495"
    },
    "Acacia": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_32"
    },
    "Eucalyptus": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_2683"
    },
    "Pine": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_5890"
    },
    "Forest protection": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_28075"
    },
    "Protected areas": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_37952"
    },
    "Protected forests": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_28126"
    },
    "Community forest": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_16532"
    },
    "Water resources": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_8325"
    },
    "Ground water": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_3391"
    },
    "Mining": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_49983"
    },
    "Coal": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_1693"
    },
    "Copper": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_1868"
    },
    "Gold": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_33067"
    },
    "Uranium": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_8084"
    },
    "Government": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_11230"
    },
    "National government": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_1437"
    },
    "Head of state": {
      "direct_match" : "http://reference.data.gov.uk/def/central-government/headOfGovernment"
    },
    "Parliament": {
      "direct_match" : "http://dbpedia.org/ontology/Parliament"
    },
    "Provincial and local governments": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_4412"
    },
    "Elections": {
      "direct_match" : "http://www.ontotext.com/proton/protonext#Election"
    },
    "Budget": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_1134"
    },
    "Taxation": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_7626"
    },
    "Government services": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_6353"
    },
    "International relations": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_26793"
    },
    "Construction": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_35060"
    },
    "Handicrafts": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_3483"
    },
    "Manufacturing": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_92365"
    },
    "Animal feed": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_2843"
    },
    "Biofuels": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_27465"
    },
    "Fertilizer": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_2867"
    },
    "Food processing": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_37969"
    },
    "Furniture": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_3152"
    },
    "Rubber": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_6678"
    },
    "Beverages": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_896"
    },
    "Processed foods": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_28228"
    },
    "Salt": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_33129"
    },
    "Cement": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_1426"
    },
    "Steel": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_7384"
    },
    "Real estate": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_13767"
    },
    "Tourism": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_7822"
    },
    "Infrastructure": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_26790"
    },
    "Internet": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_36661"
    },
    "Radio": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_6424"
    },
    "Television": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_7651"
    },
    "Markets": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_4626"
    },
    "Rail": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_6434"
    },
    "Labor": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_4128"
    },
    "Unions": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_50323"
    },
    "Land": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_4172"
    },
    "Land classifications": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_15991"
    },
    "Land transfers": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_4181"
    },
    "Concessions": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_357653f9"
    },
    "Expropriation": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_1798"
    },
    "Communal land": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_1782"
    },
    "Legal framework": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_331456"
    },
    "Police": {
      "direct_match" : "http://linkedgeodata.org/ontology/Police"
    },
    "Prisons": {
      "direct_match" : "http://dbpedia.org/ontology/Prison"
    },
    "Population": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_330887"
    },
    "Demographics": {
      "direct_match" : "http://dbpedia.org/ontology/demographics"
    },
    "Migration": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_4822"
    },
    "Immigration": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_37976"
    },
    "Emigration": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_37979"
    },
    "Censuses": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_1430"
    },
    "Foreign workers in country": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_10981"
    },
    "Arts": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_49887"
    },
    "Civil society": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_9000020"
    },
    "Non-governmental organizations": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_24068"
    },
    "Education and training": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_2488"
    },
    "Pre school": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_6160"
    },
    "Ethnic minorities and indigenous people": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_331524"
    },
    "Human rights": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_37883"
    },
    "Vocational education": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_8285"
    },
    "Higher education": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_3613"
    },
    "Universities": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_8070"
    },
    "Access to information": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_37829"
    },
    "Public health": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_6349"
    },
    "Health care policy and administration": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_28754"
    },
    "HIV/AIDS": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_37855"
    },
    "Malaria": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_34312"
    },
    "Tuberculosis": {
      "direct_match" : "http://aims.fao.org/aos/agrovoc/c_7997"
    }
  }

  if term in mapping:
    return URIRef(mapping[term]["direct_match"])

  return Literal(term)
