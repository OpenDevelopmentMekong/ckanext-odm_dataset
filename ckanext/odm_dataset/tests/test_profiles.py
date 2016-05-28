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

    triples = odm_rdf_helper.split_multilingual_object_into_triples(('some_id',RDF.type,'literal value'))
    assert len(triples) == 1
    assert triples[0][0] == 'some_id'
    assert triples[0][1] == RDF.type
    assert triples[0][2].toPython() == 'literal value'

  def test_02_split_multilingual_object_and_add_triple(self):

    triples = odm_rdf_helper.split_multilingual_object_into_triples(('some_id',RDF.type,json.loads('{"km":"value km","th":"value th"}')))
    assert len(triples) == 2
    assert triples[0][0] == 'some_id'
    assert triples[0][1] == RDF.type
    assert triples[0][2].toPython() == 'value th'

  def test_03_split_multilingual_object_and_add_triple(self):

    triples = odm_rdf_helper.split_multilingual_object_into_triples(('some_id',RDF.type,'{"km":"value km","th":"value th"}'))
    assert len(triples) == 1
    assert triples[0][0] == 'some_id'
    assert triples[0][1] == RDF.type
    assert triples[0][2].toPython() == '{"km":"value km","th":"value th"}'

  def test_04_split_multilingual_object_and_add_triple(self):

    triples = odm_rdf_helper.split_multilingual_object_into_triples(('some_id',RDF.type,None))
    assert len(triples) == 0

  def test_05_map_internal_to_standard_taxonomic_term(self):

    term = odm_rdf_helper.map_internal_to_standard_taxonomic_term('unknown')
    assert term == Literal('unknown')

  def test_06_map_internal_to_standard_taxonomic_term(self):

    term = odm_rdf_helper.map_internal_to_standard_taxonomic_term('Environment and natural resources')
    assert term == URIRef('http://aims.fao.org/aos/agrovoc/c_2593')
