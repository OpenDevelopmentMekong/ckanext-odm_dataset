import os
import json
from nose.tools import assert_equal, assert_in
import rdflib
from rdflib import URIRef, BNode, Literal
from rdflib.namespace import Namespace, RDF
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../lib')))
import odm_rdf_helper

class TestProfiles:

  def test_01_split_multilingual_object_and_add_triple(self):

    triples = odm_rdf_helper.split_multilingual_object_into_triples('some_id',RDF.type,'literal value')
    assert len(triples) == 1
    assert triples[0][0] == 'some_id'
    assert triples[0][1] == RDF.type
    assert triples[0][2].toPython() == 'literal value'

    triples = odm_rdf_helper.split_multilingual_object_into_triples('some_id',RDF.type,'{"km":"value km","th":"value th"}')
    assert len(triples) == 2
    assert triples[0][0] == 'some_id'
    assert triples[0][1] == RDF.type
    assert triples[0][2].toPython() == 'value th'
