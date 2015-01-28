import ckan.plugins as p
import ckan.lib.helpers as h
from ckan.lib.base import BaseController

class ThemeController(BaseController):
  def library(self):
    return h.redirect_to(controller='organization', action='read', id='odm-library')
