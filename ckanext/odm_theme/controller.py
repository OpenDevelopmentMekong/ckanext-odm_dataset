import ckan.plugins as p
import ckan.lib.helpers as h
import plugin as odm_theme
from ckan.lib.base import BaseController

class ThemeController(BaseController):
  def library(self):
    return h.redirect_to(controller='organization', action='read', id='odm-library')
  def search_no_library(self):
    odm_theme.set_in_library(False)
    return h.redirect_to(controller='package', action='search')
