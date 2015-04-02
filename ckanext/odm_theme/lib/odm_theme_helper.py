#!/usr/bin/env python
# -*- coding: utf-8 -*-
countries = [
  ('Cambodia','Cambodia'),
  ('Vietnam','Vietnam'),
  ('Laos','Laos'),
  ('Thailand','Thailand'),
  ('Myanmar','Myanmar')
]

languages = [
('en','English'),
('kh','Khmer'),
('vi','Vietnamese'),
('lo','Lao'),
('th','Thai'),
('my','Burmese')
]

odc_fields = [
('file_name_kh','File (Khmer)',False),
('file_name_en','File (English)',False),
('adopted_date','Adopted Date',False),
('number_en','Number (English)',False),
('number_kh','Number (Khmer)',False),
('published_date','Publication date',False),
('published_under','Published under',False)
]

metadata_fields = [
('odm_format','Format',True),
('odm_language','Language',True),
('odm_date_created','Date Created',True),
('odm_date_uploaded','Date Uploaded',True),
('odm_date_modified','Date Modified',True),
('odm_temporal_range','Temporal Range',True),
('odm_spatial_range','Spatial Range',False),
('odm_accuracy','Accuracy',False),
('odm_logical_consistency','Logical Consistency',False),
('odm_completeness','Completeness',False),
('odm_process','Process(es)',True),
('odm_source','Source(s)',True),
('odm_contact','Contact',True),
('odm_contact_email','Contact Email',True),
('odm_access_and_use_constraints','Access and Use Constraints',False),
('odm_url','Download URL',False),
('odm_metadata_reference_information','Metadata Reference Information',False),
('odm_attributes','Attributes',False)
]

tag_dictionaries = [('taxonomy','subject-list')]

library_fields = [
('marc21_020','ISBN',False),
('marc21_022','ISSN',False),
('marc21_084','Classification',False),
('marc21_100','Author',False),
('marc21_110','Corporate Author',False),
('marc21_245','Title',False),
('marc21_246','Varying Form of Title',False),
('marc21_250','Edition',False),
('marc21_260a','Publication Place',False),
('marc21_260b','Publication Name',False),
('marc21_260c','Publication Date',False),
('marc21_300','Pagination',False),
('marc21_500','General Note',False),
('marc21_520','Summary',False),
('marc21_650','Subject',False),
('marc21_651','Subject (Geographic Name)',False),
('marc21_653','Keyword',False),
('marc21_700','Co-Author',False),
('marc21_710','Co-Author (Corporate)',False),
('marc21_850','Institution',False),
('marc21_852','Location',False)
]
