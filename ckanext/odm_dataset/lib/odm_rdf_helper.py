#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import logging
import rdflib
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF

log = logging.getLogger(__name__)

def split_multilingual_object_into_triples(subject,predicate,object_value):
  ''' Takes a triple and splits it into different localized if literal_object_value
      is multilingual (JSON object, ckanext-fluent format)
  '''
  triples_to_return = []

  try:
    json_value = json.loads(object_value);
    for key, value in json_value.iteritems():
      if value:
        triples_to_return.append((subject, predicate, Literal(value, lang=key)))
  except:
    triples_to_return.append((subject, predicate, Literal(object_value)))

  return triples_to_return
