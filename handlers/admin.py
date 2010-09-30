"""
admin.py:

Handler for admin

* Author:       Mitchell Bowden <mitchellbowden AT gmail DOT com>
* License:      MIT License: http://creativecommons.org/licenses/MIT/
"""

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template

import os

class AdminHandler(webapp.RequestHandler):
  def get(self):
    template_values = {}
    template_path = os.path.join(
      os.path.dirname(__file__), '..', 'templates', 'admin.html'
    )
    self.response.out.write(template.render(template_path, template_values))
