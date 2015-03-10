#!/usr/bin/env python
# -*- coding: utf-8 -*-

metadata_fields = [
('odm_format','Format',True),
('odm_language','Language',True),
('odm_date_created','Date created',True),
('odm_date_uploaded','Date uploaded',True),
('odm_date_modified','Date modified',True),
('odm_temporal_range','Temporal range',True),
('odm_spatial_range','Spatial range',False),
('odm_accuracy','Accuracy',False),
('odm_logical_consistency','Logical Consistency',False),
('odm_completeness','Completeness',False),
('odm_process','Process(es)',True),
('odm_source','Source(s)',True),
('author','Contact',True),
('author_email','Contact Email',True),
('odm_access_and_use_constraints','Access and use constraints',False),
('url','Download URL',False),
('odm_metadata_reference_information','Metadata reference information',False),
('odm_attributes','Attributes',False)
]

taxonomy_fields = [('taxonomy','Tags in taxonomy')]

library_fields = [
('marc21_020','ISBN',False),
('marc21_022','ISSN',False),
('marc21_084','Classification',False),
('marc21_100','Author',False),
('marc21_110','Corporate Author',False),
('marc21_245','Title',False),
('marc21_246','Varying Form of Title',False),
('marc21_250','Edition',False),
('marc21_260a','Publication Name',False),
('marc21_260b','Publication Place',False),
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
