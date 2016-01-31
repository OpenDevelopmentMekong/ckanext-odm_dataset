import os
import json
from nose.tools import assert_equal, assert_in
import unittest
from unittest.case import SkipTest

class TestValidation(unittest.TestCase):

  @classmethod
  def setup_class(self):
    "set up test fixtures"
    self.dirs = [];

    self.json_files = [
      os.path.abspath(os.path.join(__file__, '../../','odm_dataset_presets.json')),
      os.path.abspath(os.path.join(__file__, '../../','odm_dataset_schema.json'))
    ];

  @classmethod
  def teardown_class(self):
    "tear down test fixtures"

  def test_data_available(self):

    for directory in self.dirs:
      assert os.path.isdir(directory)

    for json_file in self.json_files:
      print(json_file)
      assert os.path.isfile(json_file)

  def test_correct_json_files(self):

    all_valid = True
    for json_file in self.json_files:
      with open(json_file) as f:
        try:
          return json.loads(f.read())
        except ValueError as e:
          all_valid = False
          print('invalid json: %s' % e)

      assert all_valid
