# -*- coding: utf-8 -*-
''' Module containing classes and methods for interaction with NextGenLib

'''
import json
import urllib2
import urllib

# Interface definition
class INGLApi:

  def download_file(self,path,dest):
    raise NotImplementedError

# Mock implementation
class TestNGLApi (INGLApi):

  def __init__(self):

    self.ngl_url = ''

    return

  def download_file(self,path,dest):
    with open(dest, 'w') as outfile:
      outfile.write('Sample file contents')


# Real implementation
class RealNGLApi (INGLApi):

  def __init__(self,config):

    # Init here
    self.ngl_url = config.NGL_URL

    return

  def download_file(self,path,dest):

    path_to_file = str(self.ngl_url) + path
    urllib.urlretrieve(path_to_file,dest)
