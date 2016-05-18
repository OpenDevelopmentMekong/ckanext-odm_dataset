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
