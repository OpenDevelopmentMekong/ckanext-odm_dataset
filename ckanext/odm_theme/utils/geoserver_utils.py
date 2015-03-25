# -*- coding: utf-8 -*-
''' Module containing classes and methods for interaction with geoserver

'''
import json
import urllib2
import urllib

# Interface definition
class IGeoserverRestApi:

  def get_layers(self):
    raise NotImplementedError

  def get_layer(self,url):
    raise NotImplementedError

  def get_feature_type(self,url):
    raise NotImplementedError

  def get_geojson_from_url(self,url):
    raise NotImplementedError

  def download_file(self,src,dest):
    raise NotImplementedError

# Mock implementation
class TestGeoserverRestApi (IGeoserverRestApi):

  def __init__(self):

    self.geoserver_url = ''
    self.geoserver_auth = ''

    return

  def get_layers(self):

    # return JSON dictionary
    json_string = '{"layers":{"layer":[{"name":"Provinces","href":"http://64.91.228.155:8181/geoserver/rest/layers/Provinces.json"},{"name":"map_agricultural_family_living_with_rice_land_area_kh","href":"http://64.91.228.155:8181/geoserver/rest/layers/map_agricultural_family_living_with_rice_land_area_kh.json"}]}}'
    return json.loads(json_string)

  def get_layer(self,url):

    # return JSON dictionary
    json_string = '{"layer":{"name":"Provinces","type":"VECTOR","defaultStyle":{"name":"Provinces 2011","href":"http://64.91.228.155:8181/geoserver/rest/workspaces/Topography/styles/Provinces+2011.json"},"resource":{"@class":"featureType","name":"Provinces","href":"http://64.91.228.155:8181/geoserver/rest/workspaces/Topography/datastores/Province_2011/featuretypes/Provinces.json"},"enabled":true,"attribution":{"logoWidth":0,"logoHeight":0}}}'
    return json.loads(json_string)

  def get_feature_type(self,url):

    # return JSON dictionary
    json_string = '{"featureType":{"name":"Provinces","nativeName":"Provinces","namespace":{"name":"Topography","href":"http://64.91.228.155:8181/geoserver/rest/namespaces/Topography.json"},"title":"Provinces","description":"Contents of file","keywords":{"string":["features","Provinces"]}}}'
    return json.loads(json_string)

  def get_geojson_from_url(self,url):

    # return JSON dictionary
    json_string = '{"type":"FeatureCollection","features":[{"type":"Feature","geometry":{"type":"Point","coordinates":[102,0.6]},"properties":{"prop0":"value0"}},{"type":"Feature","geometry":{"type":"LineString","coordinates":[[102,0],[103,1],[104,0],[105,1]]},"properties":{"prop1":0,"prop0":"value0"}},{"type":"Feature","geometry":{"type":"Polygon","coordinates":[[[100,0],[101,0],[101,1],[100,1],[100,0]]]},"properties":{"prop1":{"this":"that"},"prop0":"value0"}}]}'
    return json.loads(json_string)

  def download_file(self,src,dest):
    with open(dest, 'w') as outfile:
      outfile.write('Sample file contents')


# Real implementation
class RealGeoserverRestApi (IGeoserverRestApi):

  def __init__(self,config):

    # Init here
    self.geoserver_url = config.GEOSERVER_URL
    self.geoserver_auth = config.GEOSERVER_AUTH

    return

  def get_layers(self):

    request = urllib2.Request(self.geoserver_url+'rest/layers.json')
    request.add_header('Authorization', self.geoserver_auth)

    # Make the HTTP request.
    response = urllib2.urlopen(request)
    assert response.code == 200

    # return JSON dictionary
    return json.loads(response.read())

  def get_layer(self,url):

    request = urllib2.Request(url)
    request.add_header('Authorization', self.geoserver_auth)

    # Make the HTTP request.
    response = urllib2.urlopen(request)
    assert response.code == 200

    # return JSON dictionary
    return json.loads(response.read())

  def get_feature_type(self,url):

    request = urllib2.Request(url)
    request.add_header('Authorization', self.geoserver_auth)

    # Make the HTTP request.
    response = urllib2.urlopen(request)
    assert response.code == 200

    # return JSON dictionary
    return json.loads(response.read())

  def get_geojson_from_url(self,url):

    request = urllib2.Request(url)
    request.add_header('Authorization', self.geoserver_auth)

    # Make the HTTP request.
    response = urllib2.urlopen(request)
    assert response.code == 200

    # return JSON dictionary
    return json.loads(response.read())

  def download_file(self,src,dest):

    urllib.urlretrieve (src,dest)
